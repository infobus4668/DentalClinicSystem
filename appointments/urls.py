# appointments/urls.py

from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # API endpoint for the calendar
    path('api/all/', views.appointment_api_view, name='appointment_api'),

    # Regular appointment views
    path('', views.appointment_list_view, name='appointment_list'),
    path('schedule/', views.schedule_appointment_view, name='schedule_appointment'),
    path('<int:appointment_id>/', views.appointment_detail_view, name='appointment_detail'),
    path('<int:appointment_id>/edit/', views.edit_appointment_view, name='edit_appointment'),
    path('<int:appointment_id>/delete/', views.delete_appointment_view, name='delete_appointment'),

    # Existing print summary
    path('<int:appointment_id>/print-summary/', views.print_summary_view, name='print_summary'),
    
    # NEW: URL for the comprehensive bill summary
    path('<int:appointment_id>/print-bill-summary/', views.print_bill_summary_view, name='print_bill_summary'),
]