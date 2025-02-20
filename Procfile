web: python manage.py collectstatic --noinput && gunicorn clinic360.wsgi:application
worker: celery -A clinic360 worker --loglevel=info
