from django.core.management.base import BaseCommand

from account.models import User, UserRole


class Command(BaseCommand):
    help = "Create user with specific role"

    def add_arguments(self, parser):
        parser.add_argument(
            "--role",
            type=str,
            required=True,
            choices=[
                UserRole.TEACHER,
                UserRole.EDUCATION,
                UserRole.FINANCE,
            ],
        )

        parser.add_argument("--username", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--phone", type=str)
        parser.add_argument("--emergency-phone", type=str)

    def handle(self, *args, **options):
        role = options["role"]

        phone = options.get("phone")
        emergency_phone = options.get("emergency_phone")

        if role == UserRole.TEACHER:
            if not phone:
                self.stdout.write(
                    self.style.ERROR(
                        "Phone is required for teachers."
                    )
                )
                return

            if not emergency_phone:
                self.stdout.write(
                    self.style.ERROR(
                        "Emergency phone is required for teachers."
                    )
                )
                return

        user = User.objects.create_user(
            username=options["username"],
            password=options["password"],
            phone=phone,
            emergency_phone=emergency_phone,
            role=role,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"User {user.username} created with role {user.role}"
            )
        )