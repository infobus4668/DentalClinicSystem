from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Patient
from .forms import PatientForm
# MODIFIED: Importing the correct decorator
from staff.decorators import role_required

# This list defines which roles can access patient records.
PATIENT_ACCESS_ROLES = ['MANAGER', 'RECEP', 'DOCTOR', 'ASSIST', 'HYGIEN', 'OTHER']

@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(allowed_roles=PATIENT_ACCESS_ROLES)
def patient_list_view(request):
    patients = Patient.objects.all().order_by('name')
    context = {
        'patients_list': patients,
        'page_title': 'Patients'
    }
    return render(request, 'patients/patient_list.html', context)

@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(allowed_roles=PATIENT_ACCESS_ROLES)
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    context = {
        'patient': patient,
        'page_title': f'Patient: {patient.name}'
    }
    return render(request, 'patients/patient_detail.html', context)

@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(allowed_roles=PATIENT_ACCESS_ROLES)
def add_patient_view(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient added successfully!')
            return redirect('patients:patient_list')
    else:
        form = PatientForm()
    context = {
        'form': form,
        'page_title': 'Add New Patient'
    }
    return render(request, 'patients/add_patient.html', context)

@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(allowed_roles=PATIENT_ACCESS_ROLES)
def edit_patient_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient details updated successfully!')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    context = {
        'form': form,
        'page_title': 'Edit Patient'
    }
    return render(request, 'patients/edit_patient.html', context)

@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(allowed_roles=['MANAGER']) # Only managers can delete patients
def delete_patient_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient deleted successfully.')
        return redirect('patients:patient_list')
    context = {
        'patient': patient,
        'page_title': 'Confirm Delete'
    }
    return render(request, 'patients/patient_confirm_delete.html', context)