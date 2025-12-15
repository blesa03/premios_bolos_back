from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = "Asigna apodo, descripción corta y larga a los usuarios de Bolos de Chill"

    def handle(self, *args, **kwargs):
        perfiles = {
            "abel": {
                "nickname": "Abelon",
                "short_bio": "Influencer de tupper",
                "long_bio": "Aprobó bachiller por error del sistema. Le van las mujeres y ahora vende vapers como si el fin del mundo fuese mañana."
            },
            "huevos": {
                "nickname": "Webos",
                "short_bio": "Vaper dealer",
                "long_bio": "Socio de Bartolo en el imperio de vapers ilegales. Si un día lo detienen, será por visionario, no por delincuente."
            },
            "barto": {
                "nickname": "Titaneo",
                "short_bio": "CEO del humo",
                "long_bio": "Mitad empresario, mitad churrero del vaper. Si puede venderte algo, te lo vende. Si no, también."
            },
            "churuco": {
                "nickname": "Charco",
                "short_bio": "Rata premium",
                "long_bio": "Ni bebe ni apuesta, pero es más rata que la peste medieval. Turquía le espera para ponerle un césped que ni el Bernabéu."
            },
            "campoy": {
                "nickname": "Fran goles",
                "short_bio": "Extranjero fake",
                "long_bio": "Ha decidido ser extranjero por deporte. Adicto al LoL, experto en NBA sin ver partidos y fumador profesional."
            },
            "miguel": {
                "nickname": "Pelos Albox",
                "short_bio": "Corta, peina, liga",
                "long_bio": "Guapo, motero y peluquero; el único del grupo que podría salir en LinkedIn sin dar miedo."
            },
            "paco": {
                "nickname": "Kiko",
                "short_bio": "¿La ruleta paga?",
                "long_bio": "Jugador de LoL enfermo. Lleva semanas diciendo: 'Me ha pagado 20€'. Si tanto paga… ¿por qué sigues pobre, Paco?"
            },

            "adrian": {
                "nickname": "Feliu",
                "short_bio": "Mandarino Prime",
                "long_bio": "Toca una tragaperras y llora. Vive entre cosen y apuestas deportivas. Si la ruleta fuese mujer, ya estarían casados."
            },
            "primo": {
                "nickname": "Prime",
                "short_bio": "Me la pela vibes",
                "long_bio": "Travel influencer de Turquía. No apuesta, pero está enganchao. Fuma como si cobrara por anuncio. Un icono del desapego."
            },
            "rigodon": {
                "nickname": "Rigodown",
                "short_bio": "Alcóholico anónimo",
                "long_bio": "La fiesta hecha persona. Coches rotos, alcohol y música. Siempre en primera línea del desastre, nunca en casa temprano."
            },
            "sorey": {
                "nickname": "Sorey07",
                "short_bio": "Yasuo enjoyer",
                "long_bio": "Main Yasuo, mártir del tilt. Capaz de tirar partidas solo con existir. Su espíritu de int nos acompaña siempre."
            },
            "tankete": {
                "nickname": "Tan Keta",
                "short_bio": "Culto al porro",
                "long_bio": "Su religión: fumarse uno antes de la partida… y otro después porque salió mal. Leyenda viva del humo."
            },
            "victor": {
                "nickname": "Fakir",
                "short_bio": "Riñón 200%",
                "long_bio": "Bebe como si tuviera cinco riñones. Bebe lo que sea, cuando sea. Responsable según él, peligro público según todos."
            },
            "villa": {
                "nickname": "El Compadrico",
                "short_bio": "Autismo Deluxe",
                "long_bio": "Patrón de los que no miran a los ojos. Protector de silencios incómodos. Aparece una vez al año y toca sufrir."
            },
            "tore": {
                "nickname": "EL GOAT",
                "short_bio": "Prime eterno",
                "long_bio": "Se mantiene en prime desde 2017. Sus peleas con la Vivi son más épicas que cualquier final de Worlds. Una leyenda real."
            },
        }

        for username, data in perfiles.items():
            try:
                user = User.objects.get(username=username)
                user.nickname = data["nickname"]
                user.short_bio = data["short_bio"][:20]
                user.long_bio = data["long_bio"][:120]
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Perfil actualizado: {username}"))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Usuario no existe: {username}"))

        self.stdout.write(self.style.SUCCESS("🚀 Perfiles actualizados correctamente"))