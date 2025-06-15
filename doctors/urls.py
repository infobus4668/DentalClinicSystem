from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list_view, name='doctor_list'),
    path('add/', views.add_doctor_view, name='add_doctor'),
    path('<int:pk>/', views.doctor_detail_view, name='doctor_detail'), # Normalized to pk
    path('<int:pk>/edit/', views.edit_doctor_view, name='edit_doctor'), # Normalized to pk
    # Path for deleting an existing doctor (NEW)
    path('<int:pk>/delete/', views.delete_doctor_view, name='delete_doctor'), # Normalized to pk
]