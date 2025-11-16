# Spanish Worksheets

Homework straight to your inbox.

## Setup
### first time setup

1. `poetry init`
2. `poetry install`
3. `poetry run django-admin startproject config .`
4. `poetry run python manage.py runserver`
5. `poetry run python manage.py migrate`

### create a new model / section

1. `poetry run python manage.py startapp NEW_ITEM`
2. Register the app in config/settings.py
3. `poetry run python manage.py makemigrations`
4. `poetry run python manage.py migrate`

### adding a new dependency

`poetry add DEPENDENCY`

## Endpoints

With custom themes (POST):
```bash
  curl -X POST http://your-domain/api/generate/ \
    -H "Content-Type: application/json" \
    -d '{"themes": ["viajes", "hoteles"]}'
```