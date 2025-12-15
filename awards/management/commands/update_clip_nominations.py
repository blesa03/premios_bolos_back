# awards/management/commands/update_clip_nominations.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from awards.models import Award, Nomination


@dataclass(frozen=True)
class ClipSpec:
    filename: str
    usernames: List[str]


CLIPS: List[ClipSpec] = [
    ClipSpec("churu_vs_salva.mp4", ["churuco", "tore"]),
    ClipSpec("cinco_lobitos.mp4", ["villa"]),
    ClipSpec("la_bomba.mp4", ["sorey"]),
    ClipSpec("lo_tiro_yo.mp4", ["churuco"]),
    ClipSpec("muerete_muerete.mp4", ["campoy"]),
    ClipSpec("no_es_justo.mp4", ["campoy"]),
    ClipSpec("punchikete.mp4", ["campoy"]),
    ClipSpec("sal_de_aqui_tonto.mp4", ["churuco"]),
    ClipSpec("vamos_mis_citrones.mp4", ["campoy", "lopez", "churuco"]),
]


def pretty_title_from_filename(filename: str) -> str:
    base = filename.rsplit(".", 1)[0]
    base = base.replace("_", " ").strip()
    # Mantener "vs" en minúscula si está
    parts = base.split()
    parts = [p.lower() if p.lower() == "vs" else (p[:1].upper() + p[1:]) for p in parts]
    return " ".join(parts)


def media_clip_url(filename: str) -> str:
    # Guardamos URL relativa (tipo /media/clips/xxx.mp4). No valida en save() y te vale en front.
    media_url = getattr(settings, "MEDIA_URL", "/media/")
    media_url = media_url if media_url.endswith("/") else media_url + "/"
    return f"{media_url}clips/{filename}"


class Command(BaseCommand):
    help = (
        "Actualiza/crea nominaciones del premio 'Clip del año' y asigna participantes "
        "(y compatibilidad nominado/nominado_secundario)."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        # 1) Buscar el premio de clips
        award = (
            Award.objects.filter(award_type="clip")
            .filter(Q(titulo__iexact="Clip del año") | Q(titulo__iexact="Clip del Año") | Q(titulo__icontains="clip"))
            .order_by("id")
            .first()
        )
        if not award:
            raise CommandError(
                "No encuentro un Award de tipo 'clip'. Crea el premio primero (award_type='clip')."
            )

        # 2) Usuario “nominado_por” para creaciones (si faltan)
        nominator = (
            User.objects.filter(is_superuser=True).order_by("id").first()
            or User.objects.filter(is_staff=True).order_by("id").first()
            or User.objects.order_by("id").first()
        )
        if not nominator:
            raise CommandError("No hay usuarios en la BD. Necesito al menos 1 usuario para 'nominado_por'.")

        # 3) Resolver usernames
        wanted_usernames = sorted({u for spec in CLIPS for u in spec.usernames})
        users_by_username: Dict[str, object] = {
            u.username: u for u in User.objects.filter(username__in=wanted_usernames)
        }
        missing = [u for u in wanted_usernames if u not in users_by_username]
        if missing:
            raise CommandError(
                "Faltan estos usernames en la BD: "
                + ", ".join(missing)
                + ". Crea esos usuarios o corrige los nombres."
            )

        updated = 0
        created = 0

        for spec in CLIPS:
            title = pretty_title_from_filename(spec.filename)
            url = media_clip_url(spec.filename)
            base = spec.filename.rsplit(".", 1)[0]

            participants = [users_by_username[u] for u in spec.usernames]
            primary = participants[0]
            secondary = participants[1] if len(participants) > 1 else None

            # 4) Encontrar la nominación del clip (por URL o por título)
            nomination = (
                Nomination.objects.filter(award=award)
                .filter(
                    Q(clip_url__endswith=spec.filename)
                    | Q(clip_title__iexact=title)
                    | Q(clip_title__icontains=base.replace("_", " "))
                )
                .order_by("id")
                .first()
            )

            # 5) Si no existe, crearla
            if not nomination:
                nomination = Nomination.objects.create(
                    award=award,
                    nominado=primary,
                    nominado_secundario=secondary,
                    nominado_por=nominator,
                    hazana="",  # si quieres, mete una descripción por defecto aquí
                    clip_title=title,
                    clip_url=url,
                    is_active=True,
                )
                nomination.participantes.set(participants)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"[CREATED] {spec.filename} -> {', '.join(spec.usernames)}"))
                continue

            # 6) Si existe, actualizar campos + M2M
            changed = False

            if nomination.clip_title.strip() == "":
                nomination.clip_title = title
                changed = True

            if nomination.clip_url.strip() == "":
                nomination.clip_url = url
                changed = True

            # Compatibilidad: nominado / nominado_secundario
            if nomination.nominado_id != primary.id:
                nomination.nominado = primary
                changed = True

            # Para clips de 3/4 participantes, guardamos el segundo aquí y el resto en M2M
            if secondary is None:
                if nomination.nominado_secundario_id is not None:
                    nomination.nominado_secundario = None
                    changed = True
            else:
                if nomination.nominado_secundario_id != secondary.id:
                    nomination.nominado_secundario = secondary
                    changed = True

            if changed:
                nomination.save(update_fields=["clip_title", "clip_url", "nominado", "nominado_secundario"])
                updated += 1

            nomination.participantes.set(participants)
            self.stdout.write(self.style.SUCCESS(f"[OK] {spec.filename} -> {', '.join(spec.usernames)}"))

        self.stdout.write(
            self.style.WARNING(
                f"\nResumen: {created} creadas, {updated} actualizadas (M2M se fuerza siempre). Premio: #{award.id} {award.titulo}"
            )
        )