from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView, DoctorListView, AvailabilityListView

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('availability/', AvailabilityListView.as_view(), name='availability-list'),
]
