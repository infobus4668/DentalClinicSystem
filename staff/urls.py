# dental_clinic/staff/urls.py

from django.urls import path
from . import views # Import views from the current app

app_name = 'staff' # Define the application namespace

urlpatterns = [
    # URL for listing all staff members (e.g., /staff/)
    path('', views.staff_list_view, name='staff_list'),
    # URL for adding a new staff member (e.g., /staff/add/)
    path('add/', views.add_staff_member_view, name='add_staff_member'),
    # URL for viewing a single staff member's details (e.g., /staff/1/)
    path('<int:staff_member_id>/', views.staff_detail_view, name='staff_detail'),
    # URL for editing an existing staff member (e.g., /staff/1/edit/)
    path('<int:staff_member_id>/edit/', views.edit_staff_member_view, name='edit_staff_member'),
    # URL for deleting an existing staff member (e.g., /staff/1/delete/)
    path('<int:staff_member_id>/delete/', views.delete_staff_member_view, name='delete_staff_member'),
]