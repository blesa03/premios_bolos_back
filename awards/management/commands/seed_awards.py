from django.core.management.base import BaseCommand
from awards.models import Award

PREMIOS = [
    {
        "titulo": "Más inoperante del año",
        "resumen": "Un homenaje al talento para no hacer nada bien.",
        "descripcion": "Para ese individuo que convierte cualquier tarea sencilla en un boss final de Dark Souls."
    },
    {
        "titulo": "Más gay del grupo",
        "resumen": "No es literal, es que se te ve el plumero.",
        "descripcion": "Premio humorístico para el que más vibra en modo arcoíris según el resto del grupo."
    },
    {
        "titulo": "Pulmones más negros",
        "resumen": "Pulmones que ni en Gotham City.",
        "descripcion": "Reconocimiento al bolero cuya dieta se basa en vaper, tabaco, porros y cachimba."
    },
    {
        "titulo": "Más alcohólico",
        "resumen": "Un hígado que pide la jubilación.",
        "descripcion": "Dedicado al integrante que convierte cada evento en una cata de bebidas espirituosas."
    },
    {
        "titulo": "Más mandarino",
        "resumen": "El ‘sí, cariño’ del año.",
        "descripcion": "Para aquel que vive con GPS emocional dictado por su pareja."
    },
    {
        "titulo": "Pareja del año",
        "resumen": "Amor verdadero (o inventado por el grupo).",
        "descripcion": "Premio dedicado a las parejas oficiales y a las que existen solo en los memes."
    },
    {
        "titulo": "Más ludópata",
        "resumen": "Rasca y gana como filosofía de vida.",
        "descripcion": "Para el que no puede ver un 1% de probabilidad sin tirar el dinero."
    },
    {
        "titulo": "Cliente más fiel de Bartolo",
        "resumen": "Patrocinado por los vapers de barto.",
        "descripcion": "Para el que mantiene viva la economía de Bartolo con compras semanales."
    },
    {
        "titulo": "Best performance of the year",
        "resumen": "Actuación digna de un Oscar.",
        "descripcion": "Para el bolero que este año se marcó la mejor jugada, clip o momento épico."
    },
]


class Command(BaseCommand):
    help = "Inserta los premios base en la BD"

    def handle(self, *args, **options):

        for premio in PREMIOS:
            obj, created = Award.objects.get_or_create(
                titulo=premio["titulo"],
                defaults={
                    "resumen": premio["resumen"],
                    "descripcion": premio["descripcion"],
                    "activo": True,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Creado: {obj.titulo}"))
            else:
                self.stdout.write(self.style.WARNING(f"• Ya existía: {obj.titulo}"))

        self.stdout.write(self.style.SUCCESS("\nPremios insertados correctamente 🎉"))