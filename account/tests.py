import jwt
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APITestCase

from .models import User


class JWTLoginTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="jwt_teacher",
            password="12345678",
            role="teacher",
            phone="09333333335",
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "jwt_teacher",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "jwt_teacher",
                "password": "wrong_password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_login_wrong_username(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "wrong_username",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_login_contains_role_in_token(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "jwt_teacher",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        access_token = response.data["access"]

        decoded_token = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        self.assertEqual(decoded_token["role"], "teacher")    

class PermissionTest(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher_test",
            password="12345678",
            role="teacher",
            phone="09111111111",
        )

        self.finance = User.objects.create_user(
            username="finance_test",
            password="12345678",
            role="finance",
            phone="09222222222",
        )

    def test_teacher_can_access_teacher_test_api(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get("/api/auth/teacher-test/")

        self.assertEqual(response.status_code, 200)

    def test_finance_cannot_access_teacher_test_api(self):
        self.client.force_authenticate(user=self.finance)

        response = self.client.get("/api/auth/teacher-test/")

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_access_teacher_api(self):
        response = self.client.get(
            "/api/auth/teacher-test/"
        )

        self.assertEqual(response.status_code, 401)    
class CreateUserCommandTest(APITestCase):

    def test_create_user_command(self):
        call_command(
            "create_user",
            username="command_teacher",
            password="12345678",
            phone="09333333333",
            role="teacher",
        )

        user = User.objects.get(username="command_teacher")

        self.assertEqual(user.role, "teacher")
        self.assertEqual(user.phone, "09333333333") 

    def test_create_user_with_invalid_role(self):
        with self.assertRaises(CommandError):
            call_command(
                "create_user",
                username="invalid_role_user",
                password="12345678",
                phone="09333333336",
                role="student",
            )

    def test_create_user_with_duplicate_username(self):
        User.objects.create_user(
            username="duplicate_user",
            password="12345678",
            phone="09333333337",
            role="teacher",
        )

        with self.assertRaises(Exception):
            call_command(
                "create_user",
                username="duplicate_user",
                password="12345678",
                phone="09333333338",
                role="teacher",
            )