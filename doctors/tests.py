# DENTALCLINICSYSTEM/doctors/tests.py

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Doctor
from patients.models import Patient
from appointments.models import Appointment

class DoctorModelTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(name="Test Patient", date_of_birth="1990-01-01")

    def test_cannot_delete_doctor_with_appointment(self):
        """
        Verify that a doctor with a linked appointment cannot be deleted.
        """
        doctor = Doctor.objects.create(name="Protected Doctor", specialization="Surgeon")
        Appointment.objects.create(
            patient=self.patient,
            doctor=doctor,
            appointment_datetime=timezone.now()
        )

        delete_url = reverse('doctors:delete_doctor', args=[doctor.id])
        self.client.post(delete_url, follow=True)

        self.assertTrue(Doctor.objects.filter(id=doctor.id).exists())