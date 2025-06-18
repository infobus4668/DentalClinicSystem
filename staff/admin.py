from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StaffMember
# We need to import the DoctorProfileInline from the doctors app's admin file
from doctors.admin import DoctorProfileInline

# Define an inline admin descriptor for StaffMember model
# This will be used in the new CustomUserAdmin
class StaffProfileInline(admin.StackedInline):
    model = StaffMember
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'
    # Specify fields to show in the inline form
    fields = ('name', 'role', 'contact_number', 'email', 'date_joined', 'is_active', 'notes')

# Define a new User admin that includes our profile inlines
class CustomUserAdmin(BaseUserAdmin):
    # Add both profile inlines to the user change page
    inlines = (StaffProfileInline, DoctorProfileInline) 

    # Customize the User list display to show the person's clinic role
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_role')

    def get_user_role(self, instance):
        """A custom method to get the user's role from their linked profile."""
        if hasattr(instance, 'doctor_profile'):
            return "Doctor"
        if hasattr(instance, 'staff_profile'):
            # Uses the get_role_display() method from your StaffMember model
            return instance.staff_profile.get_role_display()
        return "N/A"
    get_user_role.short_description = 'Clinic Role' # Sets the column header text

    # This method prevents the inlines from showing up on the "Add user" page,
    # as you must create a user before you can add a profile to them.
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Re-register UserAdmin with our custom class
admin.site.unregister(User) # First, unregister the default User admin
admin.site.register(User, CustomUserAdmin) # Then, register the User model with our custom admin

# --- This is your existing admin for the separate Staff Member list ---
# I've added 'user' to the list_display and search_fields for better usability.
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_role_display', 'contact_number', 'email', 'is_active', 'user')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('name', 'email', 'contact_number', 'notes', 'user__username')
    list_editable = ('is_active',)
    list_per_page = 20
    raw_id_fields = ('user',) # Use a search popup for the user field

admin.site.register(StaffMember, StaffMemberAdmin)