# DENTALCLINICSYSTEM/patients/models.py

from django.db import models
from django.utils import timezone
from datetime import date
from django.core.validators import RegexValidator

class Patient(models.Model):
    # DEFINE VALIDATORS for Indian phone numbers and PIN codes
    phone_regex = RegexValidator(
        regex=r'^\d{10}$', 
        message="Phone number must be exactly 10 digits."
    )
    pincode_regex = RegexValidator(
        regex=r'^\d{6}$',
        message="PIN code must be exactly 6 digits."
    )

    name = models.CharField(max_length=120)
    date_of_birth = models.DateField()
    
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # MODIFIED: Added the phone number validator
    contact_number = models.CharField(
        max_length=10, 
        validators=[phone_regex], 
        blank=True,
        help_text="Enter 10-digit mobile number."
    )
    
    # CORRECTED: Added blank=True and a default value to fix the migration error.
    place = models.CharField(
        max_length=100, 
        blank=True, 
        default='', 
        help_text="City or town of residence."
    )
    
    # ADDED: New validated field for PIN code
    pincode = models.CharField(
        max_length=6,
        validators=[pincode_regex],
        blank=True,
        null=True,
        help_text="Enter 6-digit PIN code."
    )

    # Medical History
    allergies = models.TextField(blank=True, null=True, help_text="e.g., Penicillin, Aspirin")
    ongoing_conditions = models.TextField(blank=True, null=True, help_text="e.g., Diabetes, Hypertension")
    medications = models.TextField(blank=True, null=True, help_text="List any current medications.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __str__(self):
        return f"{self.name} (ID: {self.pk})"

    class Meta:
        ordering = ['name']