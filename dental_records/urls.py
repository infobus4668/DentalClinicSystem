# DENTALCLINICSYSTEM/dental_records/urls.py

from django.urls import path
from . import views

app_name = 'dental_records'

urlpatterns = [
    # URL for adding or editing the main Dental Record (notes, treatments)
    path('appointment/<int:appointment_id>/manage-record/', views.manage_dental_record_view, name='manage_dental_record'),

    # URL for adding or editing a Prescription and its items for a specific appointment
    path('appointment/<int:appointment_id>/manage-prescription/', views.manage_prescription_view, name='manage_prescription'),

    # NEW: URL for printing a standalone prescription
    path('prescription/<int:prescription_id>/print/', views.prescription_print_view, name='prescription_print'),
]