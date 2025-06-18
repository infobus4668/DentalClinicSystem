# DENTALCLINICSYSTEM/lab_cases/urls.py

from django.urls import path
from . import views # Import views from the current app

app_name = 'lab_cases' # Define the application namespace

urlpatterns = [
    # --- Dental Lab URLs ---
    # URL for listing all dental labs (e.g., /lab-cases/labs/)
    path('labs/', views.lab_list_view, name='lab_list'),
    path('labs/add/', views.add_lab_view, name='add_lab'),
    path('labs/<int:lab_id>/edit/', views.edit_lab_view, name='edit_lab'),
    path('labs/<int:lab_id>/delete/', views.delete_lab_view, name='delete_lab'),
    path('cases/', views.lab_case_list_view, name='lab_case_list'),
    path('cases/add/', views.add_lab_case_view, name='add_lab_case'),
    path('cases/<int:case_id>/', views.lab_case_detail_view, name='lab_case_detail'),
    path('cases/<int:case_id>/edit/', views.edit_lab_case_view, name='edit_lab_case'),
    path('cases/<int:case_id>/delete/', views.delete_lab_case_view, name='delete_lab_case'),
]