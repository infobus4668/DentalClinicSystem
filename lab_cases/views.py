# DENTALCLINICSYSTEM/lab_cases/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.contrib import messages
from .models import DentalLab, LabCase
from .forms import DentalLabForm, LabCaseForm

@login_required
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

# --- New view for adding a dental lab ---
@login_required
def add_lab_view(request):
    """
    This view handles the creation of a new dental lab.
    """
    if request.method == 'POST':
        form = DentalLabForm(request.POST)
        if form.is_valid():
            form.save() # Saves the new dental lab to the database
            # Optionally, add a success message
            # messages.success(request, 'New dental lab added successfully!')
            return redirect('lab_cases:lab_list') # Redirect to the lab list page
    else:
        form = DentalLabForm() # An unbound form for a GET request

    context = {
        'form': form,
        'page_title': 'Add New Dental Lab'
    }
    return render(request, 'lab_cases/add_lab.html', context)

@login_required
def edit_lab_view(request, lab_id):
    """
    This view handles editing an existing dental lab.
    """
    lab_to_edit = get_object_or_404(DentalLab, id=lab_id)

    if request.method == 'POST':
        # Initialize the form with submitted data AND the instance of the lab being edited
        form = DentalLabForm(request.POST, instance=lab_to_edit)
        if form.is_valid():
            form.save() # Saves changes to the existing lab object
            # messages.success(request, f"'{lab_to_edit.name}' updated successfully!")
            return redirect('lab_cases:lab_list') # Redirect back to the list
    else:
        # For a GET request, pre-fill the form with the lab's current data
        form = DentalLabForm(instance=lab_to_edit)

    context = {
        'form': form,
        'lab': lab_to_edit, # Pass the lab object for context in the template
        'page_title': f'Edit Lab: {lab_to_edit.name}'
    }
    return render(request, 'lab_cases/edit_lab.html', context)

@login_required
def delete_lab_view(request, lab_id):
    """
    This view handles the deletion of an existing dental lab,
    with a check for protected foreign keys.
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
                "Please reassign or delete those cases first."
            )
            return redirect('lab_cases:lab_list') # Redirect back to the list

    # For a GET request, show the confirmation page
    context = {
        'lab': lab_to_delete,
        'page_title': f'Confirm Delete: {lab_to_delete.name}'
    }
    return render(request, 'lab_cases/lab_confirm_delete.html', context)

@login_required
def lab_case_list_view(request):
    """
    This view handles displaying a list of all lab cases.
    """
    # Fetch all LabCase objects, using the default ordering from the model's Meta class
    all_cases = LabCase.objects.all()

    context = {
        'lab_cases_list': all_cases,
        'page_title': 'Lab Cases'
    }
    # We will create this template in the next step
    return render(request, 'lab_cases/lab_case_list.html', context)

@login_required
def add_lab_case_view(request):
    """
    This view handles the creation of a new lab case.
    """
    if request.method == 'POST':
        form = LabCaseForm(request.POST)
        if form.is_valid():
            form.save() # Saves the new lab case to the database
            messages.success(request, 'New lab case logged successfully!')
            return redirect('lab_cases:lab_case_list') # Redirect to the lab case list page
    else:
        form = LabCaseForm() # An unbound form for a GET request

    context = {
        'form': form,
        'page_title': 'Log New Lab Case'
    }
    return render(request, 'lab_cases/add_lab_case.html', context)

@login_required
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
def edit_lab_case_view(request, case_id):
    """
    This view handles editing an existing lab case.
    """
    case_to_edit = get_object_or_404(LabCase, id=case_id)

    if request.method == 'POST':
        # Initialize the form with submitted data AND the instance of the case being edited
        form = LabCaseForm(request.POST, instance=case_to_edit)
        if form.is_valid():
            form.save() # Saves changes to the existing lab case object
            messages.success(request, 'Lab case updated successfully!')
            return redirect('lab_cases:lab_case_detail', case_id=case_to_edit.id) # Redirect back to the detail page
    else:
        # For a GET request, pre-fill the form with the case's current data
        form = LabCaseForm(instance=case_to_edit)

    context = {
        'form': form,
        'case': case_to_edit, # Pass the case object for context in the template
        'page_title': f'Edit Lab Case for {case_to_edit.patient.name}'
    }
    return render(request, 'lab_cases/edit_lab_case.html', context)

@login_required
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


