# doctors/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Doctor
from appointments.models import Appointment
from patients.models import Patient
# import datetime # REMOVED: No longer needed for naive datetimes
from django.utils import timezone # ADDED: Import timezone for aware datetimes

class DoctorProfileTestCase(TestCase):
    def setUp(self):
        # 1. Create a user for the doctor
        self.doctor_user = User.objects.create_user(
            username='test_doctor_user', 
            password='testpassword123'
        )

        # 2. Create the corresponding doctor profile
        self.doctor_profile = Doctor.objects.create(
            user=self.doctor_user,
            name="Dr. Smith",
            specialization="GD",
            contact_number="1234567890"
        )
        
        # 3. Create another doctor without a user link, for contrast
        self.other_doctor = Doctor.objects.create(
            name="Dr. Jones",
            specialization="ORTHO",
            contact_number="0987654321"
        )
        
        # 4. Create a patient to create appointments for
        self.patient = Patient.objects.create(
            name="Test Patient",
            contact_number="5555555555",
            date_of_birth=timezone.datetime(1990, 1, 1).date() # Changed datetime.date to timezone.datetime for consistency, then .date()
        )
        
        # 5. Create appointments for both doctors
        self.appointment_for_smith = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_profile,
            appointment_datetime=timezone.now(), # MODIFIED: Use timezone.now() for aware datetime
            reason="Checkup for Dr. Smith"
        )
        self.appointment_for_jones = Appointment.objects.create(
            patient=self.patient,
            doctor=self.other_doctor,
            appointment_datetime=timezone.now(), # MODIFIED: Use timezone.now() for aware datetime
            reason="Checkup for Dr. Jones"
        )

    def test_doctor_can_log_in_and_view_dashboard(self):
        """
        Verify that a user linked to a doctor profile can log in and see the dashboard.
        """
        self.client.login(username='test_doctor_user', password='testpassword123')
        response = self.client.get('/') # Assuming '/' is the dashboard URL
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_doctor_appointment_api_is_filtered(self):
        """
        Verify that the appointments API only returns events for the logged-in doctor.
        """
        self.client.login(username='test_doctor_user', password='testpassword123')
        response = self.client.get(reverse('appointments:appointment_api')) 
        self.assertEqual(response.status_code, 200)
        
        # The response is JSON, so we convert it
        response_data = response.json() 
        
        # There should be exactly one appointment in the response
        self.assertEqual(len(response_data), 1)
        
        # That one appointment should be for Dr. Smith (via its patient's name as per API output)
        self.assertEqual(response_data[0]['title'], 'Test Patient')