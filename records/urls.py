from django.urls import path
from .views import RegisterPatientView, CreateRecordView, ViewRecordsView, UpdateRecordView, DeleteRecordView, patient_portal_view
from appointments import views
urlpatterns = [
    path('register-patient/', RegisterPatientView.as_view(), name='register-patient'),
    path('create-record/', CreateRecordView.as_view(), name='create-record'),
    path('view-records/<int:patient_id>/', ViewRecordsView.as_view(), name='view-records'),
    path('update-record/<int:id>/', UpdateRecordView.as_view(), name='update-record'),
    path('delete-record/<int:id>/', DeleteRecordView.as_view(), name='delete-record'),
    path('patient-portal/', patient_portal_view, name='patient-portal'),
    path('book/', views.book_appointment, name='book-appointment'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule-appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel-appointment'),
]
