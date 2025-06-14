# DENTALCLINICSYSTEM/billing/admin.py

from django.contrib import admin
from .models import (
    Service, Product, Invoice, InvoiceItem, 
    Supplier, StockItem, PurchaseOrder, PurchaseOrderItem, SupplierPayment,
    StockAdjustment, StockItemTransaction
)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'email')
    search_fields = ('name', 'contact_person')

class StockItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'batch_number', 'quantity_available', 'quantity', 'cost_price', 'date_received')
    list_filter = ('product', 'supplier', 'expiry_date')
    search_fields = ('product__name', 'batch_number', 'supplier__name')
    raw_id_fields = ('product', 'supplier')
    readonly_fields = ('quantity_sold', 'quantity_available')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'stock_quantity', 'price', 'is_active')
    list_filter = ('is_active', 'brand')
    search_fields = ('name', 'description', 'brand')
    list_editable = ('price', 'is_active')
    readonly_fields = ('stock_quantity',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('is_active',)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ('service', 'stock_item', 'description', 'quantity', 'unit_price', 'discount')
    raw_id_fields = ('service', 'stock_item',) 
    
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'doctor', 'invoice_date', 'status', 'net_amount', 'amount_paid', 'balance_due')
    list_filter = ('status', 'invoice_date', 'doctor')
    search_fields = ('invoice_number', 'patient__name', 'doctor__name')
    date_hierarchy = 'invoice_date'
    readonly_fields = ('total_amount', 'net_amount', 'balance_due', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline]

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    raw_id_fields = ('product',)

class SupplierPaymentInline(admin.TabularInline):
    model = SupplierPayment
    extra = 0

class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date', 'supplier')
    search_fields = ('id', 'supplier__name')
    readonly_fields = ('total_amount',)
    inlines = [PurchaseOrderItemInline, SupplierPaymentInline]

class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'adjustment_type', 'quantity', 'reason', 'adjustment_date', 'adjusted_by')
    list_filter = ('adjustment_date', 'reason', 'adjustment_type')
    raw_id_fields = ('product', 'adjusted_by')

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(StockItem, StockItemAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(StockAdjustment, StockAdjustmentAdmin)
admin.site.register(StockItemTransaction)