from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from appointments.models import Appointment
from .models import DentalRecord, Prescription, PrescriptionItem, DentalImage # MODIFIED: Imported DentalImage
from .forms import DentalRecordForm, PrescriptionForm, PrescriptionItemFormSet

@login_required
def manage_dental_record_view(request, appointment_id):
    """
    This view handles Creating or Editing the main DentalRecord
    (clinical notes, treatments) and uploading associated images.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    record, created = DentalRecord.objects.get_or_create(appointment=appointment)

    if request.method == 'POST':
        # --- NEW: Image Upload Logic ---
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
            return redirect('dental_records:manage_dental_record', appointment_id=appointment.id)

        # --- Existing: Dental Record Form Logic ---
        # If not an image upload, process the main dental record form
        else:
            form = DentalRecordForm(request.POST, instance=record)
            if form.is_valid():
                form.save()
                messages.success(request, 'Dental record saved successfully!')
                return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else: # GET request
        form = DentalRecordForm(instance=record)

    context = {
        'form': form,
        'appointment': appointment,
        'record': record, # MODIFIED: Pass the record object to access its images in the template
        'page_title': f"Manage Dental Record for {appointment.patient.name}"
    }
    return render(request, 'dental_records/manage_dental_record.html', context)


@login_required
def manage_prescription_view(request, appointment_id):
    """
    This view handles Creating or Editing a Prescription and its Items
    for a specific appointment.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    dental_record, __ = DentalRecord.objects.get_or_create(appointment=appointment)

    try:
        prescription = dental_record.prescription
    except Prescription.DoesNotExist:
        prescription = None

    if request.method == 'POST':
        prescription_form = PrescriptionForm(request.POST, instance=prescription, prefix='presc')
        item_formset = PrescriptionItemFormSet(request.POST, instance=prescription, prefix='items')

        if prescription_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    saved_prescription = prescription_form.save(commit=False)
                    saved_prescription.dental_record = dental_record
                    saved_prescription.save()

                    item_formset.instance = saved_prescription
                    item_formset.save()
                    
                    messages.success(request, 'Prescription saved successfully!')
                    return redirect(reverse('appointments:appointment_detail', kwargs={'appointment_id': appointment.id}))
            except Exception as e:
                messages.error(request, f"An error occurred while saving the prescription: {e}")

        else:
            messages.error(request, "Please correct the errors below.")
    else:
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
def prescription_print_view(request, prescription_id):
    """
    Generates a printable view for a single prescription.
    """
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'dental_record__appointment__patient',
            'dental_record__appointment__doctor'
        ),
        pk=prescription_id
    )
    prescription_items = prescription.items.all()

    context = {
        'prescription': prescription,
        'prescription_items': prescription_items,
        'page_title': f'Prescription for {prescription.dental_record.appointment.patient.name}'
    }
    return render(request, 'dental_records/prescription_print.html', context)