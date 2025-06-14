# DENTALCLINICSYSTEM/staff/decorators.py

from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator for views that checks that the user is logged in and has
    one of the roles specified in allowed_roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # The @login_required decorator should handle unauthenticated users first.

            user_role = None

            # Use a try-except block for a more reliable way to check for related profiles.
            try:
                # Check for a staff profile first
                if request.user.staff_profile:
                    user_role = request.user.staff_profile.role
            except AttributeError:
                # If staff_profile doesn't exist, check for doctor_profile
                try:
                    if request.user.doctor_profile:
                        user_role = 'DOCTOR'
                except AttributeError:
                    # User has neither a staff nor a doctor profile linked
                    user_role = None

            if user_role not in allowed_roles:
                raise PermissionDenied(
                    f"You do not have permission to view this page. "
                    f"Your determined role is: '{user_role}'. "
                    f"Allowed roles for this page are: {allowed_roles}."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator