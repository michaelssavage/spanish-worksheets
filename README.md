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

Set `REDIS_URL` in `.env` (see `.env.example`). Worksheet delivery uses **django-rq**: `POST /api/worksheet/generate-worksheet/` only enqueues a job. Run a worker in a second terminal:

```bash
poetry run python manage.py rqworker default
```

### Railway / production

Use the same repo for **two** Railway services (or one web + one worker process), both with `DATABASE_URL`, `REDIS_URL`, and the same env as the web app. **Web:** `gunicorn` (or your current start command). **Worker:** `python manage.py rqworker default`. Without the worker, jobs accumulate in Redis and emails are never sent, while HTTP clients may still see `202 Accepted`.

### creating a new subsection

1. `poetry run python manage.py startapp NEW_APP`
2. Register the app in config/settings.py
3. `poetry run python manage.py makemigrations`
4. `poetry run python manage.py migrate`

### adding a new dependency

`poetry add DEPENDENCY`

## Verifying Email Provider

I used Mailgun for sending emails. I had to edit the DNS records for wherever your site is hosted. That was Netlify in my case.
