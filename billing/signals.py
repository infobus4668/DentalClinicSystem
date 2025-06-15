from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum, F
from .models import (
    InvoiceItem, Invoice, Product, StockAdjustment, StockItem, 
    StockItemTransaction
)

@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def on_invoice_item_change_update_invoice_total(sender, instance, **kwargs):
    invoice = instance.invoice
    total = invoice.invoice_items.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0

    if invoice.total_amount != total:
        Invoice.objects.filter(pk=invoice.pk).update(total_amount=total)


@transaction.atomic
def process_batch_sale(invoice_item):
    if not invoice_item.stock_item:
        return
    
    # Remove previous stock transactions for this item (to handle edits)
    invoice_item.stock_transactions.all().delete()

    # Create new stock transaction linking the sale to the batch
    StockItemTransaction.objects.create(
        invoice_item=invoice_item,
        stock_item=invoice_item.stock_item,
        quantity=invoice_item.quantity
    )

@receiver(post_save, sender=InvoiceItem)
def on_invoice_item_save(sender, instance, **kwargs):
    process_batch_sale(instance)
    if instance.stock_item:
        instance.stock_item.product.update_stock_quantity()

@receiver(post_delete, sender=InvoiceItem)
def on_invoice_item_delete(sender, instance, **kwargs):
    if instance.stock_item:
        instance.stock_item.product.update_stock_quantity()


@receiver(post_save, sender=StockAdjustment)
@receiver(post_delete, sender=StockAdjustment)
def on_adjustment_change(sender, instance, **kwargs):
    instance.product.update_stock_quantity()

@receiver(post_save, sender=StockItem)
@receiver(post_delete, sender=StockItem)
def on_stock_item_change(sender, instance, **kwargs):
    instance.product.update_stock_quantity()