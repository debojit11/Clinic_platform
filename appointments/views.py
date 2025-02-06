from django.shortcuts import render
from rest_framework import generics, permissions
from django.utils.timezone import make_aware
from .models import Appointment, Doctor, Availability
from .serializers import AppointmentSerializer, DoctorSerializer, AvailabilitySerializer
from django.db import transaction
from datetime import timedelta
from django.core.exceptions import ValidationError
from .tasks import send_appointment_reminder  # For notifications

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
    return render(request, 'appointments/doctor_portal.html')