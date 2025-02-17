from django.db import models
from django.contrib.auth.models import User
from records.models import Patient
from datetime import datetime, timedelta

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    specialization = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)

    def __str__(self):
        return f'Dr. {self.user.get_full_name()} - {self.specialization}'

class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def generate_slots(self):
        """Generate 30-minute slots based on availability."""
        slots = []
        current_time = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)

        while current_time + timedelta(minutes=30) <= end_datetime:
            slots.append({
                'start_time': current_time.time(),
                'end_time': (current_time + timedelta(minutes=30)).time()
            })
            current_time += timedelta(minutes=30)

        return slots

    def __str__(self):
        return f'{self.doctor.first_name} - {self.date} from {self.start_time} to {self.end_time}'

    

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f'Appointment with {self.doctor} on {self.appointment_date}'
