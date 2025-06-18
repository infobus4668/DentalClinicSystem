# DENTALCLINICSYSTEM/billing/models.py

from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from decimal import Decimal
from django.core.validators import MinValueValidator

class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    class Meta: verbose_name = "Supplier"; verbose_name_plural = "Suppliers"; ordering = ['name']
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the product (e.g., 'Fluoride Toothpaste').")
    brand = models.CharField(max_length=100, blank=True, null=True)
    content = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., '100g', '50ml'")
    low_stock_threshold = models.PositiveIntegerField(default=10, help_text="Set a threshold for low stock alerts.")
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price for this product (MRP).")
    stock_quantity = models.IntegerField(default=0, editable=False, help_text="Total current quantity from all batches.")
    is_active = models.BooleanField(default=True, help_text="Is this product currently available for sale?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Product"; verbose_name_plural = "Products"; ordering = ['name']
    
    def update_stock_quantity(self):
        total_received = self.stock_items.aggregate(total=Sum('quantity'))['total'] or 0
        total_sold = StockItemTransaction.objects.filter(stock_item__product=self).aggregate(total=Sum('quantity'))['total'] or 0
        adjustments = self.adjustments.all()
        total_added = adjustments.filter(adjustment_type='ADDITION').aggregate(total=Sum('quantity'))['total'] or 0
        total_subtracted = adjustments.filter(adjustment_type='SUBTRACTION').aggregate(total=Sum('quantity'))['total'] or 0
        final_stock = (total_received + total_added) - (total_sold + total_subtracted)
        if self.stock_quantity != final_stock:
            # CORRECTED: Update the instance directly and call self.save()
            self.stock_quantity = final_stock
            self.save(update_fields=['stock_quantity'])

    def __str__(self):
        return f"{self.name} ({self.brand or 'N/A'}) - Stock: {self.stock_quantity}"

class StockItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_items')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_items')
    purchase_order_item = models.ForeignKey('PurchaseOrderItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='received_batches')
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(help_text="The total quantity received in this batch.")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price paid to the supplier for one unit.")
    date_received = models.DateTimeField(default=timezone.now)
    
    @property
    def quantity_sold(self):
        return self.transactions.aggregate(total=Sum('quantity'))['total'] or 0
    @property
    def quantity_available(self):
        return self.quantity - self.quantity_sold

    class Meta: verbose_name = "Stock Item / Batch"; verbose_name_plural = "Stock Items / Batches"; ordering = ['date_received']
    def __str__(self): return f"Batch: {self.batch_number or 'N/A'} ({self.product.name}) - Avail: {self.quantity_available}"

class StockAdjustment(models.Model):
    ADJUSTMENT_TYPE_CHOICES = [('ADDITION', 'Manual Addition'), ('SUBTRACTION', 'Manual Subtraction'),]
    REASON_CHOICES = [('DAMAGED', 'Damaged Goods'), ('EXPIRED', 'Expired Stock'), ('STOCK_TAKE', 'Stock Take Correction'), ('INITIAL_STOCK', 'Initial Stock Setup'), ('OTHER', 'Other'),]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='adjustments')
    adjustment_type = models.CharField(max_length=11, choices=ADJUSTMENT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(blank=True, help_text="Provide details, especially if reason is 'Other'.")
    adjustment_date = models.DateTimeField(default=timezone.now)
    adjusted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_adjustments')
    def __str__(self): return f"{self.get_adjustment_type_display()} of {self.quantity} for {self.product.name} on {self.adjustment_date.date()}"
    class Meta: ordering = ['-adjustment_date']

class Service(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the dental service (e.g., 'Routine Check-up', 'Composite Filling').")
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Standard price for this service.")
    is_active = models.BooleanField(default=True, help_text="Is this service currently offered?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Service"; verbose_name_plural = "Services"; ordering = ['name']
    def __str__(self): return f"{self.name} (₹{self.price:.2f})"

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='invoices')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, null=True, blank=True, related_name='invoices')
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice', help_text="Optional: Link to the specific appointment this invoice is for.")
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = [('PENDING', 'Pending'), ('PAID', 'Paid'), ('PARTIAL', 'Partial Payment'), ('CANCELLED', 'Cancelled')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Subtotal of all items before discount")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Overall discount on the entire invoice")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Invoice"; verbose_name_plural = "Invoices"; ordering = ['-invoice_date', '-created_at']
    def __str__(self): return f"Invoice {self.invoice_number} for {self.patient.name} ({self.get_status_display()})"
    @property
    def total_discount(self):
        items_discount = self.invoice_items.aggregate(total=Sum('discount'))['total'] or Decimal('0.00')
        return self.discount + items_discount
    @property
    def net_amount(self): return self.total_amount - self.total_discount
    @property
    def balance_due(self): return self.net_amount - self.amount_paid
    def _generate_invoice_number(self):
        today_str = timezone.now().strftime('%y%m%d'); prefix = f'INV-{today_str}-'; last_invoice = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('invoice_number').last(); new_seq = 1
        if last_invoice:
            try:
                last_seq_str = last_invoice.invoice_number[len(prefix):]
                if last_seq_str.isdigit(): new_seq = int(last_seq_str) + 1
            except (ValueError, IndexError): pass
        return f'{prefix}{str(new_seq).zfill(4)}'
    def save(self, *args, **kwargs):
        if not self.pk: self.invoice_number = self._generate_invoice_number()
        super().save(*args, **kwargs)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, null=True, blank=True, related_name='invoice_items')
    description = models.CharField(max_length=255, blank=True, default='', help_text="Custom description or auto-filled from service/product.")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Discount for this specific item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Invoice Item"; verbose_name_plural = "Invoice Items"
    def save(self, *args, **kwargs):
        if self.stock_item and not self.description:
            self.description = f"{self.stock_item.product.name} (Batch: {self.stock_item.batch_number or 'N/A'})"
            self.unit_price = self.stock_item.product.price
        elif self.service and not self.description:
            self.description = self.service.name
            self.unit_price = self.service.price
        super().save(*args, **kwargs)
    @property
    def total_price(self): return (self.quantity or 0) * (self.unit_price or Decimal('0.00'))
    @property
    def net_price(self): return self.total_price - (self.discount or Decimal('0.00'))
    def __str__(self): return f"{self.quantity} x {self.description} on Invoice {self.invoice.invoice_number}"

