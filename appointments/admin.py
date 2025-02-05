from django.contrib import admin
from .models import Doctor, Appointment, Availability
from django import forms
from django.core.exceptions import ValidationError
from .serializers import AppointmentSerializer

# Register Doctor model
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialization', 'contact')

    # Custom method to show the doctor's full name
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.admin_order_field = 'user__first_name'  # Allows sorting by first name
    get_full_name.short_description = 'Doctor Name'


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'

class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentForm
    list_display = ('patient', 'doctor', 'appointment_date', 'is_confirmed')

    # Optional: format appointment_date to a readable format
    def appointment_date(self, obj):
        return obj.appointment_date.strftime('%Y-%m-%d')
    appointment_date.admin_order_field = 'appointment_date'
    appointment_date.short_description = 'Appointment Date'


# Register Appointment model with the custom form
@admin.register(Appointment)
class AppointmentAdmin(AppointmentAdmin):
    pass


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time')
    list_filter = ('doctor', 'date')
