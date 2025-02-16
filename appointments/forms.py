from django import forms
from .models import Availability, Appointment, Doctor
from records.models import MedicalRecord, Patient 

class AvailabilityForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=True)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=True)

    class Meta:
        model = Availability
        fields = ['date', 'start_time', 'end_time']


class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    availability = forms.ModelChoiceField(queryset=Availability.objects.none(), required=True)

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'availability', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                self.fields['availability'].queryset = Availability.objects.filter(
                    doctor_id=doctor_id,
                    date=self.data.get('date')
                )
            except (ValueError, TypeError):
                pass

class MedicalRecordForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    class Meta:
        model = MedicalRecord
        fields = ['patient', 'date', 'diagnosis', 'treatment', 'doctor_notes']

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if doctor:
            # Filter patients who have had appointments with this doctor
            self.fields['patient'].queryset = Patient.objects.filter(appointment__doctor=doctor).distinct()