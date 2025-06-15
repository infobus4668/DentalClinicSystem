# staff/forms.py

from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from .models import StaffMember
from doctors.models import Doctor
from phonenumber_field.widgets import PhoneNumberPrefixWidget # IMPORT THIS

class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control select2'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'role': forms.Select(attrs={'class': 'form-control select2'}),
            # MODIFIED: Using the new phone number widget.
            'contact_number': PhoneNumberPrefixWidget(initial='IN'),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any relevant notes'}),
            'currently_employed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        This now correctly filters the 'user' dropdown for both add and edit views.
        """
        super().__init__(*args, **kwargs)
        
        instance = self.instance

        # Get all user IDs that are already taken and should be excluded.
        excluded_ids = list(User.objects.filter(is_superuser=True).values_list('id', flat=True))
        excluded_ids.extend(list(Doctor.objects.filter(user__isnull=False).values_list('user__id', flat=True)))
        
        other_staff = StaffMember.objects.filter(user__isnull=False)
        if instance and instance.pk:
            other_staff = other_staff.exclude(pk=instance.pk)
        excluded_ids.extend(list(other_staff.values_list('user__id', flat=True)))

        self.fields['user'].queryset = User.objects.filter(
            is_active=True
        ).exclude(
            id__in=set(excluded_ids)
        )