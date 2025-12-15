from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "short_bio",
            "long_bio",
            "avatar",
        ]
        read_only_fields = ["id", "username"]

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "short_bio",
            "long_bio",
            "avatar",
        ]

class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer de login personalizado:
    - Recibe username y password
    - Devuelve access, refresh y datos del usuario
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user  # usuario autenticado

        # Añadimos info del usuario al response
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "short_bio": user.short_bio,
            "long_bio": user.long_bio,
            "avatar": (
                self.context["request"].build_absolute_uri(user.avatar.url)
                if user.avatar
                else None
            ),
        }

        return data