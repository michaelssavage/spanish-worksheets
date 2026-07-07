import hashlib
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from worksheet.models import Worksheet
from worksheet.tests.test_generate import TEST_GRAMMAR_POOLS, _MIN_WORKSHEET

User = get_user_model()


class LatestWorksheetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="api@example.com", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.url = "/api/worksheet/"

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
            topics=TEST_GRAMMAR_POOLS,
            themes=["bugs"],
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["themes"], ["bugs"])
        self.assertIn("past tenses", response.data["content"])
        first = response.data["content"]["past tenses"][0]
        self.assertEqual(set(first.keys()), {"prompt", "answer"})
        self.assertIsInstance(first["answer"], list)
        self.assertTrue(first["answer"][0].startswith("sol-"))


class GenerateCustomWorksheetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="custom-api@example.com", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.url = "/api/worksheet/custom/"

    def test_requires_auth(self):
        self.client.credentials()
        response = self.client.post(
            self.url,
            {"request": "Subjunctive tense about birthdays"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_missing_request(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("request", response.data)

    def test_rejects_blank_request(self):
        response = self.client.post(self.url, {"request": "   "}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("request", response.data)

    @patch("worksheet.views.generate_custom_exercises")
    def test_returns_custom_exercises_without_persisting(self, mock_generate):
        content = {
            "exercises": [
                {
                    "prompt": f"Mi amiga ___ (venir) a la fiesta {i}.",
                    "answer": ["venga"],
                }
                for i in range(8)
            ]
        }
        mock_generate.return_value = content

        response = self.client.post(
            self.url,
            {"request": "  Subjunctive tense about birthdays  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["request"], "Subjunctive tense about birthdays")
        self.assertEqual(response.data["content"], content)
        self.assertEqual(len(response.data["content"]["exercises"]), 8)
        self.assertEqual(Worksheet.objects.count(), 0)
        mock_generate.assert_called_once_with("Subjunctive tense about birthdays")

    @patch("worksheet.views.generate_custom_exercises")
    def test_returns_502_when_generation_fails(self, mock_generate):
        mock_generate.return_value = None

        response = self.client.post(
            self.url,
            {"request": "Subjunctive tense about birthdays"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data, {"error": "Custom worksheet generation failed"})
