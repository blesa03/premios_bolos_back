from django.core.management.base import BaseCommand
from users.models import Usuario


class Command(BaseCommand):
    help = "Añade usuarios iniciales al sistema"

    def handle(self, *args, **options):
        users = [
            {
                "username": "abel",
                "password": "abel.123.",
                "nickname": "Abelon",
                "short_bio": "Influencer de tupper",
                "long_bio": "Aprobó bachiller por error del sistema. Le van las mujeres y ahora vende vapers como si el fin del mundo fuese mañana.",
                "avatar": "avatars/abel_3PLBXL7.jpeg",
            },
            {
                "username": "huevos",
                "password": "huevos.123.",
                "nickname": "Webos",
                "short_bio": "Vaper dealer",
                "long_bio": "Socio de Bartolo en el imperio de vapers ilegales. Si un día lo detienen, será por visionario, no por delincuente.",
                "avatar": "avatars/huevos.jpeg",
            },
            {
                "username": "barto",
                "password": "barto.123.",
                "nickname": "Titaneo",
                "short_bio": "CEO del humo",
                "long_bio": "Mitad empresario, mitad churrero del vaper. Si puede venderte algo, te lo vende. Si no, también.",
                "avatar": "avatars/barto_UbgQB2r.png",
            },
            {
                "username": "lopez",
                "password": "lopez.123.",
                "nickname": "Jugador de buscachinas",
                "short_bio": "Jäger, humo y tilt",
                "long_bio": "Cigarro en mano, vaper cargado, Jäger con Red Bull y ranked de LoL mientras fantasea con chicas asiáticas",
                "avatar": "avatars/lopez.jpeg",
            },
            {
                "username": "churuco",
                "password": "churuco.123.",
                "nickname": "Charco",
                "short_bio": "Rata premium",
                "long_bio": "Ni bebe ni apuesta, pero es más rata que la peste medieval. Turquía le espera para ponerle un césped que ni el Bernabéu.",
                "avatar": "avatars/churu_ZtVRPgE.jpeg",
            },
            {
                "username": "adrian",
                "password": "adrian.123.",
                "nickname": "Feliu",
                "short_bio": "Mandarino Prime",
                "long_bio": "Toca una tragaperras y llora. Vive entre cosen y apuestas deportivas. Si la ruleta fuese mujer, ya estarían casados.",
                "avatar": "avatars/adrian.jpeg",
            },
            {
                "username": "miguel",
                "password": "miguel.123.",
                "nickname": "Pelos Albox",
                "short_bio": "Corta, peina, liga",
                "long_bio": "Guapo, motero y peluquero; el único del grupo que podría salir en LinkedIn sin dar miedo.",
                "avatar": "avatars/miguel.jpeg",
            },
            {
                "username": "pablo",
                "password": "pablo.123.",
                "nickname": "El Admin",
                "short_bio": "Pija radioactiva",
                "long_bio": "Pa descripciones largas toa su pija. Desde que le picó una cucaracha radioactiva su vida no volvió a ser la misma.",
                "avatar": "avatars/pablo_6eXOapT.jpeg",
            },
            {
                "username": "paco",
                "password": "paco.123.",
                "nickname": "Kiko",
                "short_bio": "¿La ruleta paga?",
                "long_bio": "Jugador de LoL enfermo. Lleva semanas diciendo: 'Me ha pagado 20€'. Si tanto paga… ¿por qué sigues pobre, Paco?",
                "avatar": "avatars/paco.jpeg",
            },
            {
                "username": "campoy",
                "password": "campoy.123.",
                "nickname": "Fran goles",
                "short_bio": "Extranjero fake",
                "long_bio": "Ha decidido ser extranjero este año. Adicto al LoL, experto en NBA sin ver partidos y fumador profesional.",
                "avatar": "avatars/campoy.jpeg",
            },
            {
                "username": "primo",
                "password": "primo.123.",
                "nickname": "Prime",
                "short_bio": "Me la pela vibes",
                "long_bio": "Travel influencer de Turquía. No apuesta, pero está enganchao. Fuma como si cobrara por anuncio. Un icono del desapego.",
                "avatar": "avatars/primo.jpeg",
            },
            {
                "username": "rigodon",
                "password": "rigodon.123.",
                "nickname": "Rigodown",
                "short_bio": "Alcóholico anónimo",
                "long_bio": "La fiesta hecha persona. Coches rotos, alcohol y música. Siempre en primera línea del desastre, nunca en casa temprano.",
                "avatar": "avatars/rigodon.jpeg",
            },
            {
                "username": "sorey",
                "password": "sorey.123.",
                "nickname": "Sorey07",
                "short_bio": "Yasuo enjoyer",
                "long_bio": "Main Yasuo, mártir del tilt. Capaz de tirar partidas solo con existir. Su espíritu de int nos acompaña siempre.",
                "avatar": "avatars/sorey.jpeg",
            },
            {
                "username": "tankete",
                "password": "tankete.123.",
                "nickname": "TanKETA",
                "short_bio": "Culto al porro",
                "long_bio": "Su religión: fumarse uno antes de la partida… y otro después porque salió mal. Leyenda viva del humo.",
                "avatar": "avatars/tankete.jpeg",
            },
            {
                "username": "victor",
                "password": "victor.123.",
                "nickname": "Jefe Victorio",
                "short_bio": "Riñón 200%",
                "long_bio": "Bebe como si tuviera cinco riñones. Bebe lo que sea, cuando sea. Responsable según él, peligro público según todos.",
                "avatar": "avatars/victor.jpeg",
            },
            {
                "username": "villa",
                "password": "villa.123.",
                "nickname": "El Compadrico",
                "short_bio": "Autismo Deluxe",
                "long_bio": "Patrón de los que no miran a los ojos. Protector de silencios incómodos. Aparece una vez al año y toca sufrir.",
                "avatar": "avatars/villa.jpeg",
            },
            {
                "username": "tore",
                "password": "tore.123.",
                "nickname": "EL GOAT",
                "short_bio": "Prime eterno",
                "long_bio": "Se mantiene en prime desde 2017. Sus peleas con la Vivi son más épicas que cualquier final de Worlds. Una leyenda real.",
                "avatar": "avatars/tore.jpeg",
            },
        ]

        for u in users:
            user, created = Usuario.objects.get_or_create(
                username=u["username"],
                defaults={
                    "nickname": u["nickname"],
                    "short_bio": u["short_bio"],
                    "long_bio": u["long_bio"],
                    "avatar": u["avatar"],
                    "is_active": True,
                }
            )

            if created:
                user.set_password(u["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✔ Usuario creado: {u['username']}"))
            else:
                self.stdout.write(self.style.WARNING(f"⏭ Usuario ya existe: {u['username']}"))

        self.stdout.write(self.style.SUCCESS("✅ Script de usuarios finalizado"))