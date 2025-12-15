from django.conf import settings
from django.db import models
from django.db.models import Q

User = settings.AUTH_USER_MODEL

class Award(models.Model):
    AWARD_TYPES = (
        ("people", "Personas"),
        ("clip", "Clip del Año"),
    )

    titulo = models.CharField(max_length=100)
    resumen = models.CharField(max_length=255)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)

    allow_nominations = models.BooleanField(default=True)
    allow_voting = models.BooleanField(default=True)
    show_results = models.BooleanField(default=False)

    allow_pair_nominations = models.BooleanField(
        default=False,
        help_text="Si está en True, este premio permite nominar a dos integrantes juntos."
    )

    award_type = models.CharField(
        max_length=20,
        choices=AWARD_TYPES,
        default="people",
        help_text="people = premio normal (1 o 2 integrantes). clip = candidatos son clips con N participantes."
    )

    def __str__(self):
        return self.titulo
    
class Nomination(models.Model):
    award = models.ForeignKey(Award, on_delete=models.CASCADE, related_name="nominaciones")

    # Para compatibilidad con lo que ya tienes:
    nominado = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="nominaciones_recibidas"
    )
    nominado_secundario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="nominaciones_recibidas_como_pareja",
        null=True,
        blank=True,
    )

    # NUEVO: lista flexible de participantes (2/3/4 para clips, y también para pareja)
    participantes = models.ManyToManyField(
        User,
        related_name="participaciones_en_nominaciones",
        blank=True,
    )

    nominado_por = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="nominaciones_hechas"
    )

    # Para people: motivo/hazaña. Para clip: puedes usarlo como descripción corta si quieres.
    hazana = models.TextField("Hazaña de la nominación")

    # NUEVO: campos del Clip del Año (solo se usan si award.award_type == 'clip')
    clip_title = models.CharField(max_length=150, blank=True, default="")
    clip_url = models.URLField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nominación"
        verbose_name_plural = "Nominaciones"

        # 👇 IMPORTANTE: quitamos UniqueConstraint (te rompe Clip del Año)
        constraints = []

    def __str__(self):
        return f"{self.nominado} nominado a {self.award} por {self.nominado_por}"
    
class AwardSuggestion(models.Model):
    """
    Sugerencias de premios hechas por los usuarios.
    Ahora también guardamos: tipo de premio y modalidad de participantes por candidato.
    """

    # ✅ mismas opciones que Award
    AWARD_TYPES = (
        ("people", "Personas"),
        ("clip", "Clip / Vídeo"),
    )

    # ✅ 1 / 2 / varios
    NOMINATION_MODES = (
        ("single", "1 participante"),
        ("pair", "2 participantes"),
        ("multi", "Varios (3+)"),
    )

    titulo = models.CharField(max_length=100)
    resumen = models.CharField(max_length=255)
    descripcion = models.TextField()

    # NUEVO
    award_type = models.CharField(
        max_length=20,
        choices=AWARD_TYPES,
        default="people",
    )
    nomination_mode = models.CharField(
        max_length=20,
        choices=NOMINATION_MODES,
        default="single",
        help_text="Cuántos participantes puede tener cada candidato (1 / 2 / varios)."
    )
    max_participants = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Solo si nomination_mode='multi'. Ej: 4."
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="award_suggestions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    is_reviewed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sugerencia: {self.titulo} (por {self.created_by})"
    
class Vote(models.Model):
    award = models.ForeignKey(Award, on_delete=models.CASCADE, related_name="votes")
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["award", "voter"],
                condition=Q(is_active=True),
                name="unique_active_vote_per_award_and_user",
            )
        ]

    def __str__(self):
        return f"{self.voter} → {self.nomination} ({self.award})"