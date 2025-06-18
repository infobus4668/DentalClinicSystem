from django.db import models
from django.contrib.auth.models import User # This import is correct

class Doctor(models.Model):
    # This field links this Doctor profile to a specific Django User account.
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='doctor_profile'
    )

    # --- Existing fields below ---
    
    # Personal Details
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, unique=True) # Assuming contact number is unique
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True) # Optional but unique if provided

    # Professional Details
    SPECIALIZATION_CHOICES = [
        ('GD', 'General Dentistry'),
        ('ORTHO', 'Orthodontics'),
        ('ENDO', 'Endodontics'),
        ('PERIO', 'Periodontics'),
        ('PROSTHO', 'Prosthodontics'),
        ('PEDO', 'Pediatric Dentistry'),
        ('OS', 'Oral Surgery'),
        ('OTHER', 'Other'),
    ]
    specialization = models.CharField(
        max_length=10,
        choices=SPECIALIZATION_CHOICES,
        default='GD' # Default to General Dentistry
    )
    credentials = models.TextField(blank=True, null=True) # E.g., license number, qualifications
    
    # For now, a simple text field for availability notes.
    # More complex scheduling can be added later.
    availability_notes = models.TextField(blank=True, null=True, help_text="E.g., Mon-Fri 9am-5pm, available on alternate Saturdays")

    # Record Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.get_specialization_display()})"