# DENTALCLINICSYSTEM/patients/forms.py

from django import forms
from .models import Patient
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

class PatientForm(forms.ModelForm):
    contact_number = PhoneNumberField(
        region="IN", 
        widget=PhoneNumberPrefixWidget(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Patient
        fields = [
            'name', 
            'date_of_birth', 
            'gender', 
            'contact_number',
            'place',
            'pincode',
            'allergies', 
            'ongoing_conditions', 
            'medications'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chennai'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 600001'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'ongoing_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'date_of_birth': 'Date of Birth',
            'ongoing_conditions': 'Ongoing Conditions',
        }