from django import forms
from .models import Doctor

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'name', 'contact_number', 'email',
            'specialization', 'credentials', 'availability_notes'
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
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'e.g., 9876543210'})
        self.fields['email'].widget.attrs.update({'placeholder': 'e.g., doctor@example.com'})
        self.fields['credentials'].widget.attrs.update({'placeholder': 'e.g., License No., Degrees'})
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})