from django.contrib import admin
from .models import Doctor

# This defines how a Doctor's profile will look when shown "inline"
# on another model's admin page (specifically, the User admin page).
class DoctorProfileInline(admin.StackedInline):
    model = Doctor
    can_delete = False # You shouldn't delete a profile from the user page. Delete the user instead.
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'
    # Specify the fields to show in the inline form
    fields = ('name', 'contact_number', 'email', 'specialization', 'credentials', 'availability_notes')

# This customizes the main list view for Doctors in the admin.
class DoctorAdmin(admin.ModelAdmin):
    # Columns to display in the doctor list
    list_display = ('name', 'get_specialization_display', 'contact_number', 'email', 'user') 
    
    # Add a search bar to search by these fields
    search_fields = ('name', 'email', 'user__username') 
    
    # Add a filter sidebar
    list_filter = ('specialization',)
    
    # Use a search popup for the user field instead of a long dropdown
    raw_id_fields = ('user',)

# Register your Doctor model with its custom admin options
admin.site.register(Doctor, DoctorAdmin)