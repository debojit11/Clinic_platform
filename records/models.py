from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')  # Linked to a user
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True, max_length=10)
    contact = models.CharField(max_length=15, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    def save(self, *args, **kwargs):
        if not self.email:
            self.email = self.user.email  # Populate the email from User model if empty
        super().save(*args, **kwargs)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records')
    date_created = models.DateTimeField(auto_now_add=True)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    doctor_notes = models.TextField()

    def __str__(self):
        return f'Record for {self.patient.first_name} {self.patient.last_name} - {self.date_created}'
