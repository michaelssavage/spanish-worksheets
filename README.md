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

Get llm content with custom themes (POST):
```bash
  curl -X POST http://your-domain/api/generate/ \
    -H "Content-Type: application/json" \
    -d '{"themes": ["viajes", "hoteles"]}'
```

response:


```json
{
    "content": "{\n  
    \"past\": [
      \"Ayer mi hermana ________ (cocinar) la cena para toda la familia\", 
      ......
    ],\n

    \"present_future\": [
      \"Mañana mi madre ________ (preparar) el almuerzo temprano\", 
      ......
    ],\n  

    \"vocab\": [
      \"Mi tío prefiere el pescado a la carne en sus comidas\", 
      ....
    ]\n}"
}
```

get token
```bash
  curl -X POST http://localhost:8000/api/token/ \
    -d "username=yourusername&password=yourpassword"
```