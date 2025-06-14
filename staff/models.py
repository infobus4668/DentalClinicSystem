# staff/models.py

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings

class StaffMember(models.Model):
    # This is the crucial link to the built-in User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='staff_profile' # This allows us to use user.staff_profile
    )
    
    # FIX: Updated the regex to match the '+91' prefix followed by 10 digits.
    phone_regex = RegexValidator(
        regex=r'^\+91\d{10}$', 
        message="Phone number must be in the format: +91 followed by 10 digits."
    )

    # --- Fields from your list ---
    name = models.CharField(max_length=120)
    
    ROLE_CHOICES = [
        ('RECEP', 'Receptionist'),
        ('ASSIST', 'Dental Assistant'),
        ('HYGIEN', 'Dental Hygienist'),
        ('MANAGER', 'Clinic Manager'),
        ('OTHER', 'Other'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='OTHER')
    
    # The validator for this field is now corrected.
    contact_number = models.CharField(max_length=15, validators=[phone_regex], blank=True, null=True)
    
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    date_joined = models.DateField(default=timezone.now)
    
    currently_employed = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True, null=True)

    # --- Record Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.contact_number and not self.contact_number.startswith('+91'):
            self.contact_number = f"+91{self.contact_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        # We can now use the user's username for a more descriptive name
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['name']