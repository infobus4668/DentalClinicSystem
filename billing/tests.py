# DENTALCLINICSYSTEM/billing/tests.py

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
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.patient = Patient.objects.create(name="Test Patient", date_of_birth="1995-01-01", gender='M')
        self.doctor = Doctor.objects.create(name="Dr. Test", specialization="General")
        self.product = Product.objects.create(name="Test Batch Product", price=100)
        self.batch1 = StockItem.objects.create(product=self.product, quantity=10, cost_price=50, batch_number="A1", date_received=timezone.now() - timezone.timedelta(days=10))
        self.batch2 = StockItem.objects.create(product=self.product, quantity=20, cost_price=55, batch_number="B2", date_received=timezone.now())
        self.product.refresh_from_db()

    def test_sell_from_specific_batch(self):
        self.assertEqual(self.product.stock_quantity, 30)
        invoice = Invoice.objects.create(patient=self.patient, doctor=self.doctor)
        InvoiceItem.objects.create(
            invoice=invoice, stock_item=self.batch2, quantity=5, unit_price=100
        )
        self.product.refresh_from_db()
        self.batch1.refresh_from_db()
        self.batch2.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 25)
        self.assertEqual(self.batch1.quantity_available, 10)
        self.assertEqual(self.batch2.quantity_available, 15)
        self.assertTrue(StockItemTransaction.objects.filter(invoice_item__invoice=invoice, stock_item=self.batch2, quantity=5).exists())

    def test_formset_validation_insufficient_stock_in_batch(self):
        invoice = Invoice.objects.create(patient=self.patient, doctor=self.doctor)
        
        # CORRECTED: Provide all required fields for the form to be valid
        form_data = {
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-0-product': self.product.id, # The product category selector
            'items-0-stock_item': self.batch1.id,
            'items-0-quantity': '11', # Try to sell 11, which is more than available
            'items-0-unit_price': '100.00',
            'items-0-discount': '0' # Added missing discount
        }
        
        formset = InvoiceItemFormSet(form_data, instance=invoice, prefix='items')
        
        self.assertFalse(formset.is_valid())
        self.assertIn('quantity', formset.errors[0])
        self.assertIn('Only 10 available', formset.errors[0]['quantity'][0])