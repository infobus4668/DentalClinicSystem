# DENTALCLINICSYSTEM/patients/forms.py

from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    
    class Meta:
        model = Patient
        fields = [
            'name', 
            'date_of_birth', 
            'gender', 
            'contact_number', 
            'place',
            'pincode', # ADDED: Include the new pincode field
            'allergies', 
            'ongoing_conditions', 
            'medications'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'ongoing_conditions': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'date_of_birth': 'Date of Birth',
            'ongoing_conditions': 'Ongoing conditions',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and common styling class
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter full name'})
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'e.g., 9876543210'})
        self.fields['place'].widget.attrs.update({'placeholder': 'e.g., Chennai'})
        self.fields['pincode'].widget.attrs.update({'placeholder': 'e.g., 600001'}) # ADDED: Placeholder for pincode

        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})