# DENTALCLINICSYSTEM/appointments/models.py

from django.db import models
from patients.models import Patient 
from doctors.models import Doctor   
from django.utils import timezone   

class Appointment(models.Model):
    # CHANGED: on_delete policy to PROTECT to prevent accidental data loss
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='appointments')

    appointment_datetime = models.DateTimeField(default=timezone.now) 
    reason = models.TextField(blank=True, null=True, help_text="Reason for the visit")

    STATUS_CHOICES = [
        ('SCH', 'Scheduled'),
        ('CNF', 'Confirmed'),
        ('CMP', 'Completed'),
        ('CAN', 'Cancelled'),
        ('NOS', 'No Show'),
    ]
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='SCH' 
    )

    notes = models.TextField(blank=True, null=True, help_text="Internal notes about the appointment")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        formatted_datetime = self.appointment_datetime.strftime("%Y-%m-%d %I:%M %p")
        return f"Appointment for {self.patient.name} with Dr. {self.doctor.name} on {formatted_datetime}"

    class Meta:
        ordering = ['appointment_datetime']