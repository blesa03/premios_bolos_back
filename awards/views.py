# awards/views.py
from rest_framework import generics, permissions, views, response, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from .models import Award, Nomination, AwardSuggestion, Vote
from .serializers import (
    AwardSerializer,
    NominationSerializer,
    AwardSuggestionSerializer,
    VoteSerializer,
    NominationWithVotesSerializer,
    AggregatedNominationResultSerializer,
)


class AwardListView(generics.ListAPIView):
    queryset = Award.objects.filter(activo=True)
    serializer_class = AwardSerializer
    permission_classes = [permissions.IsAuthenticated]


class AwardNominationsListView(generics.ListCreateAPIView):
    """
    GET  -> lista nominaciones activas de un premio
    POST -> crea una nominación nueva para ese premio
    """
    serializer_class = NominationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        award_id = self.kwargs["award_id"]
        return (
            Nomination.objects.filter(
                award_id=award_id,
                is_active=True,
            )
            .select_related("nominado", "nominado_secundario", "nominado_por")
        )


class AwardDetailView(generics.RetrieveAPIView):
    queryset = Award.objects.filter(activo=True)
    serializer_class = AwardSerializer
    permission_classes = [permissions.IsAuthenticated]


class AwardResultsView(generics.GenericAPIView):
    serializer_class = AggregatedNominationResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, award_id):
        user = request.user

        try:
            award = Award.objects.get(pk=award_id, activo=True)
        except Award.DoesNotExist:
            return response.Response({"detail": "Premio no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        qs = (
            Nomination.objects.filter(award=award, is_active=True)
            .select_related("nominado", "nominado_secundario")
            .prefetch_related("participantes")
            .annotate(
                votos=Count("votes", filter=Q(votes__is_active=True)),
                is_my_vote=Count(
                    "votes",
                    filter=Q(votes__is_active=True, votes__voter=user),
                ),
            )
            .order_by("id")
        )

        def avatar_abs(u):
            av = u.avatar.url if getattr(u, "avatar", None) else None
            if av and not av.startswith("http"):
                return request.build_absolute_uri(av)
            return av

        def pick_name(u):
            return (getattr(u, "nickname", "") or "").strip() or u.username

        def build_participants(nom: Nomination):
            # Si has metido participantes M2M, úsalo (clips/premios multi)
            parts = list(nom.participantes.all())
            if parts:
                return parts
            # fallback por compatibilidad
            parts = [nom.nominado]
            if nom.nominado_secundario_id:
                parts.append(nom.nominado_secundario)
            return parts

        def display_name_from(parts):
            names = [pick_name(p) for p in parts]
            if len(names) == 2:
                return f"{names[0]} & {names[1]}"
            if len(names) <= 1:
                return names[0] if names else ""
            # 3+ -> "A, B & C"
            return ", ".join(names[:-1]) + " & " + names[-1]

        # ---- CASO CLIP: cada nomination = 1 candidato ----
        def abs_url(url: str | None):
            if not url:
                return ""
            url = url.strip()
            if not url:
                return ""
            # Si viene "media/..." lo normalizamos a "/media/..."
            if not url.startswith("http") and not url.startswith("/"):
                url = "/" + url
            if request is not None and not url.startswith("http"):
                return request.build_absolute_uri(url)
            return url

        if award.award_type == "clip":
            data_list = []
            for nom in qs:
                parts = build_participants(nom)
                payload = {
                    "id": nom.id,
                    "award": award.id,
                    "participants": [
                        {
                            "id": p.id,
                            "username": p.username,
                            "nickname": (getattr(p, "nickname", "") or ""),
                            "avatar": avatar_abs(p),
                        }
                        for p in parts
                    ],
                    "display_name": display_name_from(parts),
                    "clip_title": nom.clip_title or "",
                    "clip_url": abs_url(nom.clip_url),
                    "hazanas": [nom.hazana] if nom.hazana else [],
                    "votos": int(nom.votos or 0),
                    "is_my_vote": int(nom.is_my_vote or 0) > 0,
                }
                data_list.append(payload)

            ser = self.get_serializer(data_list, many=True)
            return response.Response(ser.data)

        # ---- CASO PEOPLE: agrupación por usuario o pareja ----
        grouped = {}

        for nom in qs:
            votos = int(nom.votos or 0)
            my_vote = int(nom.is_my_vote or 0) > 0

            # key de agrupación
            if award.allow_pair_nominations and nom.nominado_secundario_id:
                a, b = sorted([nom.nominado_id, nom.nominado_secundario_id])
                key = f"pair:{a}-{b}"
            else:
                key = f"single:{nom.nominado_id}"

            if key not in grouped:
                parts = build_participants(nom)
                grouped[key] = {
                    "id": nom.id,  # nomination representativa para votar
                    "award": award.id,
                    "participants": [
                        {
                            "id": p.id,
                            "username": p.username,
                            "nickname": (getattr(p, "nickname", "") or ""),
                            "avatar": avatar_abs(p),
                        }
                        for p in parts
                    ],
                    "display_name": display_name_from(parts),
                    "clip_title": "",
                    "clip_url": "",
                    "hazanas": [nom.hazana] if nom.hazana else [],
                    "votos": votos,
                    "is_my_vote": my_vote,
                }
            else:
                entry = grouped[key]
                if nom.hazana:
                    entry["hazanas"].append(nom.hazana)
                entry["votos"] += votos
                entry["is_my_vote"] = entry["is_my_vote"] or my_vote

        data_list = list(grouped.values())
        ser = self.get_serializer(data_list, many=True)
        return response.Response(ser.data)


class AwardVoteView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, award_id):
        try:
            award = Award.objects.get(pk=award_id, activo=True)
        except Award.DoesNotExist:
            return response.Response(
                {"detail": "Premio no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 👇 Aquí cerramos la votación aunque existan nominaciones
        if not award.allow_voting:
            return response.Response(
                {"detail": "La votación para este premio está cerrada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VoteSerializer(
            data=request.data,
            context={"request": request, "award": award},
        )
        serializer.is_valid(raise_exception=True)
        vote = serializer.save()

        return response.Response(
            VoteSerializer(
                vote,
                context={"request": request, "award": award},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AwardSuggestionListCreateView(generics.ListCreateAPIView):
    """
    GET -> lista las sugerencias hechas por el propio usuario
    POST -> crea una nueva sugerencia
    """
    serializer_class = AwardSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AwardSuggestion.objects.filter(created_by=self.request.user)