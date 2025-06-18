# appointments/views.py

from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appointment
from .forms import AppointmentForm
from dental_records.models import DentalRecord
from dental_records.models import Prescription
from datetime import timedelta
from patients.models import Patient
from billing.models import Invoice
from django.utils import timezone

# --- API VIEW (Updated for Doctor-Specific View) ---
@login_required
def appointment_api_view(request):
    user = request.user
    # Start with all appointments, then filter if user is a doctor
    all_appointments = Appointment.objects.all().select_related('patient', 'doctor')

    if hasattr(user, 'doctor_profile'):
        all_appointments = all_appointments.filter(doctor=user.doctor_profile)

    events = []
    for appointment in all_appointments:
        events.append({
            'title': appointment.patient.name,
            'start': appointment.appointment_datetime.isoformat(),
            'end': (appointment.appointment_datetime + timedelta(minutes=45)).isoformat(),
            'url': reverse('appointments:appointment_detail', args=[appointment.id]),
            'color': '#28a745' if appointment.status == 'CMP' else '#17a2b8',
            'extendedProps': {
                'patient': appointment.patient.name,
                'doctor': f"Dr. {appointment.doctor.name}",
                'time': appointment.appointment_datetime.strftime('%I:%M %p'),
                'reason': appointment.reason or 'No reason provided'
            }
        })
    return JsonResponse(events, safe=False)

# --- Regular Views (Updated for Doctor-Specific View) ---
@login_required
def appointment_list_view(request):
    user = request.user
    # Start with all appointments, then filter if user is a doctor
    all_appointments = Appointment.objects.order_by('-appointment_datetime')

    if hasattr(user, 'doctor_profile'):
        all_appointments = all_appointments.filter(doctor=user.doctor_profile)

    context = {'appointments_list': all_appointments, 'page_title': 'List of Appointments'}
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def schedule_appointment_view(request):
    initial_data = {}
    patient_id = request.GET.get('patient_id')
    if patient_id:
        try:
            patient = Patient.objects.get(id=patient_id)
            initial_data['patient'] = patient
        except Patient.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentForm(initial=initial_data)

    context = {
        'form': form,
        'page_title': 'Schedule New Appointment'
    }
    return render(request, 'appointments/schedule_appointment.html', context)

@login_required
def appointment_detail_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    dental_record = None
    try:
        dental_record = appointment.dental_record 
    except (DentalRecord.DoesNotExist, AttributeError):
        pass

    context = {
        'appointment': appointment,
        'dental_record': dental_record,
        'page_title': f"Appointment Details for {appointment.patient.name}"
    }
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def edit_appointment_view(request, appointment_id):
    appointment_to_edit = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment_to_edit)
        if form.is_valid():
            form.save()
            return redirect('appointments:appointment_detail', appointment_id=appointment_to_edit.id)
    else:
        form = AppointmentForm(instance=appointment_to_edit)
    context = {'form': form, 'appointment': appointment_to_edit, 'page_title': f"Edit Appointment"}
    return render(request, 'appointments/edit_appointment.html', context)

@login_required
def delete_appointment_view(request, appointment_id):
    appointment_to_delete = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment_to_delete.delete()
        return redirect('appointments:appointment_list')
    context = {'appointment': appointment_to_delete, 'page_title': f"Confirm Delete"}
    return render(request, 'appointments/appointment_confirm_delete.html', context)


@login_required
def print_summary_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    context = {
        'appointment': appointment,
        'page_title': f'Summary for {appointment.patient.name} on {appointment.appointment_datetime.date()}'
    }

    try:
        invoice = appointment.invoice
        context['invoice'] = invoice
        context['invoice_items'] = invoice.invoice_items.all()
    except (Invoice.DoesNotExist, AttributeError):
        context['invoice'] = None
        context['invoice_items'] = None

    try:
        prescription = appointment.dental_record.prescription
        context['prescription'] = prescription
        context['prescription_items'] = prescription.items.all()
    except (DentalRecord.DoesNotExist, Prescription.DoesNotExist, AttributeError):
        context['prescription'] = None
        context['prescription_items'] = None
        
    return render(request, 'appointments/print_summary.html', context)

@login_required
def print_bill_summary_view(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor'), 
        pk=appointment_id
    )
    
    context = {
        'appointment': appointment,
        'page_title': f'Bill for {appointment.patient.name} on {appointment.appointment_datetime.date()}'
    }

    try:
        invoice = Invoice.objects.get(appointment=appointment)
        invoice_items = invoice.invoice_items.all()
        services = invoice_items.filter(service__isnull=False)
        products = invoice_items.filter(product__isnull=False)
        context['invoice'] = invoice
        context['services_list'] = services
        context['products_list'] = products
    except Invoice.DoesNotExist:
        context['invoice'] = None
        context['services_list'] = []
        context['products_list'] = []

    try:
        prescription = appointment.dental_record.prescription
        context['prescription'] = prescription
        context['prescription_items'] = prescription.items.all()
    except (DentalRecord.DoesNotExist, Prescription.DoesNotExist, AttributeError):
        context['prescription'] = None
        context['prescription_items'] = []
        
    return render(request, 'appointments/print_bill_summary.html', context)