# awards/management/commands/seed_clip_del_ano.py
from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from awards.models import Award, Nomination


CLIPS = [
    "churu_vs_salva.mp4",
    "cinco_lobitos.mp4",
    "la_bomba.mp4",
    "lo_tiro_yo.mp4",
    "muerete_muerete.mp4",
    "no_es_justo.mp4",
    "punchikete.mp4",
    "sal_de_aqui_tonto.mp4",
    "vamos_mis_citrones.mp4",
]


def pretty_title(filename: str) -> str:
    stem = Path(filename).stem
    # "churu_vs_salva" -> "Churu Vs Salva"
    return stem.replace("_", " ").strip().title()


def build_media_url(relative_path: str) -> str:
    """
    Devuelve una URL relativa tipo /media/clips/xxx.mp4
    respetando MEDIA_URL.
    """
    media_url = settings.MEDIA_URL or "/media/"
    if not media_url.endswith("/"):
        media_url += "/"

    # urljoin maneja bien barras dobles
    return urljoin(media_url, relative_path.lstrip("/"))


class Command(BaseCommand):
    help = "Crea el premio 'Clip del Año' (award_type='clip') y precarga las nominaciones de clips."

    def add_arguments(self, parser):
        parser.add_argument(
            "--creator",
            type=str,
            default=None,
            help="Username del usuario que figurará como 'nominado_por' (y también 'nominado' por compatibilidad). "
                 "Si no se pasa, usa el primer superuser; si no hay, el primer usuario.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No escribe en BD, solo muestra lo que haría.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Si el premio ya existe, actualiza sus campos base igualmente.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        creator_username: str | None = options["creator"]
        force: bool = options["force"]

        User = get_user_model()

        # --- Resolver usuario creador ---
        creator = None
        if creator_username:
            creator = User.objects.filter(username=creator_username).first()
            if not creator:
                raise CommandError(f"No existe ningún usuario con username='{creator_username}'")
        else:
            creator = User.objects.filter(is_superuser=True).order_by("id").first() or User.objects.order_by("id").first()

        if not creator:
            raise CommandError("No hay usuarios en la BD. Crea al menos uno (o un superuser) y reintenta.")

        # --- Comprobar ficheros en MEDIA_ROOT/clips ---
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root:
            raise CommandError("settings.MEDIA_ROOT no está configurado. No puedo validar media/clips.")

        clips_dir = Path(media_root) / "clips"
        missing = [f for f in CLIPS if not (clips_dir / f).exists()]
        if missing:
            self.stdout.write(self.style.WARNING("⚠️  Faltan estos clips en MEDIA_ROOT/clips:"))
            for f in missing:
                self.stdout.write(self.style.WARNING(f"   - {clips_dir / f}"))
            self.stdout.write(self.style.WARNING("Seguiré igualmente (se crean las nominaciones), pero revisa los archivos."))

        # --- Crear/actualizar premio ---
        award_defaults = dict(
            resumen="El clip más mítico del año (preseleccionado).",
            descripcion=(
                "Premio especial: los clips están cerrados (no se pueden subir). "
                "Solo se vota al mejor clip."
            ),
            activo=True,
            allow_nominations=False,     # cerrado
            allow_voting=True,           # votación abierta (ajusta si quieres)
            show_results=False,          # oculto hasta gala (ajusta si quieres)
            allow_pair_nominations=False,
            award_type="clip",
        )

        with transaction.atomic():
            award, created = Award.objects.get_or_create(
                titulo="Clip del Año",
                defaults=award_defaults,
            )

            if (not created and force) or (not created and award.award_type != "clip"):
                # Si existía con otra config, lo dejamos bien
                for k, v in award_defaults.items():
                    setattr(award, k, v)
                if not dry_run:
                    award.save()

            if dry_run:
                self.stdout.write(self.style.NOTICE(f"[DRY-RUN] Premio: {'CREARÍA' if created else 'USARÍA'} '{award.titulo}' (id={award.id})"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✅ Premio: {'CREADO' if created else 'OK'} '{award.titulo}' (id={award.id})"))

            # --- Crear nominaciones por clip ---
            created_n = 0
            updated_n = 0

            for filename in CLIPS:
                clip_rel = f"clips/{filename}"
                clip_url = build_media_url(clip_rel)
                clip_title = pretty_title(filename)

                # Criterio de unicidad práctico: (award + clip_url)
                nom = Nomination.objects.filter(award=award, clip_url=clip_url).first()

                if not nom:
                    if dry_run:
                        created_n += 1
                        self.stdout.write(f"[DRY-RUN] CREARÍA nominación: {clip_title} -> {clip_url}")
                        continue

                    nom = Nomination.objects.create(
                        award=award,
                        nominado=creator,          # compatibilidad (no se usa en UI para clip)
                        nominado_por=creator,
                        hazana="Clip oficial preseleccionado.",
                        clip_title=clip_title,
                        clip_url=clip_url,
                        is_active=True,
                    )
                    created_n += 1
                else:
                    # Si ya existe, actualizamos título/hazana/is_active por si cambió algo
                    changed = False
                    if nom.clip_title != clip_title:
                        nom.clip_title = clip_title
                        changed = True
                    if not nom.hazana:
                        nom.hazana = "Clip oficial preseleccionado."
                        changed = True
                    if not nom.is_active:
                        nom.is_active = True
                        changed = True

                    if changed:
                        updated_n += 1
                        if dry_run:
                            self.stdout.write(f"[DRY-RUN] ACTUALIZARÍA nominación: {clip_title} -> {clip_url}")
                        else:
                            nom.save()

            if dry_run:
                self.stdout.write(self.style.NOTICE(f"[DRY-RUN] Resumen: {created_n} nominaciones se crearían, {updated_n} se actualizarían."))
            else:
                self.stdout.write(self.style.SUCCESS(f"🎬 Resumen: {created_n} nominaciones creadas, {updated_n} actualizadas."))
                self.stdout.write(self.style.SUCCESS(f"👤 Usuario creador usado: {creator.username} (id={creator.id})"))