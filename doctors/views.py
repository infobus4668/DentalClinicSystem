# DENTALCLINICSYSTEM/doctors/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # <-- THIS LINE IS ADDED
from django.contrib import messages
from django.db.models import ProtectedError
from .models import Doctor
from .forms import DoctorForm

# View for listing all doctors
@login_required
def doctor_list_view(request):
    all_doctors = Doctor.objects.all().order_by('name')
    context = {
        'doctors_list': all_doctors,
        'page_title': 'List of Doctors'
    }
    return render(request, 'doctors/doctor_list.html', context)

# View for adding a new doctor
@login_required
def add_doctor_view(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor added successfully!')
            return redirect('doctors:doctor_list')
    else:
        form = DoctorForm()
    context = {
        'form': form,
        'page_title': 'Add New Doctor'
    }
    return render(request, 'doctors/add_doctor.html', context)

# View for a single doctor's details
@login_required
def doctor_detail_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    context = {
        'doctor': doctor,
        'page_title': f"Details for Dr. {doctor.name}"
    }
    return render(request, 'doctors/doctor_detail.html', context)

# View for editing an existing doctor
@login_required
def edit_doctor_view(request, doctor_id):
    doctor_to_edit = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor details were updated successfully!')
            return redirect('doctors:doctor_detail', doctor_id=doctor_to_edit.id)
    else:
        form = DoctorForm(instance=doctor_to_edit)

    context = {
        'form': form,
        'doctor': doctor_to_edit,
        'page_title': f"Edit Details for Dr. {doctor_to_edit.name}"
    }
    return render(request, 'doctors/edit_doctor.html', context)

# View for deleting an existing doctor (handles confirmation)
@login_required
def delete_doctor_view(request, doctor_id):
    doctor_to_delete = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        try:
            doctor_to_delete.delete()
            messages.success(request, f'Dr. {doctor_to_delete.name} has been deleted successfully.')
            return redirect('doctors:doctor_list')
        except ProtectedError:
            messages.error(request, f'Cannot delete Dr. "{doctor_to_delete.name}" because they are associated with existing appointments.')
            return redirect('doctors:doctor_list')
    
    context = {
        'doctor': doctor_to_delete,
        'page_title': f"Confirm Delete: Dr. {doctor_to_delete.name}"
    }
    return render(request, 'doctors/doctor_confirm_delete.html', context)