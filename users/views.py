from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from rest_framework.serializers import Serializer, CharField, ValidationError
from django.contrib.auth import authenticate


class TokenObtainSerializer(Serializer):
    username = CharField(required=True)
    password = CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise ValidationError("Invalid username or password")
        attrs["user"] = user
        return attrs


class TokenObtainView(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = TokenObtainSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)
