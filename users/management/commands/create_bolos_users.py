from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Crea los usuarios de Bolos de Chill con sus contraseñas por defecto."

    def handle(self, *args, **options):
        usernames = [
            "abel",
            "huevos",
            "barto",
            "lopez",
            "churuco",
            "adrian",
            "miguel",
            "pablo",
            "paco",
            "campoy",
            "primo",
            "rigodon",
            "sorey",
            "tankete",
            "victor",
            "villa",
            "tore"
        ]

        for username in usernames:
            password = f"{username}123."
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Creado: {username}  |  pass: {password}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Ya existía: {username} (no tocado)")
                )

        self.stdout.write(self.style.SUCCESS("👌 Comando terminado sin dramas."))