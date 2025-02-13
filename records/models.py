from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')  # Linked to a user
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    contact = models.CharField(max_length=15, null=True, blank=True)
    medical_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records')
    date_created = models.DateTimeField(auto_now_add=True)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    doctor_notes = models.TextField()

    def __str__(self):
        return f'Record for {self.patient.name} - {self.date_created}'
