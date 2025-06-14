# doctors/admin.py

from django.contrib import admin
from .models import Doctor

class DoctorAdmin(admin.ModelAdmin):
    # Add 'user' to the display and make it a link
    list_display = ('name', 'user', 'get_specialization_display', 'contact_number', 'email', 'updated_at')
    
    search_fields = ('name', 'email', 'contact_number', 'specialization', 'user__username') 
    
    list_filter = ('specialization',)
    
    # Use a search popup for the user field instead of a dropdown
    raw_id_fields = ('user',)

    ordering = ('name',)

admin.site.register(Doctor, DoctorAdmin)