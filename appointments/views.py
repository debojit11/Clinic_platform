from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Appointment, Doctor, Availability
from records.models import MedicalRecord
from .serializers import AppointmentSerializer, DoctorSerializer, AvailabilitySerializer
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from .tasks import send_appointment_reminder  # For notifications
from django.contrib.auth.decorators import login_required
from .forms import AvailabilityForm, AppointmentForm, MedicalRecordForm, DoctorForm

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
        appointment = serializer.save()

        # Call the Celery task to send the appointment reminder email
        send_appointment_reminder.delay(appointment.id)

    def create(self, request, *args, **kwargs):
        # Custom response logic to handle validation errors gracefully
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        appointment = serializer.save()

        # Get the new appointment start and end time from selected availability
        availability = appointment.availability
        appointment_start = datetime.combine(availability.date, availability.start_time)
        appointment_end = datetime.combine(availability.date, availability.end_time)

        # Check if the selected time slot is available
        if not self.is_availability_available(appointment.doctor, appointment_start, appointment_end):
            raise ValidationError('The selected time slot is no longer available.')

        # Check for overlapping appointments for the doctor
        if self.is_overlapping_appointment(appointment.doctor, appointment_start, appointment_end, appointment.id):
            raise ValidationError('This time slot is already booked.')

        # Send reminder after successful update
        send_appointment_reminder.apply_async(args=[appointment.id], countdown=60)

    def is_availability_available(self, doctor, start_time, end_time):
        """Check if the availability is still valid for the doctor at the given time."""
        availability = Availability.objects.filter(
            doctor=doctor,
            date=start_time.date(),
            start_time__lte=start_time.time(),
            end_time__gte=end_time.time()
        ).first()

        return availability is not None

    def is_overlapping_appointment(self, doctor, start_time, end_time, appointment_id):
        """Check if there are any overlapping appointments for the doctor."""
        overlapping_appointment = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=start_time.date(),
            appointment_date__lt=end_time,
            appointment_date__gte=start_time
        ).exclude(id=appointment_id).exists()

        return overlapping_appointment


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

    availability_form = AvailabilityForm()
    medical_record_form = MedicalRecordForm(doctor=doctor)
    details_form = DoctorForm(instance=doctor)

    if request.method == 'POST':
        if 'update_details' in request.POST:
            details_form = DoctorForm(request.POST, instance=doctor)
            if details_form.is_valid():
                details_form.save()

                # Update email if provided
                email = request.POST.get('email', doctor.user.email)
                doctor.user.email = email
                doctor.user.save()

                messages.success(request, 'Personal details updated successfully!')
                return redirect('doctor-portal')

        elif 'add_availability' in request.POST:
            availability_form = AvailabilityForm(request.POST)
            if availability_form.is_valid():
                availability = availability_form.save(commit=False)
                availability.doctor = doctor
                availability.save()
                messages.success(request, 'Availability slot added successfully!')
                return redirect('doctor-portal')

        elif 'delete_availability' in request.POST:
            availability_id = request.POST.get('availability_id')
            Availability.objects.filter(id=availability_id, doctor=doctor).delete()
            messages.success(request, 'Availability slot deleted successfully!')
            return redirect('doctor-portal')

        elif 'confirm_appointment' in request.POST:
            appointment_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
            appointment.is_confirmed = True
            appointment.save()
            messages.success(request, 'Appointment confirmed!')
            return redirect('doctor-portal')

        elif 'delete_medical_record' in request.POST:
            record_id = request.POST.get('record_id')
            MedicalRecord.objects.filter(id=record_id).delete()
            messages.success(request, 'Medical record deleted successfully!')
            return redirect('doctor-portal')

        elif 'update_medical_record' in request.POST:
            record_id = request.POST.get('record_id')
            medical_record = MedicalRecord.objects.get(id=record_id)
            form = MedicalRecordForm(request.POST, instance=medical_record, doctor=doctor)
            if form.is_valid():
                form.save()
            messages.success(request, 'Medical record updated successfully!')
            return redirect('doctor-portal')

        elif 'add_medical_record' in request.POST:
            medical_record_form = MedicalRecordForm(request.POST, doctor=doctor)
            if medical_record_form.is_valid():
                medical_record_form.save()
                messages.success(request, 'Medical record added successfully!')
                return redirect('doctor-portal')

    # Filter availability and appointments to show only future ones
    current_date = timezone.now().date()

    appointments = Appointment.objects.filter(doctor=doctor, appointment_date__gte=current_date).select_related('patient')
    availability_slots = Availability.objects.filter(doctor=doctor, date__gte=current_date)
    medical_records = MedicalRecord.objects.filter(patient__appointment__doctor=doctor).distinct()

    return render(request, 'appointments/doctor_portal.html', {
        'doctor': doctor,
        'appointments': appointments,
        'availability_slots': availability_slots,
        'availability_form': availability_form,
        'medical_record_form': medical_record_form,
        'medical_records': medical_records,
        'details_form': details_form,
    })


@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            selected_slot = form.cleaned_data['availability']
            
            if Appointment.objects.filter(availability=selected_slot, canceled=False).exists():
                form.add_error('availability', 'This slot is already booked. Please choose another one.')
            else:
                appointment = form.save(commit=False)
                appointment.patient = request.user.patient
                appointment.appointment_date = form.cleaned_data['availability'].date
                appointment.save()

                # Call the Celery task to send the appointment reminder
                send_appointment_reminder.delay(appointment.id)

                messages.success(request, 'Appointment booked successfully!')
                return redirect('patient-portal')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            # Save the form and update appointment
            updated_appointment = form.save()

            # Trigger the Celery task to send an email reminder
            send_appointment_reminder.apply_async(args=[updated_appointment.id])

            messages.success(request, 'Appointment rescheduled successfully!')
            return redirect('patient-portal')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/reschedule_appointment.html', {
        'form': form,
        'appointment': appointment
    })

@login_required
def cancel_appointment(request, appointment_id):
    print(f"Cancel appointment called for ID: {appointment_id}")  # Debugging print
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    print(f"Appointment before delete: {appointment}")  # Debugging appointment details
    
    if request.method == 'POST':
        appointment.delete()
        print(f"Appointment with ID {appointment_id} deleted")  # Debugging post-delete action
        messages.success(request, 'Appointment canceled successfully!')
        return redirect('patient-portal')

    # Render confirmation if not POST
    return render(request, 'appointments/cancel_appointment.html', {'appointment': appointment})

def get_available_slots(request):
    doctor_id = request.GET.get('doctor')
    date = request.GET.get('date')

    if doctor_id and date:
        current_time = timezone.now()

        # Fetch available slots greater than the current time
        available_slots = Availability.objects.filter(doctor_id=doctor_id, date=date, start_time__gt=current_time)

        # Exclude slots that are already booked and not canceled
        booked_slots = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date,
            canceled=False
        ).values_list('availability_id', flat=True)

        # Exclude booked slots from available slots
        available_slots = available_slots.exclude(id__in=booked_slots)

        slot_data = [{'id': slot.id, 'text': f"{slot.start_time} - {slot.end_time}"} for slot in available_slots]

        return JsonResponse({'slots': slot_data})

    return JsonResponse({'slots': []})