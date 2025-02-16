from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, permissions
from django.utils.timezone import make_aware
from .models import Appointment, Doctor, Availability
from records.models import MedicalRecord
from .serializers import AppointmentSerializer, DoctorSerializer, AvailabilitySerializer
from django.db import transaction
from django.contrib import messages
from datetime import timedelta
from django.core.exceptions import ValidationError
from .tasks import send_appointment_reminder  # For notifications
from django.contrib.auth.decorators import login_required
from .forms import AvailabilityForm, AppointmentForm, MedicalRecordForm

class AppointmentListCreateView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get the selected availability slot
        availability = serializer.validated_data['availability']

        # Check if the time slot is already booked
        overlapping_appointment = Appointment.objects.filter(
            doctor=availability.doctor,
            availability=availability
        ).exists()

        if overlapping_appointment:
            raise ValidationError('This time slot is already booked.')

        # Save the appointment
        serializer.save()


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        appointment = serializer.save()

        # Re-check availability for the new time slot
        appointment_start = appointment.appointment_date
        appointment_end = appointment_start + timedelta(minutes=appointment.duration_minutes)

        availability = Availability.objects.filter(
            doctor=appointment.doctor,
            start_time__lte=appointment_start,
            end_time__gte=appointment_end
        ).first()

        if not availability:
            raise ValidationError('The new time slot is not available.')

        # Check for overlapping appointments
        overlapping_appointment = Appointment.objects.filter(
            doctor=appointment.doctor,
            appointment_date__lt=appointment_end,
            appointment_date__gte=appointment_start
        ).exclude(id=appointment.id).exists()

        if overlapping_appointment:
            raise ValidationError('This time slot is already booked.')

        # Send reminder after successful update
        send_appointment_reminder.apply_async(args=[appointment.id], countdown=60)


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

class AvailabilityListView(generics.ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

def doctor_portal_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'doctor'):
        return redirect('signin')

    doctor = request.user.doctor
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')
    availability_slots = Availability.objects.filter(doctor=doctor)
    medical_records = MedicalRecord.objects.filter(patient__appointment__doctor=doctor).distinct()

    if request.method == 'POST':
        if 'add_availability' in request.POST:
            availability_form = AvailabilityForm(request.POST)
            if availability_form.is_valid():
                availability = availability_form.save(commit=False)
                availability.doctor = doctor
                availability.save()
                return redirect('doctor-portal')

        elif 'delete_availability' in request.POST:
            availability_id = request.POST.get('availability_id')
            Availability.objects.filter(id=availability_id, doctor=doctor).delete()
            return redirect('doctor-portal')

        elif 'confirm_appointment' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
            appointment.is_confirmed = True
            appointment.save()
            return redirect('doctor-portal')

        elif 'delete_medical_record' in request.POST:
            record_id = request.POST.get('record_id')
            MedicalRecord.objects.filter(id=record_id).delete()
            return redirect('doctor-portal')

        elif 'update_medical_record' in request.POST:
            record_id = request.POST.get('record_id')
            medical_record = MedicalRecord.objects.get(id=record_id)
            form = MedicalRecordForm(request.POST, instance=medical_record, doctor=doctor)
            if form.is_valid():
                form.save()
            return redirect('doctor-portal')

        elif 'add_medical_record' in request.POST:
            medical_record_form = MedicalRecordForm(request.POST, doctor=doctor)
            if medical_record_form.is_valid():
                medical_record_form.save()
                return redirect('doctor-portal')

    else:
        availability_form = AvailabilityForm()
        medical_record_form = MedicalRecordForm(doctor=doctor)

    return render(request, 'appointments/doctor_portal.html', {
        'doctor': doctor,
        'appointments': appointments,
        'availability_slots': availability_slots,
        'availability_form': availability_form,
        'medical_record_form': medical_record_form,
        'medical_records': medical_records,
    })


@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient
            appointment.appointment_date = form.cleaned_data['availability'].date
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('patient-portal')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {
        'form': form,
    })


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment rescheduled successfully!')
            return redirect('patient-portal')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointments/reschedule_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment canceled successfully!')
    return redirect('patient-portal')