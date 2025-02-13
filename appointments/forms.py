from django import forms
from .models import Availability, Appointment

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['date', 'start_time', 'end_time']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'availability', 'reason']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                self.fields['availability'].queryset = Availability.objects.filter(doctor_id=doctor_id, is_booked=False)
            except (ValueError, TypeError):
                self.fields['availability'].queryset = Availability.objects.none()
        elif self.instance.pk:
            self.fields['availability'].queryset = self.instance.doctor.availability_set.filter(is_booked=False)