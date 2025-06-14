# doctors/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings

class Doctor(models.Model):
    # This is the crucial link to the built-in User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Keep doctor record if user is deleted
        null=True,
        blank=True,
        related_name='doctor_profile' # Allows us to use user.doctor_profile
    )

    # FIX: Updated the regex to match the '+91' prefix followed by 10 digits.
    phone_regex = RegexValidator(
        regex=r'^\+91\d{10}$', 
        message="Phone number must be in the format: +91 followed by 10 digits."
    )

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
    # The validator for this field is now corrected.
    contact_number = models.CharField(max_length=15, unique=True, validators=[phone_regex]) 
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    credentials = models.TextField(blank=True, null=True) # E.g., license number, qualifications
    availability_notes = models.TextField(blank=True, null=True, help_text="E.g., Mon-Fri 9am-5pm")

    # --- Record Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically add +91 prefix to contact number
        if self.contact_number and not self.contact_number.startswith('+91'):
            self.contact_number = f"+91{self.contact_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.name} ({self.get_specialization_display()})"

    class Meta:
        ordering = ['name']