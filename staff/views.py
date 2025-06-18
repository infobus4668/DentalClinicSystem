# dental_clinic/staff/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import StaffMember
from .forms import StaffMemberForm
# --- NEW: IMPORT THE DECORATOR ---
from .decorators import role_required

# View for listing all staff members
@login_required
@role_required(allowed_roles=['MANAGER'])
def staff_list_view(request):
    all_staff_members = StaffMember.objects.all().order_by('name')
    context = {
        'staff_members_list': all_staff_members,
        'page_title': 'Clinic Staff Members'
    }
    return render(request, 'staff/staff_list.html', context)

# View for adding a new staff member
@login_required
@role_required(allowed_roles=['MANAGER'])
def add_staff_member_view(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff:staff_list')
    else:
        form = StaffMemberForm()
    context = {
        'form': form,
        'page_title': 'Add New Staff Member'
    }
    return render(request, 'staff/add_staff_member.html', context)

# View for a single staff member's details
@login_required
@role_required(allowed_roles=['MANAGER'])
def staff_detail_view(request, staff_member_id):
    staff_member = get_object_or_404(StaffMember, id=staff_member_id)
    context = {
        'staff_member': staff_member,
        'page_title': f"Details for {staff_member.name}"
    }
    return render(request, 'staff/staff_detail.html', context)

# View for editing an existing staff member
@login_required
@role_required(allowed_roles=['MANAGER'])
def edit_staff_member_view(request, staff_member_id):
    staff_member_to_edit = get_object_or_404(StaffMember, id=staff_member_id)

    if request.method == 'POST':
        form = StaffMemberForm(request.POST, instance=staff_member_to_edit)
        if form.is_valid():
            form.save()
            return redirect('staff:staff_detail', staff_member_id=staff_member_to_edit.id)
    else:
        form = StaffMemberForm(instance=staff_member_to_edit)

    context = {
        'form': form,
        'staff_member': staff_member_to_edit,
        'page_title': f"Edit Details for {staff_member_to_edit.name}"
    }
    return render(request, 'staff/edit_staff_member.html', context)

# View for deleting an existing staff member
@login_required
@role_required(allowed_roles=['MANAGER'])
def delete_staff_member_view(request, staff_member_id):
    staff_member_to_delete = get_object_or_404(StaffMember, id=staff_member_id)

    if request.method == 'POST':
        staff_member_to_delete.delete()
        return redirect('staff:staff_list')
    
    context = {
        'staff_member': staff_member_to_delete,
        'page_title': f"Confirm Delete: {staff_member_to_delete.name}"
    }
    return render(request, 'staff/staff_confirm_delete.html', context)