from django import forms
from datetime import datetime
from django.utils import timezone
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

        # Get the current time with timezone aware datetime
        current_datetime = timezone.now()

        if 'doctor' in self.data and 'date' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                selected_date = self.data.get('date')

                # Filter available slots for doctor and date greater than current time
                # Assuming start_time is a DateTime field on the Availability model
                self.fields['availability'].queryset = Availability.objects.filter(
                    doctor_id=doctor_id,
                    date=selected_date,
                    start_time__gt=current_datetime  # Filter slots after current time
                ).exclude(
                    appointment__isnull=False  # Exclude already booked slots (not canceled)
                )

            except (ValueError, TypeError) as e:
                print("Error:", e)
                self.fields['availability'].queryset = Availability.objects.none()

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

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'contact']

    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        doctor = super().save(commit=False)

        # Save first_name, last_name, and email to the associated User model
        user = doctor.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            doctor.save()

        return doctor
