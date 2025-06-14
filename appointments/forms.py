from django import forms
from .models import Appointment
from patients.models import Patient 
from doctors.models import Doctor   

class AppointmentForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all().order_by('name'),
        # Add 'select2-enable' class to the widget
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all().order_by('name'),
        # Add 'select2-enable' class to the widget
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    appointment_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_datetime', 
            'reason', 'status', 'notes'
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Reason for visit'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Internal notes'}),
        }
        labels = {
            'appointment_datetime': 'Appointment Date and Time',
            'reason': 'Reason for Visit',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                 field.widget.attrs.update({'class': 'form-control'})