# staff/forms.py

from django import forms
from .models import StaffMember
from django.contrib.auth.models import User

class StaffMemberForm(forms.ModelForm):
    # This queryset filters the dropdown to show only users who are not already
    # linked to a staff profile or a doctor profile.
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(staff_profile__isnull=True, doctor_profile__isnull=True),
        required=True,
        label="User Account",
        help_text="Select a user account to link to this staff profile. Only unassigned users are shown.",
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )

    class Meta:
        model = StaffMember
        fields = [
            'user', 
            'name', 
            'role', 
            'contact_number', 
            'email', 
            'date_joined', 
            'currently_employed', 
            'notes'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any relevant notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # This logic correctly handles the "edit" page.
        # It adds the staff member's current user back into the dropdown list so it can be selected.
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['user'].queryset = self.fields['user'].queryset | User.objects.filter(pk=self.instance.user.pk)

        # Apply styling to other fields
        for field_name, field in self.fields.items():
            if field_name != 'user':
                 if not isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.update({'class': 'form-control'})