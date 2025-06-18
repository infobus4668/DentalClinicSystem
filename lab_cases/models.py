# DENTALCLINICSYSTEM/lab_cases/models.py

from django.db import models
from django.utils import timezone
from patients.models import Patient
from doctors.models import Doctor
from decimal import Decimal

class DentalLab(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Notes about the lab, like specialties or turnaround times.")
    is_active = models.BooleanField(default=True, help_text="Is this lab currently used by the clinic?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Dental Lab"; verbose_name_plural = "Dental Labs"; ordering = ['name']
    def __str__(self): return self.name

class LabCase(models.Model):
    CASE_STATUS_CHOICES = [
        ('CREATED', 'Case Created'),
        ('SENT', 'Sent to Lab'),
        ('RECEIVED', 'Received from Lab'),
        ('COMPLETED', 'Completed / Fitted'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # CHANGED: on_delete policy to PROTECT
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='lab_cases')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, null=True, blank=True, related_name='lab_cases', help_text="Doctor who ordered the case.")
    
    lab = models.ForeignKey(DentalLab, on_delete=models.PROTECT, related_name='cases', help_text="The dental lab this case was sent to.")
    case_type = models.CharField(max_length=100, help_text="e.g., 'Zirconia Crown', 'PFM Bridge', 'Complete Denture'")
    description = models.TextField(help_text="Detailed instructions for the lab, including tooth numbers, shade, materials, etc.")
    status = models.CharField(max_length=10, choices=CASE_STATUS_CHOICES, default='CREATED')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cost of the lab work.")
    date_sent = models.DateField(null=True, blank=True)
    date_due = models.DateField(null=True, blank=True, help_text="Expected return date from the lab.")
    date_received = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Lab Case"; verbose_name_plural = "Lab Cases"; ordering = ['-date_due', '-date_sent']
    def __str__(self): return f"Lab Case for {self.patient.name} ({self.case_type}) - Status: {self.get_status_display()}"