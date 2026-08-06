from rest_framework.test import APITestCase

from .models import User


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
