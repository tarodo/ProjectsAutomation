release: python manage.py migrate
web: gunicorn ProjectAutomation.wsgi --log-file=-
bot: python manage.py bot