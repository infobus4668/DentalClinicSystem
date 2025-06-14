from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list_view, name='doctor_list'),
    path('add/', views.add_doctor_view, name='add_doctor'),
    path('<int:doctor_id>/', views.doctor_detail_view, name='doctor_detail'),
    path('<int:doctor_id>/edit/', views.edit_doctor_view, name='edit_doctor'),
    # Path for deleting an existing doctor (NEW)
    path('<int:doctor_id>/delete/', views.delete_doctor_view, name='delete_doctor'),
]