from rest_framework import serializers


class GenerateLLMContentRequestSerializer(serializers.Serializer):
    themes = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )


class GenerateLLMContentResponseSerializer(serializers.Serializer):
    content = serializers.CharField()


class GenerateWorksheetResponseSerializer(serializers.Serializer):
    content = serializers.CharField()


class SchedulerResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
