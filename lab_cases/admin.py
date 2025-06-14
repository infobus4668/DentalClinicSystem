from django.contrib import admin
from .models import DentalLab, LabCase # Import both models

# Custom Admin options for the DentalLab model
class DentalLabAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'contact_number', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person', 'contact_number', 'email', 'notes')
    list_editable = ('is_active',)
    list_per_page = 20

# Custom Admin options for the LabCase model
class LabCaseAdmin(admin.ModelAdmin):
    list_display = ('case_type', 'patient', 'doctor', 'lab', 'status', 'date_sent', 'date_due')
    list_filter = ('status', 'lab', 'date_sent', 'date_due', 'doctor')
    search_fields = ('case_type', 'description', 'patient__name', 'doctor__name', 'lab__name')

    # Use raw_id_fields for ForeignKeys to avoid long dropdowns if you have many
    # patients or doctors. It provides a search popup instead.
    raw_id_fields = ('patient', 'doctor', 'lab')

    date_hierarchy = 'date_sent' # Adds date-based drilldown navigation
    list_per_page = 25

# Register your models with their custom admin options
admin.site.register(DentalLab, DentalLabAdmin)
admin.site.register(LabCase, LabCaseAdmin)