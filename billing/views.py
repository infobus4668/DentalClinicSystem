# DENTALCLINICSYSTEM/billing/views.py

import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.db.models import F, Q, Sum
from django.contrib import messages
from django.forms import formset_factory

from .models import (
    Service, Product, Invoice, InvoiceItem, StockItem, Supplier,
    PurchaseOrder, PurchaseOrderItem, SupplierPayment, StockAdjustment,
    StockItemTransaction
)
from .forms import (
    ServiceForm, ProductForm, InvoiceForm, InvoiceItemFormSet,
    SupplierForm, PurchaseOrderForm, PurchaseOrderItemFormSet,
    SupplierPaymentForm, ReceiveStockFormSet, StockAdjustmentForm
)
from appointments.models import Appointment
from staff.decorators import role_required
from patients.models import Patient

BILLING_ROLES = ['MANAGER', 'RECEP', 'ASSIST', 'HYGIEN', 'OTHER']

def get_invoice_context_data():
    """Helper function to get common data for invoice forms."""
    products_with_batches = {}
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0).order_by('name')
    for p in products:
        available_batches = [
            {
                'id': batch.id,
                'name': f"Batch: {batch.batch_number or 'N/A'} | Avail: {batch.quantity_available} | Cost: {batch.cost_price}",
                'available': batch.quantity_available
            } 
            for batch in p.stock_items.all() if batch.quantity_available > 0
        ]
        if available_batches:
             products_with_batches[p.id] = available_batches
    
    js_data = {
        'services': {s.id: str(s.price) for s in Service.objects.filter(is_active=True)},
        'products': {p.id: {'price': str(p.price)} for p in products},
        'batches': products_with_batches
    }
    return js_data

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def create_invoice_view(request, appointment_id=None):
    initial_data = {}
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if hasattr(appointment, 'invoice'):
            messages.warning(request, f"An invoice already exists for this appointment.")
            return redirect('billing:invoice_detail', invoice_id=appointment.invoice.id)
        initial_data = {
            'patient': appointment.patient, 'doctor': appointment.doctor, 'appointment': appointment,
            'invoice_date': appointment.appointment_datetime.date(),
        }
    else:
        patient_id = request.GET.get('patient_id')
        if patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
                initial_data['patient'] = patient
            except Patient.DoesNotExist: pass

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, prefix='invoice')
        item_formset = InvoiceItemFormSet(request.POST, prefix='items')
        if invoice_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                invoice = invoice_form.save()
                items = item_formset.save(commit=False)
                for item in items:
                    item.invoice = invoice
                    item.save()
                messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
                return redirect('billing:invoice_detail', invoice_id=invoice.id)
        else:
             messages.error(request, "Please correct the errors below.")
    else:
        invoice_form = InvoiceForm(prefix='invoice', initial=initial_data)
        item_formset = InvoiceItemFormSet(prefix='items', queryset=InvoiceItem.objects.none())

    context = {
        'invoice_form': invoice_form, 
        'formset': item_formset, 
        'page_title': 'Create New Invoice',
        'js_data': json.dumps(get_invoice_context_data())
    }
    return render(request, 'billing/create_invoice.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def edit_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, instance=invoice, prefix='invoice')
        item_formset = InvoiceItemFormSet(request.POST, instance=invoice, prefix='items')
        if invoice_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                invoice_form.save()
                item_formset.save()
                messages.success(request, f'Invoice {invoice.invoice_number} updated successfully!')
                return redirect('billing:invoice_detail', invoice_id=invoice.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else: 
        invoice_form = InvoiceForm(instance=invoice, prefix='invoice')
        item_formset = InvoiceItemFormSet(instance=invoice, prefix='items')

    context = {
        'invoice_form': invoice_form,
        'formset': item_formset,
        'invoice': invoice,
        'page_title': f'Edit Invoice: {invoice.invoice_number}',
        'js_data': json.dumps(get_invoice_context_data())
    }
    return render(request, 'billing/edit_invoice.html', context)

@login_required
@role_required(allowed_roles=['MANAGER'])
def stock_adjustment_list_view(request):
    adjustments = StockAdjustment.objects.select_related('product', 'adjusted_by').all()
    context = { 'adjustments_list': adjustments, 'page_title': 'Stock Adjustment History' }
    return render(request, 'billing/stock_adjustment_list.html', context)

@login_required
@role_required(allowed_roles=['MANAGER'])
def create_stock_adjustment_view(request):
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.adjusted_by = request.user
            adjustment.save()
            messages.success(request, f'Stock for "{adjustment.product.name}" was adjusted successfully.')
            return redirect('billing:stock_adjustment_list')
    else:
        form = StockAdjustmentForm()
    context = { 'form': form, 'page_title': 'Create Manual Stock Adjustment' }
    return render(request, 'billing/stock_adjustment_form.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def purchase_order_list_view(request):
    purchase_orders = PurchaseOrder.objects.all().order_by('-order_date')
    context = { 'purchase_orders_list': purchase_orders, 'page_title': 'Supplier Purchase Orders' }
    return render(request, 'billing/purchase_order_list.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def purchase_order_create_view(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, prefix='main')
        formset = PurchaseOrderItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                purchase_order = form.save()
                items = formset.save(commit=False)
                for item in items:
                    item.purchase_order = purchase_order
                    item.save()
                purchase_order.update_total_amount()
                messages.success(request, 'Purchase Order created successfully.')
                return redirect('billing:purchase_order_detail', po_id=purchase_order.id)
        else: messages.error(request, "Please correct the errors below.")
    else:
        form = PurchaseOrderForm(prefix='main')
        formset = PurchaseOrderItemFormSet(prefix='items', queryset=PurchaseOrderItem.objects.none())
    context = { 'form': form, 'formset': formset, 'page_title': 'Create New Purchase Order' }
    return render(request, 'billing/purchase_order_form.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def purchase_order_detail_view(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder.objects.prefetch_related('items__product'), id=po_id)
    amount_paid = purchase_order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = purchase_order.total_amount - amount_paid
    items_to_receive = any(not item.is_fully_received for item in purchase_order.items.all())
    context = {
        'po': purchase_order, 'amount_paid': amount_paid, 'balance': balance,
        'items_to_receive': items_to_receive, 'page_title': f'Details for PO #{purchase_order.id}'
    }
    return render(request, 'billing/purchase_order_detail.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def purchase_order_edit_view(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
    if purchase_order.status != 'PENDING':
        messages.error(request, 'Cannot edit an order that has been partially or fully received.')
        return redirect('billing:purchase_order_detail', po_id=po_id)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=purchase_order, prefix='main')
        formset = PurchaseOrderItemFormSet(request.POST, instance=purchase_order, prefix='items')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                purchase_order.update_total_amount()
                messages.success(request, 'Purchase Order updated successfully.')
                return redirect('billing:purchase_order_detail', po_id=purchase_order.id)
        else: messages.error(request, "Please correct the errors below.")
    else:
        form = PurchaseOrderForm(instance=purchase_order, prefix='main')
        formset = PurchaseOrderItemFormSet(instance=purchase_order, prefix='items')
    context = { 'form': form, 'formset': formset, 'po': purchase_order, 'page_title': f'Edit Purchase Order #{purchase_order.id}'}
    return render(request, 'billing/purchase_order_form.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def receive_purchase_order_view(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder.objects.prefetch_related('items__product'), id=po_id)
    items_to_receive = purchase_order.items.filter(quantity_received__lt=F('quantity'))
    if not items_to_receive.exists():
        messages.warning(request, "This purchase order has already been fully received.")
        return redirect('billing:purchase_order_detail', po_id=po_id)
    if request.method == 'POST':
        formset = ReceiveStockFormSet(request.POST, prefix='receive')
        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    po_item_id = form.cleaned_data.get('purchase_order_item_id')
                    quantity_now = form.cleaned_data.get('quantity_to_receive', 0)
                    if not po_item_id or not isinstance(quantity_now, int) or quantity_now <= 0: continue
                    po_item = get_object_or_404(PurchaseOrderItem, id=po_item_id)
                    StockItem.objects.create(
                        product=po_item.product, supplier=purchase_order.supplier,
                        purchase_order_item=po_item, quantity=quantity_now,
                        cost_price=po_item.cost_price, batch_number=form.cleaned_data.get('batch_number'),
                        expiry_date=form.cleaned_data.get('expiry_date')
                    )
                    po_item.quantity_received = F('quantity_received') + quantity_now
                    po_item.save()
            purchase_order.update_status()
            messages.success(request, "Stock received and inventory updated successfully.")
            return redirect('billing:purchase_order_detail', po_id=purchase_order.id)
    else:
        initial_data = [{'purchase_order_item_id': item.id} for item in items_to_receive]
        formset = ReceiveStockFormSet(initial=initial_data, prefix='receive')
    forms_with_items = zip(formset, items_to_receive)
    context = {
        'purchase_order': purchase_order, 'formset': formset, 'forms_with_items': forms_with_items,
        'page_title': f'Receive Stock for PO #{purchase_order.id}'
    }
    return render(request, 'billing/receive_purchase_order.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def add_supplier_payment_view(request, po_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
    if request.method == 'POST':
        form = SupplierPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.purchase_order = purchase_order
            payment.save()
            messages.success(request, f'Payment of ₹{payment.amount} recorded successfully.')
            return redirect('billing:purchase_order_detail', po_id=purchase_order.id)
    else: form = SupplierPaymentForm()
    context = { 'form': form, 'purchase_order': purchase_order, 'page_title': f'Add Payment for PO #{purchase_order.id}'}
    return render(request, 'billing/add_supplier_payment.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def supplier_list_view(request):
    suppliers = Supplier.objects.all().order_by('name')
    context = {'suppliers_list': suppliers, 'page_title': 'Product Suppliers'}
    return render(request, 'billing/supplier_list.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def add_supplier_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('billing:supplier_list')
    else: form = SupplierForm()
    context = {'form': form, 'page_title': 'Add New Supplier'}
    return render(request, 'billing/add_supplier.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def edit_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('billing:supplier_list')
    else: form = SupplierForm(instance=supplier)
    context = {'form': form, 'supplier': supplier, 'page_title': f'Edit Supplier: {supplier.name}'}
    return render(request, 'billing/edit_supplier.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def delete_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!')
        return redirect('billing:supplier_list')
    context = {'supplier': supplier, 'page_title': f'Confirm Delete: {supplier.name}'}
    return render(request, 'billing/supplier_confirm_delete.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def service_list_view(request):
    services = Service.objects.all().order_by('name')
    context = {'services_list': services, 'page_title': 'Clinic Services'}
    return render(request, 'billing/service_list.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def add_service_view(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added successfully!')
            return redirect('billing:service_list')
    else: form = ServiceForm()
    context = {'form': form, 'page_title': 'Add New Service'}
    return render(request, 'billing/add_service.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('billing:service_list')
    else: form = ServiceForm(instance=service)
    context = {'form': form, 'service': service, 'page_title': f'Edit Service: {service.name}'}
    return render(request, 'billing/edit_service.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('billing:service_list')
    context = {'service': service, 'page_title': f'Confirm Delete: {service.name}'}
    return render(request, 'billing/service_confirm_delete.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def product_list_view(request):
    products = Product.objects.all().order_by('name')
    context = {'products_list': products, 'page_title': 'Products & Inventory'}
    return render(request, 'billing/product_list.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('billing:product_list')
    else: form = ProductForm()
    context = {'form': form, 'page_title': 'Add New Product'}
    return render(request, 'billing/add_product.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('billing:product_list')
    else: form = ProductForm(instance=product)
    context = {'form': form, 'product': product, 'page_title': f'Edit Product: {product.name}'}
    return render(request, 'billing/edit_product.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('billing:product_list')
    context = {'product': product, 'page_title': f'Confirm Delete: {product.name}'}
    return render(request, 'billing/product_confirm_delete.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def invoice_list_view(request):
    invoices = Invoice.objects.select_related('patient', 'doctor').all()
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in [choice[0] for choice in Invoice.STATUS_CHOICES]:
        invoices = invoices.filter(status=status_filter)
    if search_query:
        invoices = invoices.filter(Q(invoice_number__icontains=search_query) | Q(patient__name__icontains=search_query))
    context = {
        'invoices_list': invoices, 'page_title': 'Patient Invoices', 'search_query': search_query,
        'status_filter': status_filter, 'status_choices': Invoice.STATUS_CHOICES,
    }
    return render(request, 'billing/invoice_list.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_items = invoice.invoice_items.all()
    context = {'invoice': invoice, 'invoice_items': invoice_items, 'page_title': f'Invoice: {invoice.invoice_number}'}
    return render(request, 'billing/invoice_detail.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def delete_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, f'Invoice {invoice.invoice_number} deleted successfully!')
        return redirect('billing:invoice_list')
    context = {'invoice': invoice, 'page_title': f'Confirm Delete: {invoice.invoice_number}'}
    return render(request, 'billing/invoice_confirm_delete.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def invoice_print_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_items = invoice.invoice_items.all()
    context = {
        'invoice': invoice, 'invoice_items': invoice_items,
        'page_title': f'Print Invoice: {invoice.invoice_number}'
    }
    return render(request, 'billing/invoice_print.html', context)

@login_required
@role_required(allowed_roles=BILLING_ROLES)
def low_stock_report_view(request):
    low_stock_products = Product.objects.filter(is_active=True, stock_quantity__lte=F('low_stock_threshold')).order_by('stock_quantity')
    context = {'low_stock_products': low_stock_products, 'page_title': 'Low Stock Report'}
    return render(request, 'billing/low_stock_report.html', context)