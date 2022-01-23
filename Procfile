release: python manage.py migrate
web: gunicorn ProjectsAutomation.wsgi --log-file=-
bot: python manage.py bot