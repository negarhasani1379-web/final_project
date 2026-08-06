from django.core.management.base import BaseCommand,

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
        parser.add_argument("--phone", type=str, required=True)

    def handle(self, *args, **options):
        role = options["role"]

        user = User.objects.create_user(
            username=options["username"],
            password=options["password"],
            phone=options["phone"],
            role=role,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"User {user.username} created with role {user.role}"
            )
        )