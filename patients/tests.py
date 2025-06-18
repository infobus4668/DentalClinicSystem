# DENTALCLINICSYSTEM/patients/tests.py

from django.test import TestCase
from .models import Patient
from datetime import date, timedelta

class PatientModelTest(TestCase):

    def test_age_calculation(self):
        """
        Tests the age property of the Patient model.
        """
        # Create a birth date for someone who is exactly 20 years old
        birth_date = date.today() - timedelta(days=365.25 * 20) 
        patient = Patient.objects.create(name="Test Age", date_of_birth=birth_date)
        
        # Check if the age property returns the correct age
        self.assertEqual(patient.age, 20)