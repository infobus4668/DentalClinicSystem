from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from staff.models import StaffMember

from .models import (
    Invoice, InvoiceItem, Service, Product, Supplier, PurchaseOrder, 
    PurchaseOrderItem, StockItem, StockAdjustment, StockItemTransaction
)
from .forms import InvoiceItemFormSet
from patients.models import Patient
from doctors.models import Doctor


class BatchAwareSellingTests(TestCase):
    def setUp(self):
        # Create a user and login
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        # Create test patient and doctor
        self.patient = Patient.objects.create(name="Test Patient", date_of_birth="1995-01-01", gender='M')
        self.doctor = Doctor.objects.create(name="Dr. Test", specialization="General")
        
        # Create product
        self.product = Product.objects.create(name="Test Batch Product", price=100)
        
        # Create stock batches
        self.batch1 = StockItem.objects.create(
            product=self.product, quantity=10, cost_price=50, 
            batch_number="A1", date_received=timezone.now() - timezone.timedelta(days=10)
        )
        self.batch2 = StockItem.objects.create(
            product=self.product, quantity=20, cost_price=55, 
            batch_number="B2", date_received=timezone.now()
        )
        # Refresh product stock_quantity
        self.product.update_stock_quantity()
        self.product.refresh_from_db()

    def test_sell_from_specific_batch(self):
        # Initial stock quantity
        self.assertEqual(self.product.stock_quantity, 30)
        
        # Create an invoice
        invoice = Invoice.objects.create(patient=self.patient, doctor=self.doctor)
        
        # Create invoice item selling 5 items from batch2
        invoice_item = InvoiceItem.objects.create(
            invoice=invoice, stock_item=self.batch2, quantity=5, unit_price=100
        )
        
        # Refresh quantities to reflect transactions/signals
        self.product.refresh_from_db()
        self.batch1.refresh_from_db()
        self.batch2.refresh_from_db()
        
        # Check updated stock quantity on product and batches
        self.assertEqual(self.product.stock_quantity, 25)  # 30 - 5 sold
        self.assertEqual(self.batch1.quantity_available, 10)  # untouched batch
        self.assertEqual(self.batch2.quantity_available, 15)  # 20 - 5 sold
        
        # Confirm StockItemTransaction is recorded correctly
        self.assertTrue(
            StockItemTransaction.objects.filter(
                invoice_item=invoice_item,
                stock_item=self.batch2,
                quantity=5
            ).exists()
        )

    def test_formset_validation_insufficient_stock_in_batch(self):
        invoice = Invoice.objects.create(patient=self.patient, doctor=self.doctor)
        
        # Create a blank service so the form doesn't complain about missing service (if needed)
        # Since either service or stock_item is required, provide service=None
        # But if you want, create a service like below
        # service = Service.objects.create(name="Consultation", price=200, is_active=True)
        
        form_data = {
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-service': '',  # No service selected
            'items-0-product': str(self.product.pk),  # Changed from self.product.id
            'items-0-stock_item': str(self.batch1.pk), # Changed from self.batch1.id
            'items-0-description': 'Test product sale',
            'items-0-quantity': '11',  # Above batch1 quantity_available which is 10
            'items-0-unit_price': '100.00',
            'items-0-discount': '0',
            'items-0-DELETE': '',  # Make sure formset delete flag is included (blank means not deleted)
        }
        
        formset = InvoiceItemFormSet(form_data, instance=invoice, prefix='items')
        
        self.assertFalse(formset.is_valid())
        # Check the error on quantity field contains "Only 10 available"
        self.assertIn('quantity', formset.errors[0])
        self.assertIn('Only 10 available', formset.errors[0]['quantity'][0])