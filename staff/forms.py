# staff/forms.py

from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from .models import StaffMember
from doctors.models import Doctor

class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control select2'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'role': forms.Select(attrs={'class': 'form-control select2'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 10-digit mobile number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any relevant notes'}),
            'currently_employed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        FIX: Rewritten logic to be more explicit and correct.
        This now correctly filters the 'user' dropdown for both add and edit views.
        """
        super().__init__(*args, **kwargs)
        
        instance = self.instance

        # Get all user IDs that are already taken and should be excluded.
        # This includes superusers and users linked to other profiles.
        
        # 1. Get IDs of superusers
        excluded_ids = list(User.objects.filter(is_superuser=True).values_list('id', flat=True))

        # 2. Get IDs of users linked to doctors
        excluded_ids.extend(list(Doctor.objects.filter(user__isnull=False).values_list('user__id', flat=True)))
        
        # 3. Get IDs of users linked to OTHER staff members.
        # If we are editing, we exclude the current staff member's user from this query.
        other_staff = StaffMember.objects.filter(user__isnull=False)
        if instance and instance.pk:
            other_staff = other_staff.exclude(pk=instance.pk)
        excluded_ids.extend(list(other_staff.values_list('user__id', flat=True)))

        # The final queryset includes all active users EXCEPT those in our exclusion list.
        self.fields['user'].queryset = User.objects.filter(
            is_active=True
        ).exclude(
            id__in=set(excluded_ids)
        )