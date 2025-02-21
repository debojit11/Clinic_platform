from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView, DoctorListView, AvailabilityListView, doctor_portal_view, get_available_slots

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('availability/', AvailabilityListView.as_view(), name='availability-list'),
    path('doctor-portal/', doctor_portal_view, name='doctor-portal'),
    path('get-available-slots/', get_available_slots, name='get_available_slots'),
]
