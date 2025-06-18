from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # <<<--- ADD THIS IMPORT

class StaffMember(models.Model):
    # This field links this Staff profile to a specific Django User account.
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='staff_profile'
    )

    # --- Existing fields below ---

    ROLE_CHOICES = [
        ('RECEP', 'Receptionist'),
        ('ASSIST', 'Dental Assistant'),
        ('HYGIEN', 'Dental Hygienist'),
        ('MANAGER', 'Clinic Manager'),
        ('OTHER', 'Other'),
    ]

    # Personal Details
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='OTHER')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True) # Optional, but unique if provided

    date_joined = models.DateField(default=timezone.now, blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Is the staff member currently employed?")

    # Notes (optional)
    notes = models.TextField(blank=True, null=True)

    # Record Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['name'] # Order staff members by name by default