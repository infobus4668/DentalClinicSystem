# DENTALCLINICSYSTEM/billing/signals.py

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import (
    Invoice, InvoiceItem, Product, StockAdjustment, StockItem, 
    StockItemTransaction
)

@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def on_invoice_item_change_update_invoice_total(sender, instance, **kwargs):
    """When an invoice's items change, recalculate its total."""
    invoice = instance.invoice
    total = invoice.invoice_items.aggregate(
        total=models.Sum(models.F('quantity') * models.F('unit_price'))
    )['total'] or 0
    
    if invoice.total_amount != total:
        Invoice.objects.filter(pk=invoice.pk).update(total_amount=total)


@transaction.atomic
def process_batch_sale(invoice_item):
    """
    This function processes a sale from a specific batch.
    It creates a transaction record to link the sale to the stock item.
    """
    # This check is crucial for items that are services, not products
    if not invoice_item.stock_item:
        return
    
    # Clear any previous transactions for this item to handle updates correctly
    invoice_item.stock_transactions.all().delete()

    # Create the new transaction linking the sale to the specific batch
    StockItemTransaction.objects.create(
        invoice_item=invoice_item,
        stock_item=invoice_item.stock_item,
        quantity=invoice_item.quantity
    )
    
@receiver(post_save, sender=InvoiceItem)
def on_invoice_item_save(sender, instance, **kwargs):
    """When an invoice item is saved, process the stock change."""
    process_batch_sale(instance)
    # After processing the sale, trigger a recount of the product's total stock
    if instance.stock_item:
        instance.stock_item.product.update_stock_quantity()

@receiver(post_delete, sender=InvoiceItem)
def on_invoice_item_delete(sender, instance, **kwargs):
    """When an invoice item is deleted, just trigger a stock update."""
    # The CASCADE on the relationship from StockItemTransaction to InvoiceItem
    # handles deleting the transaction. We just need to trigger the recount.
    if instance.stock_item:
        instance.stock_item.product.update_stock_quantity()


# --- Centralized handler for all other stock changes ---

@receiver(post_save, sender=StockAdjustment)
@receiver(post_delete, sender=StockAdjustment)
def on_adjustment_change(sender, instance, **kwargs):
    """When a stock adjustment is made or deleted, update the product's stock."""
    instance.product.update_stock_quantity()

@receiver(post_save, sender=StockItem)
@receiver(post_delete, sender=StockItem)
def on_stock_item_change(sender, instance, **kwargs):
    """When stock is received or a batch is deleted, update the product's stock."""
    instance.product.update_stock_quantity()