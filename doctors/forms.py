# doctors/forms.py

from django import forms
from .models import Doctor
from django.contrib.auth.models import User

class DoctorForm(forms.ModelForm):
    # Field to select a user, filtering out users already linked to other doctors or staff
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(doctor_profile__isnull=True, staff_profile__isnull=True),
        required=False,
        help_text="Optional: Link this doctor profile to a system user account for login."
    )

    class Meta:
        model = Doctor
        # This list now perfectly matches the fields on the updated Doctor model
        fields = [
            'user', # <<< ADDED
            'name', 
            'specialization',
            'contact_number', 
            'email',
            'credentials', 
            'availability_notes'
        ]
        widgets = {
            'credentials': forms.Textarea(attrs={'rows': 3}),
            'availability_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'E.g., Mon-Fri 9am-5pm, available on alternate Saturdays'}),
        }
        labels = {
            'email': 'Email Address (Optional)',
            'availability_notes': 'Availability Notes / Schedule',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and common styling class
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter full name'})
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'Enter 10-digit number'})
        self.fields['email'].widget.attrs.update({'placeholder': 'e.g., doctor@example.com'})
        self.fields['credentials'].widget.attrs.update({'placeholder': 'e.g., License No., Degrees'})
        
        for field_name, field in self.fields.items():
            # Add select2 class for better dropdowns
            if field_name == 'user':
                field.widget.attrs.update({'class': 'form-control select2-enable'})
            elif 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})
        
        # If editing an existing doctor that has a user, add that user back to the queryset
        if self.instance and self.instance.user:
            self.fields['user'].queryset = User.objects.filter(doctor_profile__isnull=True, staff_profile__isnull=True) | User.objects.filter(pk=self.instance.user.pk)