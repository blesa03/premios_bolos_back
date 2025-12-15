from django.core.management.base import BaseCommand
from awards.models import Award

PREMIOS_ACTUALIZADOS = [
    {
        "titulo": "Más inoperante del año",
        "resumen": "Para el que no acierta ni queriendo.",
        "descripcion": (
            "Un homenaje al talento innato de no hacer nada bien. "
            "Si existe un botón que no hay que tocar, esta persona lo toca. "
            "Si hay una decisión mala, la elige. Si hay una opción peor, también la elige. "
            "Maestro del desastre técnico y emocional."
        )
    },
    {
        "titulo": "Más gay del grupo",
        "resumen": "No hay gays, pero el premio existe porque somos así.",
        "descripcion": (
            "Se entrega al integrante cuya esencia desprende más color que una bandera "
            "arcoíris mojada. No hace falta justificarlo: simplemente lo es, y todos lo sabemos."
        )
    },
    {
        "titulo": "Pulmones más negros",
        "resumen": "Para el fumador premium del grupo.",
        "descripcion": (
            "Tabaco, vaper, porros, cachimba… si quema, se lo fuma. "
            "Tiene más nicotina en sangre que un estanco. "
            "Cuando respira, el aire pierde calidad. Un referente del sector."
        )
    },
    {
        "titulo": "Más alcohólico",
        "resumen": "Al que vive más en la barra que en su casa.",
        "descripcion": (
            "No bebe: marida la vida con etanol. Su hígado pide un sindicato propio. "
            "El camarero sabe su nombre, su DNI y su número de pie."
        )
    },
    {
        "titulo": "Más mandarino",
        "resumen": "El pagafantas máximo, 100% domado.",
        "descripcion": (
            "No toma decisiones: las recibe por WhatsApp. "
            "Está más controlado que un preso en tercer grado. Ídolo caído del “sí cariño”."
        )
    },
    {
        "titulo": "Pareja del año",
        "resumen": "Para la dupla más icónica del año.",
        "descripcion": (
            "Puede ser una pareja real o una pareja inventada por el grupo porque nos hace gracia. "
            "Lo importante es que su dinámica nos dio vida durante el año."
        )
    },
    {
        "titulo": "Más ludópata",
        "resumen": "Para quien ve una tragaperras y suda emoción.",
        "descripcion": (
            "Vive entre apuestas, slots, combinadas imposibles y “esta entra fijo”. "
            "Lo pierde todo, pero sigue sonriendo. Un guerrero del azar."
        )
    },
    {
        "titulo": "Cliente más fiel de Bartolo",
        "resumen": "Literalmente el que más le compra a Barto.",
        "descripcion": (
            "Vaper, recambio, líquido, accesorio, oferta, promo, pack ahorro… "
            "Si existe, esta persona ya lo compró. Mantiene la economía circular del grupo."
        )
    },
    {
        "titulo": "Best performance of the year",
        "resumen": "Para el momento más legendario del año.",
        "descripcion": (
            "Ese clip, esa frase, esa jugada, ese momento que se va a recordar en el grupo "
            "hasta que alguien muera. El pico creativo absoluto del bolerismo."
        )
    },
]

class Command(BaseCommand):
    help = "Actualiza los textos de resumen y descripción de los premios existentes"

    def handle(self, *args, **kwargs):
        for p in PREMIOS_ACTUALIZADOS:
            try:
                award = Award.objects.get(titulo=p["titulo"])
                award.resumen = p["resumen"]
                award.descripcion = p["descripcion"]
                award.save()
                self.stdout.write(self.style.SUCCESS(f"✔ Premió actualizado: {p['titulo']}"))
            except Award.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"✘ No existe en BD: {p['titulo']}"))

        self.stdout.write(self.style.SUCCESS("🎉 Premios actualizados correctamente"))