from celery import shared_task
from django.core.mail import send_mail
from .models import Appointment

@shared_task
def send_appointment_reminder(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        patient_email = appointment.patient.user.email
        doctor_name = appointment.doctor.user.get_full_name()

        send_mail(
            'Appointment Reminder',
            f'Dear {appointment.patient.first_name},\n\nYou have an appointment with {doctor_name} on {appointment.appointment_date}.\n\nBest regards,\nClinic ',
            'clinic@example.com',
            [patient_email],
            fail_silently=False,
        )
        return f'Reminder sent to {patient_email}'
    except Appointment.DoesNotExist:
        return f'Appointment with ID {appointment_id} does not exist.'
