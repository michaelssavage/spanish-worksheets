from rest_framework import serializers


class GenerateLLMContentRequestSerializer(serializers.Serializer):
    themes = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )


class GenerateLLMContentResponseSerializer(serializers.Serializer):
    content = serializers.CharField()


class GenerateCustomWorksheetRequestSerializer(serializers.Serializer):
    request = serializers.CharField(min_length=5, max_length=300)

    def validate_request(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Request cannot be blank.")
        return value


class GenerateCustomWorksheetResponseSerializer(serializers.Serializer):
    request = serializers.CharField()
    content = serializers.DictField()


class GenerateWorksheetResponseSerializer(serializers.Serializer):
    content = serializers.CharField()
