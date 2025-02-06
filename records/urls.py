from django.urls import path
from .views import RegisterPatientView, CreateRecordView, ViewRecordsView, UpdateRecordView, DeleteRecordView, patient_portal_view

urlpatterns = [
    path('register-patient/', RegisterPatientView.as_view(), name='register-patient'),
    path('create-record/', CreateRecordView.as_view(), name='create-record'),
    path('view-records/<int:patient_id>/', ViewRecordsView.as_view(), name='view-records'),
    path('update-record/<int:id>/', UpdateRecordView.as_view(), name='update-record'),
    path('delete-record/<int:id>/', DeleteRecordView.as_view(), name='delete-record'),
    path('patient-portal/', patient_portal_view, name='patient-portal'),
]