class StockItemTransaction(models.Model):
    invoice_item = models.ForeignKey(InvoiceItem, on_delete=models.CASCADE, related_name="stock_transactions")
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name="transactions")
    quantity = models.PositiveIntegerField()
    def __str__(self): return f"{self.quantity} units from {self.stock_item} for {self.invoice_item}"

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    order_date = models.DateField(default=timezone.now)
    STATUS_CHOICES = [('PENDING', 'Pending'), ('PARTIALLY_RECEIVED', 'Partially Received'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Total cost of the order.")
    notes = models.TextField(blank=True, null=True)
    def update_total_amount(self):
        self.total_amount = self.items.aggregate(total=Sum(F('quantity') * F('cost_price')))['total'] or Decimal('0.00')
        self.save(update_fields=['total_amount'])
    def update_status(self):
        total_ordered = self.items.aggregate(total=Sum('quantity'))['total'] or 0
        total_received = self.items.aggregate(total=Sum('quantity_received'))['total'] or 0
        if total_received == 0: self.status = 'PENDING'
        elif total_received < total_ordered: self.status = 'PARTIALLY_RECEIVED'
        else: self.status = 'COMPLETED'
        self.save(update_fields=['status'])
    def __str__(self): return f"PO #{self.id} for {self.supplier.name} on {self.order_date}"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_items')
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per unit for this specific purchase.")
    quantity_received = models.PositiveIntegerField(default=0)
    @property
    def is_fully_received(self): return self.quantity_received >= self.quantity
    @property
    def quantity_remaining(self): return self.quantity - self.quantity_received
    def __str__(self): return f"{self.quantity} x {self.product.name} for PO #{self.purchase_order.id}"

class SupplierPayment(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    PAYMENT_METHODS = [('CASH', 'Cash'), ('BANK', 'Bank Transfer'), ('CHEQUE', 'Cheque')]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='BANK')
    notes = models.TextField(blank=True, null=True)
    def __str__(self): return f"Payment of ₹{self.amount} for PO {self.purchase_order.id}"