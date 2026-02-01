from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock
import json
import requests

from worksheet.services.email import (
    normalize_to_list,
    format_worksheet_html,
    send_worksheet_email,
)
from recipients.models import UserRecipient

User = get_user_model()


class NormalizeToListTest(TestCase):
    """Test normalize_to_list function for various input types"""

    def test_already_list(self):
        """Test that list input returns unchanged"""
        input_list = ["item1", "item2", "item3"]
        result = normalize_to_list(input_list)
        self.assertEqual(result, input_list)

    def test_string_with_quoted_list_pattern(self):
        """Test splitting by '", "' pattern (quoted list strings)"""
        input_str = '"item1", "item2", "item3"'
        result = normalize_to_list(input_str)
        self.assertEqual(result, ["item1", "item2", "item3"])

    def test_string_with_sentence_boundary_pattern(self):
        """Test splitting by '., ' pattern (sentence boundaries)"""
        input_str = "Sentence one., Sentence two., Sentence three."
        result = normalize_to_list(input_str)
        self.assertEqual(result, ["Sentence one.", "Sentence two.", "Sentence three."])

    def test_sentence_pattern_without_final_period(self):
        """Test sentence pattern where last sentence doesn't have period"""
        input_str = "First sentence., Second sentence., Third sentence"
        result = normalize_to_list(input_str)
        self.assertEqual(
            result, ["First sentence.", "Second sentence.", "Third sentence"]
        )

    def test_plain_string(self):
        """Test that plain string returns as single-item list"""
        input_str = "Just a single string"
        result = normalize_to_list(input_str)
        self.assertEqual(result, [input_str])

    def test_non_string_non_list(self):
        """Test that non-string, non-list returns empty list"""
        result = normalize_to_list(123)
        self.assertEqual(result, [])

    def test_empty_string(self):
        """Test empty string handling"""
        result = normalize_to_list("")
        self.assertEqual(result, [""])

    def test_quoted_pattern_with_extra_quotes(self):
        """Test quoted pattern with various quote styles"""
        input_str = "'item1', 'item2', 'item3'"
        # This should not match the '", "' pattern, so returns as single item
        result = normalize_to_list(input_str)
        self.assertEqual(result, [input_str])


