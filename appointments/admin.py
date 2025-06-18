from django.contrib import admin
from .models import Appointment # Import your Appointment model

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_datetime', 'status', 'reason')
    list_filter = ('status', 'doctor', 'appointment_datetime')
    search_fields = ('patient__name', 'doctor__name', 'reason')
    list_per_page = 20 # Show 20 appointments per page in admin

# Register your models here.
admin.site.register(Appointment, AppointmentAdmin) # Register Appointment with its custom admin options