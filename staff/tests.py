# staff/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import StaffMember
from doctors.models import Doctor
from .forms import StaffMemberForm

class StaffFormTest(TestCase):
    """
    FIX: This test class now directly tests the StaffMemberForm logic
    to ensure the user dropdown is filtered correctly.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        cls.user_for_staff1 = User.objects.create_user('staffuser1', 'staff1@example.com', 'password')
        cls.user_for_doctor = User.objects.create_user('doctoruser', 'doctor@example.com', 'password')
        cls.unassigned_user = User.objects.create_user('unassigned', 'unassigned@example.com', 'password')
        
        cls.staff_member1 = StaffMember.objects.create(user=cls.user_for_staff1, name="Existing Staff")
        cls.doctor = Doctor.objects.create(user=cls.user_for_doctor, name="Existing Doctor", contact_number="+911234567890")

    def test_new_staff_member_form_filters_users(self):
        """
        Test that the form for a NEW staff member correctly filters the user list.
        It should only show users who are not superusers and not linked to any profile.
        """
        # Instantiate the form for creating a new object
        form = StaffMemberForm()
        user_field_queryset = form.fields['user'].queryset
        
        # Check that ONLY the unassigned user is available.
        self.assertIn(self.unassigned_user, user_field_queryset)
        self.assertEqual(user_field_queryset.count(), 1)

        # Verify that all other users are correctly excluded.
        self.assertNotIn(self.admin_user, user_field_queryset)
        self.assertNotIn(self.user_for_staff1, user_field_queryset)
        self.assertNotIn(self.user_for_doctor, user_field_queryset)

    def test_edit_staff_member_form_filters_users(self):
        """
        Test that the form for EDITING a staff member correctly filters the user list.
        It should show unassigned users AND the user currently assigned to the instance.
        """
        # Instantiate the form for editing our existing staff member
        form = StaffMemberForm(instance=self.staff_member1)
        user_field_queryset = form.fields['user'].queryset

        # It should contain the user of the instance being edited.
        self.assertIn(self.user_for_staff1, user_field_queryset)
        # It should also contain any unassigned users.
        self.assertIn(self.unassigned_user, user_field_queryset)
        # Check the total count is correct.
        self.assertEqual(user_field_queryset.count(), 2)

        # It should NOT contain the superuser or users assigned to other profiles.
        self.assertNotIn(self.admin_user, user_field_queryset)
        self.assertNotIn(self.user_for_doctor, user_field_queryset)