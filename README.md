# Projects Automation
Сервис, что позволяет формировать группы на проекты в соответствии с их возможными временными слотами на время проекта.

## Setup
1. Create `.env` from `.env.Exmaple`
2. `pip install -r requirements.txt`

## .env
1. `TELEGRAM_TOKEN` - Get token from [BotFather](https://t.me/botfather)
2. `SECRET_KEY` - Django SECRET_KEY
3. `DEBUG` - Django mode
4. `ALLOWED_HOSTS` - Настройка доверенных хостов. По дефолту: `['.localhost', '127.0.0.1', '[::1]', '.herokuapp.com']`
5. `DATABASE_URL` - настройка доступа к БД. Согласно [примеру](https://github.com/jacobian/dj-database-url#url-schema)

## Run
### Bot
```
python manage.py migrate
python manage.py bot
```
### Django admin
### First run
```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
http://127.0.0.1:8000/admin/
```
### Common run
```
python manage.py migrate
python manage.py runserver
```