import requests
from decouple import config
from django.core.management.base import BaseCommand, CommandError


EMAIL_API_KEY = config("EMAIL_API_KEY", default=None)
EMAIL_BASE_URL = config("EMAIL_BASE_URL", default="https://api.mailgun.net")
SANDBOX_DOMAIN = config("SANDBOX_DOMAIN", default=None)
TEST_EMAIL_TO = config(
    "TEST_EMAIL_TO", default="Michael Savage <michaelsavage940@gmail.com>"
)
TEST_EMAIL_FROM = config(
    "TEST_EMAIL_FROM", default="Mailgun Sandbox <postmaster@SANDBOX_DOMAIN>"
)


def send_simple_email():
    if not all([EMAIL_API_KEY, SANDBOX_DOMAIN]):
        raise CommandError(
            "EMAIL_API_KEY and SANDBOX_DOMAIN must be set to send the test email."
        )

    url = f"{EMAIL_BASE_URL.rstrip('/')}/v3/{SANDBOX_DOMAIN}/messages"
    data = {
        "from": TEST_EMAIL_FROM.replace("SANDBOX_DOMAIN", SANDBOX_DOMAIN),
        "to": TEST_EMAIL_TO,
        "subject": "Hello from Spanish Worksheets",
        "text": "Congratulations! You just triggered the Mailgun test command.",
    }

    response = requests.post(
        url,
        auth=("api", EMAIL_API_KEY),
        data=data,
        timeout=10,
    )
    return response


class Command(BaseCommand):
    help = "Send a test email through Mailgun using configured environment variables."

    def handle(self, *args, **options):
        response = send_simple_email()

        if response.ok:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Test email sent successfully (status {response.status_code})."
                )
            )
            return

        raise CommandError(
            f"Failed to send test email (status {response.status_code}): {response.text}"
        )
