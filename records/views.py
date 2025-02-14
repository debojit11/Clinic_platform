from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework import generics, permissions
from .models import Patient, MedicalRecord
from appointments.models import Appointment
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
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


def patient_portal_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'patient'):
        return redirect('signin')

    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient)
    medical_records = MedicalRecord.objects.filter(patient=patient)

    if request.method == 'POST':
        if 'update_details' in request.POST:
            details_form = PatientDetailsForm(request.POST, instance=patient)
            if details_form.is_valid():
                details_form.save()
                messages.success(request, 'Personal details updated successfully!')
                return redirect('patient-portal')
    else:
        details_form = PatientDetailsForm(instance=patient)

    return render(request, 'records/patient_portal.html', {
        'patient': patient,
        'appointments': appointments,
        'medical_records': medical_records,
        'details_form': details_form,
    })