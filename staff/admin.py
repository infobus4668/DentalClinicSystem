# staff/admin.py

from django.contrib import admin
from .models import StaffMember
# FIX: Import the custom StaffMemberForm from your forms.py file
from .forms import StaffMemberForm

class StaffMemberAdmin(admin.ModelAdmin):
    # FIX: Tell the admin to use our intelligent form instead of the default one.
    form = StaffMemberForm
    
    # These are your existing display preferences, which are good.
    list_display = ('name', 'role', 'contact_number', 'email', 'currently_employed', 'date_joined')
    list_filter = ('role', 'currently_employed')
    search_fields = ('name', 'email', 'contact_number', 'notes', 'user__username')
    list_editable = ('currently_employed',)
    list_per_page = 20

# We are re-registering the model with the updated admin class
admin.site.register(StaffMember, StaffMemberAdmin)