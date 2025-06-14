# DENTALCLINICSYSTEM/dental_records/models.py

from django.db import models
from appointments.models import Appointment # Import the Appointment model

# --- Existing DentalRecord Model ---
class DentalRecord(models.Model):
    # Link to a specific appointment. OneToOneField ensures each appointment
    # can have at most one primary dental record entry.
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE, # If appointment is deleted, delete this record too
        primary_key=True, # Makes the appointment field the primary key for this model
        related_name='dental_record'
    )
    
    clinical_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Doctor's clinical notes, observations, diagnosis for this visit."
    )
    
    treatments_performed = models.TextField(
        blank=True, 
        null=True,
        help_text="Details of treatments performed during this visit (e.g., 'Scaling and Polishing', 'Composite filling on #24 MOD')."
    )
    
    # Record Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        appointment_datetime_str = self.appointment.appointment_datetime.strftime("%Y-%m-%d %I:%M %p")
        return f"Dental Record for Appointment: {self.appointment.patient.name} with Dr. {self.appointment.doctor.name} on {appointment_datetime_str}"

    class Meta:
        verbose_name = "Dental Record"
        verbose_name_plural = "Dental Records"


# --- NEW: Prescription Models ---

class Prescription(models.Model):
    """Represents a prescription linked to a single dental record/visit."""
    dental_record = models.OneToOneField(
        DentalRecord,
        on_delete=models.CASCADE,
        primary_key=True, # The associated DentalRecord is the key
        related_name='prescription'
    )
    date_prescribed = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="General notes for the entire prescription.")
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription for {self.dental_record.appointment.patient.name} on {self.date_prescribed}"

    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"

class PrescriptionItem(models.Model):
    """Represents a single medication item on a prescription."""
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items' # e.g., some_prescription.items.all()
    )
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True, help_text="e.g., '500mg', '1 tablet'")
    frequency = models.CharField(max_length=100, blank=True, help_text="e.g., '3 times a day', 'Once at night'")
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 'for 5 days', 'for 1 week'")
    notes = models.TextField(blank=True, null=True, help_text="Specific instructions for this medication.")

    def __str__(self):
        return f"{self.medication_name} ({self.dosage})"

    class Meta:
        verbose_name = "Prescription Item"
        verbose_name_plural = "Prescription Items"

def dental_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/patient_images/patient_<id>/<filename>
    patient_id = instance.dental_record.appointment.patient.id
    return f'patient_images/patient_{patient_id}/{filename}'

class DentalImage(models.Model):
    dental_record = models.ForeignKey(
        DentalRecord,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to=dental_image_path)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.dental_record.appointment.patient.name} - {self.caption or 'No caption'}"