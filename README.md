# Clinic360 Platform

Clinic360 Platform is a comprehensive Electronic Health Record (EHR) and clinic management system designed to streamline patient records, appointments, and overall clinic operations. Built with Django, this platform provides healthcare professionals with a seamless way to manage their practices efficiently.

## Features

- **Patient Management**: Maintain detailed patient records, including medical history and treatment plans.
- **Appointment Scheduling**: Efficiently schedule and manage patient appointments with automated reminders.
- **Medical Records**: Securely store and access patient medical records.
- **User Authentication**: Secure login and role-based access control for different users.
- **API Documentation**: Interactive API documentation available via Swagger UI.

## Live Demo

The platform is deployed and accessible online:

- **Live URL**: [Clinic360 Platform](https://clinic-platform.up.railway.app/)

## Project Structure

The project is organized into several Django applications:

- **accounts**: Manages user authentication and profiles.
- **appointments**: Handles patient appointment scheduling.
- **clinic360**: Core application integrating all modules.
- **records**: Manages patient medical records.

## Installation

To set up the Clinic360 Platform locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/debojit11/Clinic360_platform.git
   cd Clinic360_platform
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

   The platform will be accessible at `http://127.0.0.1:8000/`.

## API Access

The Clinic360 Platform provides a RESTful API for managing users, appointments, and medical records. You can explore the available endpoints using Swagger UI:

- **API Documentation**: [`https://clinic-platform.up.railway.app/api/docs/`](https://clinic-platform.up.railway.app/api/docs/)

## Deployment

The project is deployed using Railway.app. Ensure all environment variables and configurations are correctly set before deploying.

### Procfile

A `Procfile` is used to define the command for running the application in a production environment:

```
web: python manage.py collectstatic --noinput && gunicorn clinic360.wsgi:application
worker: celery -A clinic360 worker --loglevel=info
```

Make sure the `Procfile` is included in the root directory of the project.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make changes and commit: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---
For more information, visit the [Clinic360 Platform repository](https://github.com/debojit11/Clinic360_platform).
