from django.contrib import admin
from .models import DentalRecord, Prescription, PrescriptionItem # Import all three models

# This defines how a Prescription's items will look when shown "inline"
# on the Prescription admin page. We use TabularInline for a compact table layout.
class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1 # Start with one empty form for a new medication item
    fields = ('medication_name', 'dosage', 'frequency', 'duration', 'notes')

# This defines the admin page for a standalone Prescription.
# It includes the inline for its items.
class PrescriptionAdmin(admin.ModelAdmin):
    inlines = [PrescriptionItemInline]
    list_display = ('__str__', 'date_prescribed')
    search_fields = ('dental_record__appointment__patient__name',)

# This defines how a Prescription form will look when shown "inline"
# on the DentalRecord admin page. We use StackedInline for a standard form layout.
class PrescriptionInline(admin.StackedInline):
    model = Prescription
    can_delete = False # You typically delete the parent DentalRecord, not just the prescription container.
    verbose_name_plural = 'Prescription'
    # Since Prescription's primary key is the DentalRecord, Django handles the link automatically.
    # The fields shown here are for the Prescription model itself.
    fields = ('notes',) 

# This updates the existing DentalRecordAdmin to include the Prescription inline
class DentalRecordAdmin(admin.ModelAdmin):
    # Keep all the helpful display options from before
    list_display = ('get_appointment_patient', 'get_appointment_doctor', 'get_appointment_datetime', 'created_at')
    list_filter = ('appointment__appointment_datetime', 'appointment__doctor')
    search_fields = ('appointment__patient__name', 'appointment__doctor__name', 'clinical_notes', 'treatments_performed')
    raw_id_fields = ('appointment',)
    
    # Add the Prescription inline to this admin page
    inlines = [PrescriptionInline] # <<<--- ADD THIS LINE

    # Keep the custom methods from before
    def get_appointment_patient(self, obj):
        return obj.appointment.patient.name
    get_appointment_patient.short_description = 'Patient'
    get_appointment_patient.admin_order_field = 'appointment__patient__name'

    def get_appointment_doctor(self, obj):
        return f"Dr. {obj.appointment.doctor.name}"
    get_appointment_doctor.short_description = 'Doctor'
    get_appointment_doctor.admin_order_field = 'appointment__doctor__name'

    def get_appointment_datetime(self, obj):
        return obj.appointment.appointment_datetime
    get_appointment_datetime.short_description = 'Appointment Time'
    get_appointment_datetime.admin_order_field = 'appointment__appointment_datetime'

# --- Registration ---
# Unregister the old DentalRecord admin if it's already registered to avoid conflicts
# and re-register it with the new version that includes the inline.
# A simple try/except block handles the case where it might not be registered yet.
try:
    admin.site.unregister(DentalRecord)
except admin.sites.NotRegistered:
    pass
admin.site.register(DentalRecord, DentalRecordAdmin)

# Register the standalone Prescription admin (which includes PrescriptionItemInline)
admin.site.register(Prescription, PrescriptionAdmin)

# We don't register PrescriptionItem separately because it's managed inline.