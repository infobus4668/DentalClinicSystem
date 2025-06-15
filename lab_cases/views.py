# DENTALCLINICSYSTEM/lab_cases/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.contrib import messages
from .models import DentalLab, LabCase
from .forms import DentalLabForm, LabCaseForm
# MODIFIED: Importing the role_required decorator
from staff.decorators import role_required

# Defines which roles can manage lab cases.
LAB_ACCESS_ROLES = ['MANAGER', 'RECEP', 'DOCTOR', 'ASSIST']


@login_required
# MODIFIED: Added role-based security
@role_required(allowed_roles=LAB_ACCESS_ROLES)
def lab_list_view(request):
    """
    This view handles displaying a list of all dental labs.
    """
    all_labs = DentalLab.objects.all()
    context = {
        'labs_list': all_labs,
        'page_title': 'Dental Laboratories'
    }
    return render(request, 'lab_cases/lab_list.html', context)


@login_required
# MODIFIED: Restricting lab management to Managers only
@role_required(allowed_roles=['MANAGER'])
def add_lab_view(request):
    """
    This view handles the creation of a new dental lab.
    """
    if request.method == 'POST':
        form = DentalLabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New dental lab added successfully!')
            return redirect('lab_cases:lab_list')
    else:
        form = DentalLabForm()

    context = {
        'form': form,
        'page_title': 'Add New Dental Lab'
    }
    return render(request, 'lab_cases/add_lab.html', context)

@login_required
# MODIFIED: Restricting lab management to Managers only
@role_required(allowed_roles=['MANAGER'])
def edit_lab_view(request, lab_id):
    """
    This view handles editing an existing dental lab.
    """
    lab_to_edit = get_object_or_404(DentalLab, id=lab_id)

    if request.method == 'POST':
        form = DentalLabForm(request.POST, instance=lab_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{lab_to_edit.name}' updated successfully!")
            return redirect('lab_cases:lab_list')
    else:
        form = DentalLabForm(instance=lab_to_edit)

    context = {
        'form': form,
        'lab': lab_to_edit,
        'page_title': f'Edit Lab: {lab_to_edit.name}'
    }
    return render(request, 'lab_cases/edit_lab.html', context)

@login_required
# MODIFIED: Restricting lab management to Managers only
@role_required(allowed_roles=['MANAGER'])
def delete_lab_view(request, lab_id):
    """
    This view handles the deletion of an existing dental lab.
    """
    lab_to_delete = get_object_or_404(DentalLab, id=lab_id)

    if request.method == 'POST':
        try:
            lab_to_delete.delete()
            messages.success(request, f"The lab '{lab_to_delete.name}' was deleted successfully.")
            return redirect('lab_cases:lab_list')
        except ProtectedError:
            messages.error(request, 
                f"The lab '{lab_to_delete.name}' cannot be deleted because it is linked to one or more existing lab cases. "
            )
            return redirect('lab_cases:lab_list')

    context = {
        'lab': lab_to_delete,
        'page_title': f'Confirm Delete: {lab_to_delete.name}'
    }
    return render(request, 'lab_cases/lab_confirm_delete.html', context)


@login_required
# MODIFIED: Added role-based security
@role_required(allowed_roles=LAB_ACCESS_ROLES)
def lab_case_list_view(request):
    """
    This view handles displaying a list of all lab cases.
    """
    all_cases = LabCase.objects.all()

    context = {
        'lab_cases_list': all_cases,
        'page_title': 'Lab Cases'
    }
    return render(request, 'lab_cases/lab_case_list.html', context)

@login_required
# MODIFIED: Added role-based security
@role_required(allowed_roles=LAB_ACCESS_ROLES)
def add_lab_case_view(request):
    """
    This view handles the creation of a new lab case.
    """
    if request.method == 'POST':
        form = LabCaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New lab case logged successfully!')
            return redirect('lab_cases:lab_case_list')
    else:
        form = LabCaseForm()

    context = {
        'form': form,
        'page_title': 'Log New Lab Case'
    }
    return render(request, 'lab_cases/add_lab_case.html', context)

@login_required
# MODIFIED: Added role-based security
@role_required(allowed_roles=LAB_ACCESS_ROLES)
def lab_case_detail_view(request, case_id):
    """
    This view displays the details of a single lab case.
    """
    lab_case = get_object_or_404(LabCase, id=case_id)

    context = {
        'case': lab_case,
        'page_title': f"Details for Lab Case: {lab_case.case_type} for {lab_case.patient.name}"
    }
    return render(request, 'lab_cases/lab_case_detail.html', context)

@login_required
# MODIFIED: Added role-based security
@role_required(allowed_roles=LAB_ACCESS_ROLES)
def edit_lab_case_view(request, case_id):
    """
    This view handles editing an existing lab case.
    """
    case_to_edit = get_object_or_404(LabCase, id=case_id)

    if request.method == 'POST':
        form = LabCaseForm(request.POST, instance=case_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lab case updated successfully!')
            return redirect('lab_cases:lab_case_detail', case_id=case_to_edit.id)
    else:
        form = LabCaseForm(instance=case_to_edit)

    context = {
        'form': form,
        'case': case_to_edit,
        'page_title': f'Edit Lab Case for {case_to_edit.patient.name}'
    }
    return render(request, 'lab_cases/edit_lab_case.html', context)

@login_required
# MODIFIED: Added role-based security (Only Managers can delete)
@role_required(allowed_roles=['MANAGER'])
def delete_lab_case_view(request, case_id):
    """
    This view handles the deletion of an existing lab case.
    """
    case_to_delete = get_object_or_404(LabCase, id=case_id)

    if request.method == 'POST':
        case_to_delete.delete()
        messages.success(request, "The lab case was deleted successfully.")
        return redirect('lab_cases:lab_case_list')
    
    context = {
        'case': case_to_delete,
        'page_title': f'Confirm Delete Lab Case for {case_to_delete.patient.name}'
    }
    return render(request, 'lab_cases/lab_case_confirm_delete.html', context)