from rest_framework import generics, permissions
from .models import Patient, MedicalRecord
from .serializers import PatientSerializer, MedicalRecordSerializer

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
