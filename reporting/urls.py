# DENTALCLINICSYSTEM/reporting/urls.py
from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.report_index_view, name='report_index'),
    path('financial-summary/', views.financial_summary_report, name='financial_summary'),
    path('stock-received/', views.stock_received_report_view, name='stock_received_report'),
    path('supplier-payments/', views.supplier_payment_report_view, name='supplier_payment_report'),
    # NEW: URL for the Lab Cases report
    path('lab-cases/', views.lab_cases_report_view, name='lab_cases_report'),
]