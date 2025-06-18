from django import forms
from django.forms import inlineformset_factory # For PrescriptionItem formset
from .models import DentalRecord, Prescription, PrescriptionItem

# --- Existing DentalRecordForm ---
class DentalRecordForm(forms.ModelForm):
    class Meta:
        model = DentalRecord
        fields = ['clinical_notes', 'treatments_performed']
        widgets = {
            'clinical_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': "Enter clinical notes, observations, diagnosis..."}),
            'treatments_performed': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': "Detail treatments performed..."}),
        }
        labels = {
            'clinical_notes': 'Clinical Notes & Diagnosis',
            'treatments_performed': 'Treatments Performed',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})


# --- NEW: Forms for Prescriptions ---

class PrescriptionForm(forms.ModelForm):
    """Form for the main Prescription object."""
    class Meta:
        model = Prescription
        # The dental_record is linked in the view, so we only need the notes.
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Optional general notes for the whole prescription...'}),
        }

class PrescriptionItemForm(forms.ModelForm):
    """Form for a single item within a prescription."""
    class Meta:
        model = PrescriptionItem
        fields = ['medication_name', 'dosage', 'frequency', 'duration', 'notes']
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Amoxicillin'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 tablet 3 times a day'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., for 5 days'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes, e.g., after food'}),
        }

# Create a formset for PrescriptionItems, linked to a Prescription
PrescriptionItemFormSet = inlineformset_factory(
    Prescription,               # Parent model
    PrescriptionItem,           # Child model
    form=PrescriptionItemForm,  # The form to use for each item
    fields=['medication_name', 'dosage', 'frequency', 'duration', 'notes'],
    extra=1,                    # Show 1 empty form by default
    can_delete=True,            # Allow deleting items when editing
    can_delete_extra=True       # Allow deleting the initial empty forms too
)