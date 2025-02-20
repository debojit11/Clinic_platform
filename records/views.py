from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework import generics, permissions
from .models import Patient, MedicalRecord
from appointments.models import Appointment, Availability
from .serializers import PatientSerializer, MedicalRecordSerializer
from django.contrib.auth.decorators import login_required
from .forms import PatientDetailsForm, MedicalRecordForm

# Register a new patient
class RegisterPatientView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]  # JWT protected


# Create a new medical record linked to a patient
class CreateRecordView(generics.CreateAPIView):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


# Retrieve all records for a specific patient
class ViewRecordsView(generics.ListAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return MedicalRecord.objects.filter(patient_id=patient_id)


# Update an existing medical record
class UpdateRecordView(generics.UpdateAPIView):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


# Delete a medical record
class DeleteRecordView(generics.DestroyAPIView):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


def patient_portal_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'patient'):
        return redirect('signin')

    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient)
    medical_records = MedicalRecord.objects.filter(patient=patient)

    # Initialize the form with the patient's details
    details_form = PatientDetailsForm(instance=patient)

    # Ensure the form's email field is populated with the user's email from the User model
    if not details_form.instance.user.email:
        details_form.instance.user.email = request.user.email

    if request.method == 'POST':
        if 'update_details' in request.POST:
            details_form = PatientDetailsForm(request.POST, instance=patient)
            if details_form.is_valid():
                # Save the patient's details
                patient = details_form.save()

                # Manually update the User's related fields if they were modified
                if 'email' in details_form.cleaned_data:
                    request.user.email = details_form.cleaned_data['email']
                if 'first_name' in details_form.cleaned_data:
                    request.user.first_name = details_form.cleaned_data['first_name']
                if 'last_name' in details_form.cleaned_data:
                    request.user.last_name = details_form.cleaned_data['last_name']

                request.user.save()

                messages.success(request, 'Personal details updated successfully!')
                return redirect('patient-portal')

    return render(request, 'records/patient_portal.html', {
        'patient': patient,
        'appointments': appointments,
        'medical_records': medical_records,
        'details_form': details_form,
    })
