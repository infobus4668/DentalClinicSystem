# DENTALCLINICSYSTEM/patients/models.py

from django.db import models
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField

class Patient(models.Model):
    name = models.CharField(max_length=120)
    date_of_birth = models.DateField()
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    contact_number = PhoneNumberField(
        blank=False, null=False,
        help_text="Enter phone number with country code."
    )
    place = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(
        max_length=20,
        blank=True, null=True,
        help_text="Enter postal code."
    )
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
        return f"{self.name} (ID: {self.pk})" # Normalized to pk

    class Meta:
        ordering = ['name']