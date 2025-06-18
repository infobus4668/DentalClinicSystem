from django import forms
from .models import StaffMember

class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = [
            'name', 'role', 'contact_number', 'email', 
            'date_joined', 'is_active', 'notes'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any relevant notes...'}),
            # Ensure other fields that need specific widgets or extensive styling are defined here
            # or handled in the __init__ method.
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 9876543210'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g., staff@example.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Checkbox styling might need specific CSS
        }
        labels = {
            'email': 'Email Address (Optional)',
            'is_active': 'Currently Employed?',
            'date_joined': 'Date Joined (YYYY-MM-DD)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add common styling class to any fields not explicitly handled by Meta.widgets,
        # though in this case, most are.
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs and not isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-control'})
            # Special handling for checkbox if you want it wrapped or styled differently than default form-control
            # For example, to align with Bootstrap, you might wrap it or just ensure it has form-check-input
            # self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})