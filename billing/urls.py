# DENTALCLINICSYSTEM/billing/urls.py

from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Suppliers
    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/add/', views.add_supplier_view, name='add_supplier'),
    path('suppliers/<int:supplier_id>/edit/', views.edit_supplier_view, name='edit_supplier'),
    path('suppliers/<int:supplier_id>/delete/', views.delete_supplier_view, name='delete_supplier'),

    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list_view, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create_view, name='purchase_order_create'),
    path('purchase-orders/<int:po_id>/', views.purchase_order_detail_view, name='purchase_order_detail'),
    path('purchase-orders/<int:po_id>/edit/', views.purchase_order_edit_view, name='purchase_order_edit'),
    path('purchase-orders/<int:po_id>/add-payment/', views.add_supplier_payment_view, name='add_supplier_payment'),
    path('purchase-orders/<int:po_id>/receive/', views.receive_purchase_order_view, name='receive_purchase_order'),
    
    # Services
    path('services/', views.service_list_view, name='service_list'),
    path('services/add/', views.add_service_view, name='add_service'),
    path('services/<int:service_id>/edit/', views.edit_service_view, name='edit_service'),
    path('services/<int:service_id>/delete/', views.delete_service_view, name='delete_service'),
    
    # Products
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),
    
    # Invoices
    path('invoices/', views.invoice_list_view, name='invoice_list'),
    path('invoices/create/', views.create_invoice_view, name='create_invoice'),
    path('invoices/create/from-appointment/<int:appointment_id>/', views.create_invoice_view, name='create_invoice_from_appointment'),
    path('invoices/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.edit_invoice_view, name='edit_invoice'),
    path('invoices/<int:invoice_id>/delete/', views.delete_invoice_view, name='delete_invoice'),
    path('invoices/<int:invoice_id>/print/', views.invoice_print_view, name='invoice_print'),

    # Inventory Reports and Adjustments
    path('reports/low-stock/', views.low_stock_report_view, name='low_stock_report'),
    path('adjustments/', views.stock_adjustment_list_view, name='stock_adjustment_list'),
    path('adjustments/create/', views.create_stock_adjustment_view, name='create_stock_adjustment'),
]