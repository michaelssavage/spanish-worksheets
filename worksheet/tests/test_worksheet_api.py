import hashlib
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from worksheet.models import Worksheet
from worksheet.tests.test_generate import _MIN_WORKSHEET

User = get_user_model()


class LatestWorksheetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="api@example.com", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.url = "/api/worksheet/latest/"

    def test_requires_auth(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_404_when_no_worksheet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_parsed_content_with_answers(self):
        content = json.dumps(_MIN_WORKSHEET)
        Worksheet.objects.create(
            user=self.user,
            content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            content=content,
            topics=["past", "present", "future", "translation"],
            themes=["bugs"],
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["themes"], ["bugs"])
        self.assertIn("past", response.data["content"])
        first = response.data["content"]["past"][0]
        self.assertEqual(set(first.keys()), {"prompt", "answer"})
        self.assertTrue(first["answer"].startswith("sol-"))
