from django import forms
from .models import DentalLab, LabCase
from patients.models import Patient
from doctors.models import Doctor

class DentalLabForm(forms.ModelForm):
    class Meta:
        model = DentalLab
        fields = [
            'name', 'contact_person', 'contact_number', 'email', 
            'address', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of the Dental Lab'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +91 9876543210'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g., contact@labname.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Notes about specialties, turnaround times, etc.'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
#... rest of DentalLabForm...

class LabCaseForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    lab = forms.ModelChoiceField(
        queryset=DentalLab.objects.filter(is_active=True).order_by('name'),
        label="Dental Lab",
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    
    class Meta:
        model = LabCase
        fields = [
            'patient', 'doctor', 'lab', 'case_type', 'description', 'status',
            'cost', 'date_sent', 'date_due', 'date_received'
        ]
        widgets = {
            'case_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Zirconia Crown, PFM Bridge'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Detailed instructions for the lab...'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'date_sent': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_due': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_received': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
#... rest of LabCaseForm...