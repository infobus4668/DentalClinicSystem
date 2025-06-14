# DENTALCLINICSYSTEM/reporting/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from staff.decorators import role_required
from django.db.models import Sum, Q
from billing.models import Invoice, StockItem, SupplierPayment
from lab_cases.models import LabCase
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from .forms import ReportFilterForm

@login_required
@role_required(allowed_roles=['MANAGER'])
def report_index_view(request):
    context = {'page_title': 'Reports'}
    return render(request, 'reporting/report_index.html', context)

@login_required
@role_required(allowed_roles=['MANAGER'])
def financial_summary_report(request):
    # This view is unchanged
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    next_month = (start_of_month + timedelta(days=32)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)
    invoices_this_month = Invoice.objects.filter(
        invoice_date__gte=start_of_month, 
        invoice_date__lte=end_of_month
    ).exclude(status='CANCELLED')
    monthly_summary = invoices_this_month.aggregate(
        total_invoiced=Sum('total_amount'),
        total_paid=Sum('amount_paid')
    )
    total_invoiced_this_month = monthly_summary.get('total_invoiced') or Decimal('0.00')
    total_paid_this_month = monthly_summary.get('total_paid') or Decimal('0.00')
    total_outstanding_balance_all_time_agg = Invoice.objects.filter(
        Q(status='PENDING') | Q(status='PARTIAL')
    ).aggregate(
        total_due=Sum('total_amount'),
        total_paid=Sum('amount_paid')
    )
    total_due = total_outstanding_balance_all_time_agg.get('total_due') or Decimal('0.00')
    total_paid_overall = total_outstanding_balance_all_time_agg.get('total_paid') or Decimal('0.00')
    total_outstanding_balance = total_due - total_paid_overall
    context = {
        'page_title': 'Financial Summary Report',
        'report_month': start_of_month.strftime("%B %Y"),
        'total_invoiced_this_month': total_invoiced_this_month,
        'total_paid_this_month': total_paid_this_month,
        'total_outstanding_balance': total_outstanding_balance,
    }
    return render(request, 'reporting/financial_summary.html', context)

@login_required
@role_required(allowed_roles=['MANAGER', 'RECEP'])
def stock_received_report_view(request):
    # This view is unchanged
    form = ReportFilterForm(request.GET or None, hide_lab=True, hide_patient=True)
    stock_items = StockItem.objects.select_related('product', 'supplier').order_by('-date_received')
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        product = form.cleaned_data.get('product')
        supplier = form.cleaned_data.get('supplier')
        if start_date and end_date:
            stock_items = stock_items.filter(date_received__date__range=[start_date, end_date])
        if product:
            stock_items = stock_items.filter(product=product)
        if supplier:
            stock_items = stock_items.filter(supplier=supplier)
    context = {
        'form': form,
        'stock_items': stock_items,
        'page_title': 'Stock Received Report'
    }
    return render(request, 'reporting/stock_received_report.html', context)

@login_required
@role_required(allowed_roles=['MANAGER'])
def supplier_payment_report_view(request):
    # This view is unchanged
    form = ReportFilterForm(request.GET or None, hide_product=True, hide_lab=True, hide_patient=True)
    payments = SupplierPayment.objects.select_related('purchase_order__supplier').order_by('-payment_date')
    total_paid = 0
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        supplier = form.cleaned_data.get('supplier')
        if start_date and end_date:
            payments = payments.filter(payment_date__range=[start_date, end_date])
        if supplier:
            payments = payments.filter(purchase_order__supplier=supplier)
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    context = {
        'form': form,
        'payments': payments,
        'total_paid': total_paid,
        'page_title': 'Supplier Payment Report'
    }
    return render(request, 'reporting/supplier_payment_report.html', context)

# --- MODIFIED: Lab Cases Report View ---
@login_required
@role_required(allowed_roles=['MANAGER', 'RECEP'])
def lab_cases_report_view(request):
    # Use the form, hiding the fields we don't need for this report
    form = ReportFilterForm(request.GET or None, hide_supplier=True, hide_product=True)
    lab_cases = LabCase.objects.select_related('patient', 'doctor', 'lab').order_by('-date_sent')

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        lab = form.cleaned_data.get('lab')
        patient = form.cleaned_data.get('patient') # <-- Get the patient object

        if start_date and end_date:
            lab_cases = lab_cases.filter(date_sent__range=[start_date, end_date])
        if lab:
            lab_cases = lab_cases.filter(lab=lab)
        if patient: # <-- Filter by patient
            lab_cases = lab_cases.filter(patient=patient)
    
    context = {
        'form': form,
        'lab_cases': lab_cases,
        'page_title': 'Lab Cases Report'
    }
    return render(request, 'reporting/lab_cases_report.html', context)