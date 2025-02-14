from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView, DoctorListView, AvailabilityListView, doctor_portal_view, book_appointment, reschedule_appointment, cancel_appointment

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('availability/', AvailabilityListView.as_view(), name='availability-list'),
    path('doctor-portal/', doctor_portal_view, name='doctor-portal'),
    path('book/<int:availability_id>/', book_appointment, name='book-appointment'),
    path('reschedule/<int:appointment_id>/', reschedule_appointment, name='reschedule-appointment'),
    path('cancel/<int:appointment_id>/', cancel_appointment, name='cancel-appointment'),
]
