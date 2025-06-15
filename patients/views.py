# DENTALCLINICSYSTEM/patients/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, ProtectedError
from .models import Patient
from .forms import PatientForm
from billing.models import Invoice
from appointments.models import Appointment

@login_required
def patient_list_view(request):
    query = request.GET.get('q', '')
    if query:
        all_patients = Patient.objects.filter(
            Q(name__icontains=query) |
            Q(contact_number__icontains=query)
        ).order_by('name')
    else:
        all_patients = Patient.objects.all().order_by('name')

    context = {
        'patients_list': all_patients,
        'page_title': 'List of Patients',
        'search_query': query
    }
    return render(request, 'patients/patient_list.html', context)

@login_required
def add_patient_view(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient "{form.cleaned_data.get("name")}" was added successfully.')
            return redirect('patients:patient_list')
    else:
        form = PatientForm()
    context = {
        'form': form,
        'page_title': 'Add New Patient'
    }
    return render(request, 'patients/add_patient.html', context)

@login_required
def patient_detail_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient_appointments = patient.appointments.all().order_by('-appointment_datetime')
    patient_invoices = Invoice.objects.filter(patient=patient).order_by('-invoice_date')

    context = {
        'patient': patient,
        'patient_appointments': patient_appointments,
        'patient_invoices': patient_invoices,
        'page_title': f"Details for {patient.name}"
    }
    return render(request, 'patients/patient_detail.html', context)

@login_required
def edit_patient_view(request, patient_id):
    patient_to_edit = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient details were updated successfully!')
            return redirect('patients:patient_detail', patient_id=patient_to_edit.id)
    else:
        form = PatientForm(instance=patient_to_edit)

    context = {
        'form': form,
        'patient': patient_to_edit,
        'page_title': f"Edit Details for {patient_to_edit.name}"
    }
    return render(request, 'patients/edit_patient.html', context)

@login_required
def delete_patient_view(request, patient_id):
    patient_to_delete = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        try:
            patient_to_delete.delete()
            messages.success(request, f'Patient "{patient_to_delete.name}" has been deleted successfully.')
            return redirect('patients:patient_list')
        except ProtectedError:
            messages.error(request, f'Cannot delete "{patient_to_delete.name}" because they have existing appointments or other associated records.')
            return redirect('patients:patient_detail', patient_id=patient_id)

    context = {
        'patient': patient_to_delete,
        'page_title': f"Confirm Delete: {patient_to_delete.name}"
    }
    return render(request, 'patients/patient_confirm_delete.html', context)