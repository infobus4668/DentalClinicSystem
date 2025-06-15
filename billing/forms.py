from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet, formset_factory
from .models import (
    Service, Product, Invoice, InvoiceItem, 
    Supplier, StockItem, PurchaseOrder, PurchaseOrderItem, SupplierPayment,
    StockAdjustment
)
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from decimal import Decimal

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone_number', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier or Company Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'supplier@example.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Full address of the supplier...'}),
        }

class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = ['payment_date', 'amount', 'payment_method', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'e.g., Paid via GPay, Ref #123'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Detailed description of the service...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {'is_active': 'Service Available?'}

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'content', 'description', 'price', 'low_stock_threshold', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'content': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "e.g., '100g' or '50ml'"}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Detailed description of the product...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'price': 'Selling Price (MRP)',
            'is_active': 'Product Available for Sale?'
        }

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['product', 'adjustment_type', 'quantity', 'reason', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control select2-enable'}),
            'adjustment_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        adjustment_type = self.cleaned_data.get('adjustment_type')
        product = self.cleaned_data.get('product')

        if adjustment_type == 'SUBTRACTION' and product:
            stock_qty = getattr(product, 'stock_quantity', None)
            if stock_qty is None:
                stock_qty = product.stockitem_set.aggregate(total_qty=models.Sum('quantity_available'))['total_qty'] or 0
            if quantity > stock_qty:
                raise forms.ValidationError(
                    f"Cannot subtract {quantity} items. Only {stock_qty} are available."
                )
        return quantity

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control select2-enable'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Any notes for this purchase order...'}),
        }

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'cost_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control purchase-item-product select2-enable'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    fields=['product', 'quantity', 'cost_price'],
    extra=1,
    can_delete=True
)

class ReceiveStockForm(forms.Form):
    purchase_order_item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity_to_receive = forms.IntegerField(
        min_value=0,
        label="Receive Now",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
    )
    batch_number = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    expiry_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

ReceiveStockFormSet = formset_factory(ReceiveStockForm, extra=0)

class InvoiceForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    appointment = forms.ModelChoiceField(
        queryset=Appointment.objects.all().order_by('-appointment_datetime'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2-enable'}),
        help_text="Optional: Link this invoice to a specific appointment."
    )
    class Meta:
        model = Invoice
        fields = ['patient', 'doctor', 'appointment', 'invoice_date', 'due_date', 'status', 'discount', 'amount_paid', 'notes']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Internal notes about the invoice...'}),
        }

class InvoiceItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True, stock_quantity__gt=0),
        required=False,
        label="Product Category",
        widget=forms.Select(attrs={'class': 'form-control item-product select2-enable'})
    )

    class Meta:
        model = InvoiceItem
        fields = ['service', 'product', 'stock_item', 'description', 'quantity', 'unit_price', 'discount']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control item-service select2-enable'}),
            'stock_item': forms.Select(attrs={'class': 'form-control item-stock-batch select2-enable'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }
        labels = {
            'stock_item': 'Product Batch'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        stock_item_field = self.fields['stock_item']
        stock_item_field.queryset = StockItem.objects.none()

        if self.is_bound:
            product_key = f"{self.prefix}-product" if self.prefix else "product"
            try:
                product_id = int(self.data.get(product_key))
                stock_item_field.queryset = StockItem.objects.filter(product_id=product_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.stock_item:
            self.fields['product'].initial = self.instance.stock_item.product
            stock_item_field.queryset = StockItem.objects.filter(product=self.instance.stock_item.product)

    def is_empty(self):
        if self.instance.pk:
            return False

        data = self.data if self.is_bound else self.initial

        check_fields = [
            'service', 'product', 'stock_item', 'description', 
            'quantity', 'unit_price', 'discount'
        ]

        for field_name in check_fields:
            field_key = self.prefix + '-' + field_name if self.is_bound else field_name
            value = data.get(field_key)

            if field_name in ['quantity', 'unit_price', 'discount']:
                try:
                    if value is not None and value != '' and Decimal(value) != Decimal('0'):
                        return False
                except Exception:
                    return False
            elif value not in [None, '']:
                return False
        
        return True

    def has_changed(self):
        if super().has_changed():
            return True
        if not self.instance.pk and self.is_empty():
            return False
        return False


class BaseInvoiceItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        forms_to_validate = [
            form for form in self.forms
            if not form.cleaned_data.get('DELETE', False)
            and not form.is_empty()
            and not form.errors
        ]

        for form in forms_to_validate:
            service = form.cleaned_data.get('service')
            stock_item = form.cleaned_data.get('stock_item')
            quantity = form.cleaned_data.get('quantity')

            if not service and not stock_item:
                form.add_error(None, "Each line item must have either a service or a product batch selected.")

            if stock_item and quantity is not None:
                initial_quantity = form.instance.quantity if form.instance and form.instance.pk else 0
                available_qty = stock_item.quantity_available + initial_quantity
                if quantity > available_qty:
                    form.add_error(
                        'quantity', 
                        f"Not enough stock in Batch: {stock_item.batch_number or 'N/A'}. Only {available_qty} available."
                    )

InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    formset=BaseInvoiceItemFormSet,
    fields=['service', 'product', 'stock_item', 'description', 'quantity', 'unit_price', 'discount'],
    extra=1,
    can_delete=True
)