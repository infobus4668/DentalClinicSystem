from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from appointments.models import Appointment
from .models import DentalRecord, Prescription, PrescriptionItem, DentalImage
from .forms import DentalRecordForm, PrescriptionForm, PrescriptionItemFormSet
# MODIFIED: Importing the correct decorator
from staff.decorators import role_required 

# This defines which roles are allowed to manage dental records.
DENTAL_STAFF_ROLES = ['MANAGER', 'DOCTOR', 'ASSIST', 'HYGIEN']

@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(DENTAL_STAFF_ROLES)
def manage_dental_record_view(request, appointment_pk):
    """
    This view handles Creating or Editing the main DentalRecord
    (clinical notes, treatments) and uploading associated images.
    """
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    # The record is linked to the appointment, so we get_or_create based on that
    record, created = DentalRecord.objects.get_or_create(appointment=appointment)

    if request.method == 'POST':
        # Check if the form submission is for uploading an image
        if request.POST.get('action') == 'upload_image':
            image_file = request.FILES.get('image')
            caption = request.POST.get('caption', '')
            if image_file:
                DentalImage.objects.create(
                    dental_record=record,
                    image=image_file,
                    caption=caption
                )
                messages.success(request, 'Image uploaded successfully!')
            else:
                messages.error(request, 'No image file was selected.')
            return redirect('dental_records:manage_dental_record', appointment_pk=appointment.pk)

        # If not an image upload, process the main dental record form
        else:
            form = DentalRecordForm(request.POST, instance=record)
            if form.is_valid():
                form.save()
                messages.success(request, 'Dental record saved successfully!')
                return redirect('appointments:appointment_detail', pk=appointment.pk)
    else: # GET request
        form = DentalRecordForm(instance=record)

    context = {
        'form': form,
        'appointment': appointment,
        'record': record,
        'page_title': f"Manage Dental Record for {appointment.patient.name}"
    }
    return render(request, 'dental_records/manage_dental_record.html', context)


@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(DENTAL_STAFF_ROLES)
def manage_prescription_view(request, appointment_pk):
    """
    This view handles Creating or Editing a Prescription and its Items
    for a specific appointment.
    """
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    dental_record, __ = DentalRecord.objects.get_or_create(appointment=appointment)

    # A prescription is linked to the dental record.
    try:
        # This works because of the OneToOneField relationship
        prescription = dental_record.prescription
    except Prescription.DoesNotExist:
        prescription = None

    if request.method == 'POST':
        # We bind the main form and the formset to the POST data
        prescription_form = PrescriptionForm(request.POST, instance=prescription, prefix='presc')
        item_formset = PrescriptionItemFormSet(request.POST, instance=prescription, prefix='items')

        if prescription_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    # Save the main prescription object
                    saved_prescription = prescription_form.save(commit=False)
                    saved_prescription.dental_record = dental_record
                    saved_prescription.save()

                    # Save the related prescription items
                    item_formset.instance = saved_prescription
                    item_formset.save()
                    
                    messages.success(request, 'Prescription saved successfully!')
                    return redirect(reverse('appointments:appointment_detail', kwargs={'pk': appointment.pk}))
            except Exception as e:
                messages.error(request, f"An error occurred while saving the prescription: {e}")

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # For a GET request, create unbound forms
        prescription_form = PrescriptionForm(instance=prescription, prefix='presc')
        item_formset = PrescriptionItemFormSet(instance=prescription, prefix='items')

    context = {
        'prescription_form': prescription_form,
        'item_formset': item_formset,
        'appointment': appointment,
        'page_title': f"Manage Prescription for {appointment.patient.name}"
    }
    return render(request, 'dental_records/manage_prescription.html', context)


@login_required
# MODIFIED: Using the correct decorator with the appropriate roles
@role_required(DENTAL_STAFF_ROLES)
def prescription_print_view(request, prescription_pk):
    """
    Generates a printable view for a single prescription.
    """
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'dental_record__appointment__patient',
            'dental_record__appointment__doctor'
        ),
        pk=prescription_pk
    )
    prescription_items = prescription.items.all()

    context = {
        'prescription': prescription,
        'prescription_items': prescription_items,
        'page_title': f'Prescription for {prescription.dental_record.appointment.patient.name}'
    }
    return render(request, 'dental_records/prescription_print.html', context)