class FormatWorksheetHtmlTest(TestCase):
    """Test format_worksheet_html function"""

    def test_valid_json_string(self):
        """Test formatting valid JSON string"""
        content = json.dumps(
            {
                "past": ["Ayer fui al parque.", "Comí pizza."],
                "present": ["Voy a la escuela.", "Estudio español."],
                "future": ["Mañana viajaré.", "Compraré un coche."],
                "error_correction": ["palabra", "frase"],
            }
        )
        result = format_worksheet_html(content)

        self.assertIn("<html>", result)
        self.assertIn("Past Tense", result)
        self.assertIn("Present Tense", result)
        self.assertIn("Future Tense", result)
        self.assertIn("Vocabulary Expansion", result)
        self.assertIn("Ayer fui al parque.", result)
        self.assertIn("Voy a la escuela.", result)

    def test_valid_dict(self):
        """Test formatting valid dict object"""
        content = {
            "past": ["Sentence 1"],
            "present": ["Sentence 2"],
            "future": ["Sentence 3"],
            "error_correction": ["word"],
        }
        result = format_worksheet_html(content)

        self.assertIn("<html>", result)
        self.assertIn("Sentence 1", result)
        self.assertIn("Sentence 2", result)
        self.assertIn("Sentence 3", result)
        self.assertIn("word", result)

    def test_missing_sections(self):
        """Test handling of missing sections in JSON"""
        content = {"past": ["Only past tense"]}
        result = format_worksheet_html(content)

        # Should still generate HTML structure
        self.assertIn("<html>", result)
        self.assertIn("Past Tense", result)
        self.assertIn("Only past tense", result)
        # Other sections should be empty but structure should exist
        self.assertIn("Present Tense", result)
        self.assertIn("Future Tense", result)

    def test_string_values_normalization(self):
        """Test that string values are normalized to lists"""
        content = {
            "past": '"Sentence 1", "Sentence 2"',  # String that should be split
            "present": ["Normal list"],
            "future": "Single sentence., Another sentence.",
            "error_correction": ["word"],
        }
        result = format_worksheet_html(content)

        self.assertIn("Sentence 1", result)
        self.assertIn("Sentence 2", result)
        self.assertIn("Single sentence.", result)
        self.assertIn("Another sentence.", result)

    def test_html_escaping_xss_prevention(self):
        """Test that HTML special characters are escaped to prevent XSS"""
        content = {
            "past": ["<script>alert('xss')</script>", "Normal & safe"],
            "present": ["<img src=x onerror=alert(1)>"],
            "future": ["'quotes' & \"more quotes\""],
            "error_correction": ["<b>bold</b>"],
        }
        result = format_worksheet_html(content)

        # Should escape HTML tags
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("&lt;img", result)
        self.assertIn("&amp;", result)
        self.assertIn("&quot;", result)
        # Should not contain unescaped script tags
        self.assertNotIn("<script>", result)

    def test_invalid_json_fallback(self):
        """Test fallback behavior for invalid JSON"""
        content = "This is not valid JSON at all"
        result = format_worksheet_html(content)

        # Should return fallback HTML with content in <pre> tag
        self.assertIn("<html>", result)
        self.assertIn("<pre>", result)
        self.assertIn("This is not valid JSON at all", result)

    def test_empty_content(self):
        """Test handling of empty content"""
        content = {}
        result = format_worksheet_html(content)

        # Should still generate valid HTML structure
        self.assertIn("<html>", result)
        self.assertIn("Past Tense", result)
        self.assertIn("Present Tense", result)

    def test_malformed_json_string(self):
        """Test handling of malformed JSON string"""
        content = '{"past": [unclosed string}'
        result = format_worksheet_html(content)

        # Should fallback to plain text display
        self.assertIn("<html>", result)
        self.assertIn("<pre>", result)


