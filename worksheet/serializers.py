import logging

from rest_framework import serializers
from rest_framework.exceptions import APIException

from worksheet.models import Worksheet
from worksheet.services.exercise_items import parse_worksheet_content

logger = logging.getLogger(__name__)


def _language_field():
    return serializers.ChoiceField(
        choices=Worksheet.Language.choices, default=Worksheet.Language.SPANISH
    )


class InvalidWorksheetContent(APIException):
    status_code = 500
    default_detail = "Worksheet content is invalid"
    default_code = "invalid_worksheet_content"


class WorksheetLanguageQuerySerializer(serializers.Serializer):
    language = _language_field()


class WorksheetSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Worksheet
        fields = ["id", "language", "created_at", "themes", "topics", "content"]

    def get_content(self, obj):
        parsed = parse_worksheet_content(obj.content)
        if parsed is None:
            logger.error(
                "Stored %s worksheet %s for %s is not valid JSON",
                obj.language,
                obj.id,
                obj.user.email,
            )
            raise InvalidWorksheetContent()
        return parsed


class GenerateLLMContentRequestSerializer(serializers.Serializer):
    themes = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    language = _language_field()


class GenerateLLMContentResponseSerializer(serializers.Serializer):
    content = serializers.CharField()


class GenerateCustomWorksheetRequestSerializer(serializers.Serializer):
    request = serializers.CharField(min_length=5, max_length=300)
    language = _language_field()

    def validate_request(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Request cannot be blank.")
        return value


class GenerateCustomWorksheetResponseSerializer(serializers.Serializer):
    request = serializers.CharField()
    language = serializers.CharField()
    content = serializers.DictField()


class GenerateWorksheetResponseSerializer(serializers.Serializer):
    content = serializers.CharField()
