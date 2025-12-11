# Spanish Worksheets

**Homework straight to your inbox.**

A Django app deployed to Railway with a Github Action CRON job. The CRON runs every second day and generates Spanish homework via an LLM, and then sends an email of the homework via Mailgun's API.

## Setup
### first time setup locally

1. `poetry init`
2. `poetry install`
3. `poetry run django-admin startproject config .`
4. `poetry run python manage.py runserver`
5. `poetry run python manage.py migrate`
6. `poetry run python manage.py createsuperuser`

### creating a new subsection

1. `poetry run python manage.py startapp NEW_APP`
2. Register the app in config/settings.py
3. `poetry run python manage.py makemigrations`
4. `poetry run python manage.py migrate`

### adding a new dependency

`poetry add DEPENDENCY`

## Verifying Email Provider

I used Mailgun for sending emails. I had to edit the DNS records for wherever your site is hosted. That was Netlify in my case.

## Endpoints

Get llm content with custom themes (POST):
```bash
  curl -X POST http://your-domain/api/worksheet/generate-worksheet \
    -H "Content-Type: application/json" -H "Authorization: Token TOKEN_VALUE" \
    -d '{"themes": ["viajes", "hoteles"]}'
```

response:


```json
{
  "content": {  
    "past": [
      "Ayer mi hermana ________ (cocinar) la cena para toda la familia", 
      ......
    ],
    "present_future": [
      "Mañana mi madre ________ (preparar) el almuerzo temprano", 
      ......
    ],  
    "vocab": [
      "Mi tío prefiere el pescado a la carne en sus comidas", 
      ....
    ]
  }
}
```

get token
```bash
  curl -X POST http://localhost:8000/api/token/ \
    -d "username=yourusername&password=yourpassword"
```