class SendWorksheetEmailTest(TestCase):
    """Test send_worksheet_email function"""

    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_successful_email_send(self, mock_post):
        """Test successful email sending"""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        content = {
            "past": ["Ayer fui al parque."],
            "present": ["Voy a la escuela."],
            "future": ["Mañana viajaré."],
            "error_correction": ["palabra"],
        }

        # Execute
        send_worksheet_email(self.user, content)

        # Assert
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["auth"], ("api", "test-api-key"))
        self.assertEqual(call_args[1]["timeout"], 10)

        # Check email data
        email_data = call_args[1]["data"]
        self.assertEqual(email_data["from"], "noreply@test.com")
        self.assertEqual(email_data["subject"], "Your Spanish Worksheet")
        # Note: user.email_recipients only includes additional recipients, not user's own email
        self.assertEqual(email_data["to"], [])
        self.assertIn("text", email_data)
        self.assertIn("html", email_data)

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_email_with_additional_recipients(self, mock_post):
        """Test email sending includes additional recipients"""
        # Add additional recipients
        UserRecipient.objects.create(user=self.user, email="recipient1@example.com")
        UserRecipient.objects.create(user=self.user, email="recipient2@example.com")

        mock_response = Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        content = {
            "past": ["Test"],
            "present": ["Test"],
            "future": ["Test"],
            "error_correction": ["Test"],
        }
        send_worksheet_email(self.user, content)

        # Check that all recipients are included
        call_args = mock_post.call_args
        email_data = call_args[1]["data"]
        recipients = email_data["to"]

        # Should include only additional recipients (not user's own email)
        self.assertIn("recipient1@example.com", recipients)
        self.assertIn("recipient2@example.com", recipients)
        self.assertEqual(len(recipients), 2)

    @override_settings(
        MAILGUN_API_KEY="",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    def test_missing_mailgun_api_key(self):
        """Test that missing API key raises ValueError"""
        content = {
            "past": ["Test"],
            "present": ["Test"],
            "future": ["Test"],
            "error_correction": ["Test"],
        }

        with self.assertRaises(ValueError) as context:
            send_worksheet_email(self.user, content)

        self.assertIn("MAILGUN_API_KEY", str(context.exception))

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    def test_missing_mailgun_domain(self):
        """Test that missing domain raises ValueError"""
        content = {
            "past": ["Test"],
            "present": ["Test"],
            "future": ["Test"],
            "error_correction": ["Test"],
        }

        with self.assertRaises(ValueError) as context:
            send_worksheet_email(self.user, content)

        self.assertIn("MAILGUN_DOMAIN", str(context.exception))

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_mailgun_api_failure(self, mock_post):
        """Test handling of Mailgun API failure"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        # Make raise_for_status raise an exception
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Bad Request"
        )
        mock_post.return_value = mock_response

        content = {
            "past": ["Test"],
            "present": ["Test"],
            "future": ["Test"],
            "error_correction": ["Test"],
        }

        with self.assertRaises(requests.exceptions.HTTPError):
            send_worksheet_email(self.user, content)

        # Should call raise_for_status
        mock_response.raise_for_status.assert_called_once()

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_network_error_handling(self, mock_post):
        """Test handling of network/timeout errors"""
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")

        content = {
            "past": ["Test"],
            "present": ["Test"],
            "future": ["Test"],
            "error_correction": ["Test"],
        }

        with self.assertRaises(requests.exceptions.Timeout):
            send_worksheet_email(self.user, content)

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_plain_text_generation(self, mock_post):
        """Test that plain text version is generated correctly"""
        mock_response = Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        content = {
            "past": ["Ayer fui al parque.", "Comí pizza."],
            "present": ["Voy a la escuela."],
            "future": ["Mañana viajaré."],
            "error_correction": ["palabra", "frase"],
        }
        send_worksheet_email(self.user, content)

        call_args = mock_post.call_args
        plain_text = call_args[1]["data"]["text"]

        self.assertIn("Your Spanish Worksheet", plain_text)
        self.assertIn("El pasado:", plain_text)
        self.assertIn("El presente:", plain_text)
        self.assertIn("El futuro:", plain_text)
        self.assertIn("Ampliación de vocabulario:", plain_text)
        self.assertIn("Ayer fui al parque.", plain_text)
        self.assertIn("Comí pizza.", plain_text)

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_json_string_content(self, mock_post):
        """Test handling of JSON string content"""
        mock_response = Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        content = json.dumps(
            {
                "past": ["Test past"],
                "present": ["Test present"],
                "future": ["Test future"],
                "error_correction": ["Test vocab"],
            }
        )
        send_worksheet_email(self.user, content)

        # Should process successfully
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        email_data = call_args[1]["data"]
        self.assertIn("Test past", email_data["text"])

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net/",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_url_construction_with_trailing_slash(self, mock_post):
        """Test URL construction handles trailing slash in base URL"""
        mock_response = Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        content = {
            "past": ["Test"],
            "present": ["Test"],
            "future": ["Test"],
            "error_correction": ["Test"],
        }
        send_worksheet_email(self.user, content)

        call_args = mock_post.call_args
        url = call_args[0][0]

        # Should not have double slashes
        self.assertNotIn("//v3", url)
        self.assertIn("/v3/test.mailgun.org/messages", url)

    @override_settings(
        MAILGUN_API_KEY="test-api-key",
        MAILGUN_DOMAIN="test.mailgun.org",
        MAILGUN_BASE_URL="https://api.mailgun.net",
        DEFAULT_FROM_EMAIL="noreply@test.com",
    )
    @patch("worksheet.services.email.requests.post")
    def test_invalid_content_fallback(self, mock_post):
        """Test handling of invalid content that can't be parsed"""
        mock_response = Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        # Invalid content that will fail JSON parsing
        content = "Not valid JSON at all"
        send_worksheet_email(self.user, content)

        # Should still send email with fallback content
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        email_data = call_args[1]["data"]
        # Plain text should be the string representation
        self.assertEqual(email_data["text"], "Not valid JSON at all")
