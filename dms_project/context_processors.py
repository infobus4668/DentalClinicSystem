# dms_project/context_processors.py

def clinic_details(request):
    """
    Adds clinic contact information to the context of all templates.
    """
    return {
        'CLINIC_NAME': 'Babu Dental Clinic',
        'CLINIC_ADDRESS': 'Beach Road, Kadapakkam, Cheyyur Taluk, Chengalpattu District, Tamilnadu - 603304',
        'CLINIC_PHONE': '04427526041',
        'CLINIC_EMAIL': 'drbdcdental@gmail.com'
    }

# FIX: Added the user_roles_processor to define role-based variables for all templates.
def user_roles_processor(request):
    """
    Determines user roles correctly and adds them to the template context.
    This makes 'is_manager', 'is_doctor', and 'is_receptionist'
    booleans available in all templates for display logic.
    """
    if not request.user.is_authenticated:
        return {}
    
    # Default all roles to False
    is_manager = False
    is_doctor = False
    is_receptionist = False

    # A superuser has all roles, regardless of profiles
    if request.user.is_superuser:
        is_manager = True
        is_doctor = True
        is_receptionist = True
    else:
        # Use separate 'if' statements to handle users who might have multiple roles 
        # (e.g., a doctor who is also a manager).

        # Check for staff roles.
        if hasattr(request.user, 'staff_profile') and request.user.staff_profile:
            role = request.user.staff_profile.role
            if role == 'MANAGER':
                is_manager = True
            if role == 'RECEP':
                is_receptionist = True
        
        # Separately, check for a doctor profile.
        if hasattr(request.user, 'doctor_profile') and request.user.doctor_profile:
            is_doctor = True
            
    return {
        'is_manager': is_manager,
        'is_doctor': is_doctor,
        'is_receptionist': is_receptionist,
    }