# doctors/models.py

from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField # IMPORT THIS

class Doctor(models.Model):
    # This is the crucial link to the built-in User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Keep doctor record if user is deleted
        null=True,
        blank=True,
        related_name='doctor_profile' # Allows us to use user.doctor_profile
    )

    # REMOVED: The old phone_regex is no longer needed.

    # --- Fields from your list ---
    name = models.CharField(max_length=100)
    
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
        default='GD'
    )
    # MODIFIED: Changed CharField to the more robust PhoneNumberField.
    contact_number = PhoneNumberField(unique=True, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    credentials = models.TextField(blank=True, null=True) # E.g., license number, qualifications
    availability_notes = models.TextField(blank=True, null=True, help_text="E.g., Mon-Fri 9am-5pm")

    # --- Record Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # REMOVED: The custom save method is no longer needed.

    def __str__(self):
        return f"Dr. {self.name} ({self.get_specialization_display()})"

    class Meta:
        ordering = ['name']