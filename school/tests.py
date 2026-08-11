from rest_framework.test import APITestCase

from account.models import User
from school.models import School


class SchoolAPITest(APITestCase):

    def setUp(self):
        self.education = User.objects.create_user(
            username="school_education",
            password="12345678",
            role="education",
            phone="09123456701",
        )

        self.teacher = User.objects.create_user(
            username="school_teacher",
            password="12345678",
            role="teacher",
            phone="09123456702",
        )

        self.finance = User.objects.create_user(
            username="school_finance",
            password="12345678",
            role="finance",
            phone="09123456703",
        )

        self.school = School.objects.create(
            name="Test School"
        )

        self.url = "/api/schools/"

    def test_education_can_list_schools(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["name"],
            "Test School",
        )

    def test_anonymous_user_cannot_list_schools(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401) 

    def test_teacher_cannot_list_schools(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403) 

    def test_finance_cannot_list_schools(self):
        self.client.force_authenticate(user=self.finance)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403) 

    def test_education_can_create_school(self):
        self.client.force_authenticate(user=self.education)

        data = {
        "name": "New School",
        }

        response = self.client.post(
        self.url,
        data,
        format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New School")

        self.assertTrue(
        School.objects.filter(name="New School").exists()
        ) 

    def test_education_cannot_create_school_without_name(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.post(
        self.url,
        {},
        format="json",
        )

        self.assertEqual(response.status_code, 400) 

    def test_education_cannot_create_school_with_duplicate_name(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.post(
        self.url,
        {"name": "Test School"},
        format="json",
        )

        self.assertEqual(response.status_code, 400) 

    def test_education_can_retrieve_school(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(
        f"{self.url}{self.school.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.school.id)
        self.assertEqual(response.data["name"], "Test School")  

    def test_education_cannot_retrieve_nonexistent_school(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(
        f"{self.url}99999/"
        )

        self.assertEqual(response.status_code, 404) 

    def test_education_can_update_school(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.patch(
        f"{self.url}{self.school.id}/",
        {"name": "Updated School"},
        format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated School")

        self.school.refresh_from_db()
        self.assertEqual(self.school.name, "Updated School")

    def test_education_cannot_update_school_with_duplicate_name(self):
        self.client.force_authenticate(user=self.education)

        second_school = School.objects.create(
            name="Second School"
        )

        response = self.client.patch(
            f"{self.url}{second_school.id}/",
            {"name": "Test School"},
            format="json",
        )

        self.assertEqual(response.status_code, 400) 

    def test_education_can_soft_delete_school(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.delete(
            f"{self.url}{self.school.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.school.refresh_from_db()

        self.assertTrue(self.school.is_deleted)

    def test_soft_deleted_school_not_in_list(self):
        self.client.force_authenticate(user=self.education)

        self.school.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0) 

    def test_soft_deleted_school_still_exists_in_database(self):
        self.client.force_authenticate(user=self.education)

        self.school.delete()

        self.school.refresh_from_db()

        self.assertTrue(
            School.objects.filter(id=self.school.id).exists()
        )
        self.assertTrue(self.school.is_deleted)                                         