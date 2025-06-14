# DENTALCLINICSYSTEM/patients/models.py

from django.db import models
from django.utils import timezone
from datetime import date
from django.core.validators import RegexValidator

class Patient(models.Model):
    # DEFINE VALIDATORS
    # FIX: Updated the regex to match the '+91' prefix followed by 10 digits.
    phone_regex = RegexValidator(
        regex=r'^\+91\d{10}$', 
        message="Phone number must be in the format: +91 followed by 10 digits."
    )
    pincode_regex = RegexValidator(
        regex=r'^\d{6}$',
        message="PIN code must be exactly 6 digits."
    )

    name = models.CharField(max_length=120)
    date_of_birth = models.DateField()
    
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # The validator for this field is now corrected.
    contact_number = models.CharField(
        max_length=15, 
        validators=[phone_regex], 
        blank=True,
        help_text="Enter 10-digit mobile number."
    )
    
    place = models.CharField(
        max_length=100, 
        blank=True, 
        default='', 
        help_text="City or town of residence."
    )
    
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

    # This save method correctly formats the number before it is validated.
    def save(self, *args, **kwargs):
        # Check if contact_number has a value and doesn't already start with +91
        if self.contact_number and not self.contact_number.startswith('+91'):
            self.contact_number = f"+91{self.contact_number}"
        super().save(*args, **kwargs) # Call the original save method

    def __str__(self):
        return f"{self.name} (ID: {self.pk})"

    class Meta:
        ordering = ['name']