from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User

from .models import Term


class TermTest(TestCase):
    def test_create_term_with_valid_dates(self):
        term = Term(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        term.full_clean()
        term.save()

        self.assertEqual(term.title, "Fall 2026")
        self.assertEqual(term.term_type, "normal")

    def test_term_end_date_cannot_be_before_start_date(self):
        term = Term(
            title="Invalid Term",
            start_date="2026-09-01",
            end_date="2026-08-01",
            term_type="normal",
        )

        with self.assertRaises(ValidationError):
            term.full_clean() 

    def test_create_summer_term(self):
        term = Term(
            title="Summer 2026",
            start_date="2026-06-01",
            end_date="2026-08-31",
            term_type="summer",
        )

        term.full_clean()
        term.save()

        self.assertEqual(term.term_type, "summer") 

    def test_term_type_must_be_valid(self):
        term = Term(
            title="Invalid Type Term",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="winter",
        )

        with self.assertRaises(ValidationError):
            term.full_clean() 

    def test_term_title_is_required(self):
        term = Term(
            title="",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        with self.assertRaises(ValidationError):
            term.full_clean() 

class TermAPITest(APITestCase):

    def setUp(self):
        self.education = User.objects.create_user(
            username="education_test",
            password="Test12345",
            role="education",
        )

        self.teacher = User.objects.create_user(
            username="teacher_test",
            password="Test12345",
            role="teacher",
        )

        self.term_data = {
            "title": "Fall 2026",
            "start_date": "2026-09-01",
            "end_date": "2027-01-20",
            "term_type": "normal",
        }

        self.url = "/api/terms/"


    def test_education_can_create_term(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.post(
            self.url,
            self.term_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Term.objects.count(), 1)
        self.assertEqual(response.data["title"], "Fall 2026")

    def test_teacher_cannot_create_term(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            self.url,
            self.term_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Term.objects.count(), 0) 

    def test_unauthenticated_user_cannot_create_term(self):
        response = self.client.post(
            self.url,
            self.term_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Term.objects.count(), 0) 

    def test_education_can_list_terms(self):
        self.client.force_authenticate(user=self.education)

        Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Fall 2026")

    def test_education_can_retrieve_term(self):
        self.client.force_authenticate(user=self.education)

        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        response = self.client.get(f"{self.url}{term.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], term.id)
        self.assertEqual(response.data["title"], "Fall 2026") 

    def test_create_term_with_invalid_dates(self):
        self.client.force_authenticate(user=self.education)

        data = {
            "title": "Invalid Term",
            "start_date": "2026-09-01",
            "end_date": "2026-08-01",
            "term_type": "normal",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Term.objects.count(), 0) 

    def test_create_term_with_invalid_term_type(self):
        self.client.force_authenticate(user=self.education)

        data = {
            "title": "Invalid Type Term",
            "start_date": "2026-09-01",
            "end_date": "2027-01-20",
            "term_type": "winter",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Term.objects.count(), 0) 


          

