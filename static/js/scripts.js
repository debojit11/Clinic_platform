// Utility function to include CSRF token in AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Login Form Submission
document.getElementById('loginForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/api/accounts/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            localStorage.setItem('token', data.access); // Save JWT token
            window.location.href = data.redirect; // Redirect to the appropriate portal
        } else {
            alert('Login failed!');
        }
    });
});

// Register Form Submission
document.getElementById('registerForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    fetch('/api/accounts/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ username, email, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.username) {
            alert('Registration successful!');
            window.location.href = '/login/'; // Redirect to login page
        } else {
            alert('Registration failed!');
        }
    });
});

// Fetch doctors and populate the dropdown
function fetchDoctors() {
    fetch('/api/appointments/doctors/')
        .then(response => response.json())
        .then(data => {
            const doctorSelect = document.getElementById('doctorSelect');
            if (doctorSelect) {
                doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
                data.forEach(doctor => {
                    const option = `<option value="${doctor.id}">${doctor.user.username}</option>`;
                    doctorSelect.innerHTML += option;
                });
            }
        });
}

// Fetch time slots for a selected doctor
function fetchTimeSlots(doctorId) {
    fetch(`/api/appointments/availability/?doctor_id=${doctorId}`)
        .then(response => response.json())
        .then(data => {
            const timeSlotSelect = document.getElementById('timeSlotSelect');
            if (timeSlotSelect) {
                timeSlotSelect.innerHTML = '<option value="">Select a time slot</option>';
                data.forEach(slot => {
                    const option = `<option value="${slot.id}">${slot.start_time} - ${slot.end_time}</option>`;
                    timeSlotSelect.innerHTML += option;
                });
            }
        });
}

// Book Appointment Form Submission
document.getElementById('bookAppointmentForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const doctorId = document.getElementById('doctorSelect').value;
    const timeSlotId = document.getElementById('timeSlotSelect').value;
    const reason = document.getElementById('reason').value;

    fetch('/api/appointments/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            doctor: doctorId,
            availability: timeSlotId,
            reason: reason,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            alert('Appointment booked successfully!');
            window.location.reload(); // Refresh the page
        } else {
            alert('Failed to book appointment!');
        }
    });
});

// Confirm Appointment (Doctor)
function confirmAppointment(appointmentId) {
    fetch(`/api/appointments/${appointmentId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ is_confirmed: true }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.is_confirmed) {
            alert('Appointment confirmed!');
            window.location.reload(); // Refresh the page
        } else {
            alert('Failed to confirm appointment!');
        }
    });
}

// Fetch and display appointments
function fetchAppointments() {
    fetch('/api/appointments/')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('appointmentsTable');
            if (table) {
                table.innerHTML = ''; // Clear existing rows
                data.forEach(appointment => {
                    const row = `<tr>
                        <td>${appointment.appointment_date}</td>
                        <td>${appointment.doctor.user.username}</td>
                        <td>${appointment.availability.start_time} - ${appointment.availability.end_time}</td>
                        <td>${appointment.is_confirmed ? 'Confirmed' : 'Pending'}</td>
                        <td>
                            <button class="btn btn-danger btn-sm" onclick="cancelAppointment(${appointment.id})">Cancel</button>
                        </td>
                    </tr>`;
                    table.innerHTML += row;
                });
            }
        });
}

// Fetch and display medical records
function fetchMedicalRecords() {
    fetch('/api/records/')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('medicalRecordsTable');
            if (table) {
                table.innerHTML = ''; // Clear existing rows
                data.forEach(record => {
                    const row = `<tr>
                        <td>${record.date_created}</td>
                        <td>${record.diagnosis}</td>
                        <td>${record.treatment}</td>
                        <td>${record.doctor_notes}</td>
                    </tr>`;
                    table.innerHTML += row;
                });
            }
        });
}

// Call the functions on page load
document.addEventListener('DOMContentLoaded', function () {
    fetchDoctors();
    fetchAppointments();
    fetchMedicalRecords();
});