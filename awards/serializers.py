from rest_framework import serializers
from django.db.models import Count, Q
from .models import Nomination, Award, AwardSuggestion, Vote


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = [
            "id",
            "titulo",
            "resumen",
            "descripcion",
            "activo",
            "allow_nominations",
            "allow_voting",
            "show_results",
            "allow_pair_nominations",
            "award_type",
        ]


class NominationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nomination
        fields = [
            "id",
            "award",
            "nominado",
            "nominado_secundario",  # 👈 segundo integrante (puede ser null)
            "nominado_por",
            "hazana",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "nominado_por", "is_active", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        award = attrs["award"]
        nominado = attrs["nominado"]

        # 1) Si el premio está cerrado, no se puede nominar
        if not award.allow_nominations:
            raise serializers.ValidationError(
                "Este premio está cerrado y no admite nuevas nominaciones."
            )

        # 2) Límite: máximo 3 nominaciones por premio y usuario que nomina
        count = Nomination.objects.filter(
            award=award,
            nominado_por=user,
            is_active=True,
        ).count()
        if count >= 3:
            raise serializers.ValidationError(
                "Has alcanzado el máximo de 3 nominaciones para este premio."
            )

        # 3) Evitar nominarse a uno mismo (si quieres esta regla, es opcional)
        if nominado == user:
            raise serializers.ValidationError(
                "No puedes nominarte a ti mismo, mi rey. Que no eres tan especial."
            )

        return attrs

    def create(self, validated_data):
        # El nominado_por siempre es el usuario autenticado
        user = self.context["request"].user
        validated_data["nominado_por"] = user
        return super().create(validated_data)


class AwardSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwardSuggestion
        fields = [
            "id",
            "titulo",
            "resumen",
            "descripcion",

            # NUEVO
            "award_type",
            "nomination_mode",
            "max_participants",

            "created_at",
            "is_reviewed",
            "is_accepted",
        ]
        read_only_fields = ["id", "created_at", "is_reviewed", "is_accepted"]

    def validate(self, attrs):
        mode = attrs.get("nomination_mode", "single")
        max_p = attrs.get("max_participants", None)

        if mode != "multi":
            # si no es multi, ignoramos max_participants
            attrs["max_participants"] = None
            return attrs

        # mode == multi
        if max_p is None:
            # si quieres permitirlo sin número, puedes poner default aquí:
            attrs["max_participants"] = 4
            return attrs

        if max_p < 3:
            raise serializers.ValidationError(
                {"max_participants": "Para 'varios', el máximo debe ser 3 o más."}
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)


class NominationWithVotesSerializer(serializers.ModelSerializer):
    nominado_username = serializers.CharField(
        source="nominado.username", read_only=True
    )
    nominado_nickname = serializers.CharField(
        source="nominado.nickname", read_only=True
    )
    votos = serializers.IntegerField(read_only=True)
    is_my_vote = serializers.BooleanField(read_only=True)

    class Meta:
        model = Nomination
        fields = [
            "id",
            "award",
            "nominado",
            "nominado_username",
            "nominado_nickname",
            "hazana",
            "votos",
            "is_my_vote",
        ]


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = [
            "id",
            "award",
            "nomination",
            "voter",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "voter", "is_active", "created_at", "award"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        award: Award = self.context["award"]
        nomination: Nomination = attrs["nomination"]

        # Aseguramos que la nominación pertenece al premio de la URL
        if nomination.award_id != award.id:
            raise serializers.ValidationError(
                "Esa nominación no pertenece a este premio, bribón."
            )

        # Inyectamos estos campos en el validated_data
        attrs["award"] = award
        attrs["voter"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["voter"]
        award = validated_data["award"]
        nomination = validated_data["nomination"]

        # ¿Hay ya un voto activo de este usuario para este premio?
        previous_vote = Vote.objects.filter(
            award=award,
            voter=user,
            is_active=True,
        ).first()

        if previous_vote:
            # Si ya estaba votando a esta nominación, no hacemos nada raro
            if previous_vote.nomination_id == nomination.id:
                return previous_vote

            # Cambiar voto: desactivar el antiguo
            previous_vote.is_active = False
            previous_vote.save()

        # Creamos el nuevo voto activo
        return super().create(validated_data)
    
class ParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    nickname = serializers.CharField(allow_blank=True)
    avatar = serializers.CharField(allow_null=True)

class AggregatedNominationResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    award = serializers.IntegerField()

    # Nuevo: lista flexible 1..N
    participants = ParticipantSerializer(many=True)
    display_name = serializers.CharField()

    # Para clip
    clip_title = serializers.CharField(allow_blank=True, required=False)
    clip_url = serializers.CharField(allow_blank=True, required=False)

    hazanas = serializers.ListField(child=serializers.CharField())
    votos = serializers.IntegerField()
    is_my_vote = serializers.BooleanField()