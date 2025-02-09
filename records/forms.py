from django import forms
from .models import Patient, MedicalRecord

class PatientDetailsForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender']

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'doctor_notes']