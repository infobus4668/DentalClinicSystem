# DENTALCLINICSYSTEM/patients/tests.py

from django.test import TestCase
from .models import Patient
from datetime import date, timedelta
from phonenumber_field.phonenumber import PhoneNumber

class PatientModelTest(TestCase):

    def test_age_calculation(self):
        """
        Tests the age property of the Patient model.
        """
        birth_date = date.today() - timedelta(days=365.25 * 20)
        # Updated to include the required contact_number field
        patient = Patient.objects.create(
            name="Test Age",
            date_of_birth=birth_date,
            gender='M',
            contact_number=PhoneNumber.from_string('+919876543210')
        )
        self.assertEqual(patient.age, 20)

    def test_create_full_patient_profile(self):
        """
        Tests creating a patient with a simple 'place' field.
        """
        patient = Patient.objects.create(
            name="Priya Sharma",
            date_of_birth=date(1995, 8, 22),
            gender='F',
            contact_number=PhoneNumber.from_string('+919988776655'),
            place="Mumbai",
            pincode="400001"
        )
        
        saved_patient = Patient.objects.get(pk=patient.pk) # Normalized to pk
        
        self.assertEqual(saved_patient.name, "Priya Sharma")
        self.assertEqual(str(saved_patient.contact_number), "+919988776655")
        self.assertEqual(saved_patient.place, "Mumbai")
        self.assertEqual(saved_patient.pincode, "400001")