from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list_view, name='patient_list'),
    path('add/', views.add_patient_view, name='add_patient'),
    path('<int:patient_id>/', views.patient_detail_view, name='patient_detail'),
    path('<int:patient_id>/edit/', views.edit_patient_view, name='edit_patient'),
    # Path for deleting an existing patient (NEW)
    path('<int:patient_id>/delete/', views.delete_patient_view, name='delete_patient'),
]