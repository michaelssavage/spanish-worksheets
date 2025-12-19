from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.views import TokenObtainSerializer

User = get_user_model()


class TokenObtainSerializerTest(TestCase):
    """Tests for TokenObtainSerializer"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_valid_credentials(self):
        """Test serializer with valid credentials"""
        serializer = TokenObtainSerializer(
            data={"username": "test@example.com", "password": "testpass123"}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_missing_username(self):
        """Test serializer with missing username"""
        serializer = TokenObtainSerializer(data={"password": "testpass123"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_missing_password(self):
        """Test serializer with missing password"""
        serializer = TokenObtainSerializer(data={"username": "test@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_empty_username(self):
        """Test serializer with empty username"""
        serializer = TokenObtainSerializer(
            data={"username": "", "password": "testpass123"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)


class TokenObtainViewTest(TestCase):
    """Tests for TokenObtainView"""

    def setUp(self):
        """Set up test user and API client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.url = "/api/token/"

    def test_successful_token_creation(self):
        """Test successful token creation with valid credentials"""
        response = self.client.post(
            self.url, {"username": "test@example.com", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_token_retrieval_for_existing_token(self):
        """Test that existing token is returned instead of creating new one"""
        # Create a token first
        existing_token, _ = Token.objects.get_or_create(user=self.user)

        response = self.client.post(
            self.url, {"username": "test@example.com", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], existing_token.key)
        # Verify only one token exists
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)

    def test_invalid_credentials(self):
        """Test view with invalid credentials"""
        response = self.client.post(
            self.url, {"username": "test@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_invalid_username(self):
        """Test view with non-existent username"""
        response = self.client.post(
            self.url, {"username": "nonexistent@example.com", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_missing_username(self):
        """Test view with missing username field"""
        response = self.client.post(self.url, {"password": "testpass123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_missing_password(self):
        """Test view with missing password field"""
        response = self.client.post(self.url, {"username": "test@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
