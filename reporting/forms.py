# DENTALCLINICSYSTEM/reporting/forms.py

from django import forms
from billing.models import Supplier, Product
from lab_cases.models import DentalLab
from patients.models import Patient # <-- Import the Patient model

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    lab = forms.ModelChoiceField(
        queryset=DentalLab.objects.all(),
        required=False,
        label="Dental Lab",
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )
    # CHANGED: Replaced 'place' with a 'patient' dropdown
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        required=False,
        label="Patient Name",
        widget=forms.Select(attrs={'class': 'form-control select2-enable'})
    )

    def __init__(self, *args, **kwargs):
        # Allow hiding fields that aren't needed for a specific report
        hide_supplier = kwargs.pop('hide_supplier', False)
        hide_product = kwargs.pop('hide_product', False)
        hide_lab = kwargs.pop('hide_lab', False)
        hide_patient = kwargs.pop('hide_patient', False) # <-- Handle hiding the new field
        super().__init__(*args, **kwargs)
        
        if hide_supplier: del self.fields['supplier']
        if hide_product: del self.fields['product']
        if hide_lab: del self.fields['lab']
        if hide_patient: del self.fields['patient']