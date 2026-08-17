from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User
from school.models import School

from .models import Class, TeacherAssignment, Term
from .serializers import TeacherAssignmentSerializer


########## TERM #########
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


    def test_education_can_update_term(self):
        self.client.force_authenticate(user=self.education)

        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )
        response = self.client.patch(
            f"{self.url}{term.id}/",
            {
                "title": "Fall 2026 Updated",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        term.refresh_from_db()
        self.assertEqual(term.title, "Fall 2026 Updated")      

    
    def test_update_term_with_invalid_dates(self):
        self.client.force_authenticate(user=self.education)

        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )
        response = self.client.patch(
            f"{self.url}{term.id}/",
            {
                "end_date": "2026-08-01",
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        term.refresh_from_db()
        self.assertEqual(term.end_date.isoformat(), "2027-01-20")


    def test_education_can_soft_delete_term(self):
        self.client.force_authenticate(user=self.education)

        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        response = self.client.delete(
            f"{self.url}{term.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        term.refresh_from_db()

        self.assertTrue(term.is_deleted)

    def test_deleted_term_is_not_in_term_list(self):
        self.client.force_authenticate(user=self.education)

        term = Term.objects.create(
            title="Deleted Term",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        term.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 



########## CLASS ######### 

class ClassTest(TestCase):
    def test_create_class_with_valid_session_duration(self):
        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        school = School.objects.create(
            name="Test School",
        )

        classroom = Class(
            title="English Literature",
            school=school,
            term=term,
            session_duration=90,
        )

        classroom.full_clean()
        classroom.save()

        self.assertEqual(classroom.title, "English Literature")
        self.assertEqual(classroom.session_duration, 90)

    def test_class_accepts_60_minutes(self):
        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        school = School.objects.create(
            name="Test School",
        )

        classroom = Class(
            title="English",
            school=school,
            term=term,
            session_duration=60,
        )

        classroom.full_clean()

    def test_class_accepts_120_minutes(self):
        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        school = School.objects.create(
            name="Test School",
        )

        classroom = Class(
            title="English",
            school=school,
            term=term,
            session_duration=120,
        )

        classroom.full_clean()

    def test_class_rejects_invalid_session_duration(self):
        term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        school = School.objects.create(
            name="Test School",
        )

        classroom = Class(
            title="English",
            school=school,
            term=term,
            session_duration=75,
        )

        with self.assertRaises(ValidationError):
            classroom.full_clean() 

class ClassAPITest(APITestCase):

    def setUp(self):
        self.education = User.objects.create_user(
            username="education_class_test",
            password="Test12345",
            role="education",
        )

        self.teacher = User.objects.create_user(
            username="teacher_class_test",
            password="Test12345",
            role="teacher",
        )

        self.school = School.objects.create(
            name="Test School",
        )

        self.term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        self.class_data = {
            "title": "English Literature",
            "school": self.school.id,
            "term": self.term.id,
            "session_duration": 90,
        }

        self.url = "/api/classes/"

    def test_education_can_create_class(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.post(
            self.url,
            self.class_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Class.objects.count(), 1)
        self.assertEqual(
            response.data["title"],
            "English Literature",
        )
        self.assertEqual(
            response.data["session_duration"],
            90,
        )

    def test_teacher_cannot_create_class(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            self.url,
            self.class_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Class.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_class(self):
        response = self.client.post(
            self.url,
            self.class_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(Class.objects.count(), 0)

    def test_education_can_list_classes(self):
        self.client.force_authenticate(user=self.education)

        Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "English Literature",
        )

    def test_education_can_retrieve_class(self):
        self.client.force_authenticate(user=self.education)

        classroom = Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        response = self.client.get(
            f"{self.url}{classroom.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            classroom.id,
        )

        self.assertEqual(
            response.data["title"],
            "English Literature",
        )

    def test_education_can_update_class(self):
        self.client.force_authenticate(user=self.education)

        classroom = Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        response = self.client.patch(
            f"{self.url}{classroom.id}/",
            {
                "title": "Advanced English Literature",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        classroom.refresh_from_db()

        self.assertEqual(
            classroom.title,
            "Advanced English Literature",
        )

    def test_update_class_with_invalid_session_duration(self):
        self.client.force_authenticate(user=self.education)

        classroom = Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        response = self.client.patch(
            f"{self.url}{classroom.id}/",
            {
                "session_duration": 75,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        classroom.refresh_from_db()

        self.assertEqual(
            classroom.session_duration,
            90,
        )

    def test_education_can_soft_delete_class(self):
        self.client.force_authenticate(user=self.education)

        classroom = Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        response = self.client.delete(
            f"{self.url}{classroom.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        classroom.refresh_from_db()

        self.assertTrue(classroom.is_deleted) 

    def test_deleted_class_is_not_in_class_list(self):
        self.client.force_authenticate(user=self.education)

        classroom = Class.objects.create(
            title="Deleted Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        classroom.delete()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        ) 

class ClassFilterAPITest(APITestCase):

    def setUp(self):
        self.education = User.objects.create_user(
            username="education_filter_test",
            password="Test12345",
            role="education",
        )

        self.teacher = User.objects.create_user(
            username="teacher_filter_test",
            password="Test12345",
            role="teacher",
        )

        self.other_teacher = User.objects.create_user(
            username="other_teacher_filter_test",
            password="Test12345",
            role="teacher",
        )

        self.school = School.objects.create(
            name="Test School",
        )

        self.other_school = School.objects.create(
            name="Other School",
        )

        self.term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        self.other_term = Term.objects.create(
            title="Summer 2026",
            start_date="2026-06-01",
            end_date="2026-08-31",
            term_type="summer",
        )

        self.classroom = Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        self.other_classroom = Class.objects.create(
            title="Mathematics",
            school=self.other_school,
            term=self.other_term,
            session_duration=60,
        )

        self.url = "/api/classes/"

    def test_education_can_filter_classes_by_school(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(
            f"{self.url}?school={self.school.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        ) 

    def test_education_can_filter_classes_by_term(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(
            f"{self.url}?term={self.term.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        ) 

    def test_education_can_filter_classes_by_teacher(self):
        self.client.force_authenticate(user=self.education)

        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.get(
            f"{self.url}?teacher={self.teacher.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        )

    def test_education_can_filter_classes_by_school_and_term(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(
            f"{self.url}?school={self.school.id}&term={self.term.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        )              

##########TeacherAssignment########## 
class TeacherAssignmentTest(APITestCase):

    def setUp(self):
        self.education = User.objects.create_user(
            username="education_assignment_test",
            password="Test12345",
            role="education",
        )

        self.teacher = User.objects.create_user(
            username="teacher_assignment_test",
            password="Test12345",
            role="teacher",
        )

        self.school = School.objects.create(
            name="Test School",
        )

        self.term = Term.objects.create(
            title="Fall 2026",
            start_date="2026-09-01",
            end_date="2027-01-20",
            term_type="normal",
        )

        self.classroom = Class.objects.create(
            title="English Literature",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

    def test_create_teacher_assignment_with_valid_dates(self):
        assignment = TeacherAssignment(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        assignment.full_clean()
        assignment.save()

        self.assertEqual(assignment.teacher, self.teacher)
        self.assertEqual(assignment.classroom, self.classroom)

    def test_assignment_end_date_cannot_be_before_start_date(self):
        assignment = TeacherAssignment(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-10-01",
            end_date="2026-09-01",
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_assignment_can_have_no_end_date(self):
        assignment = TeacherAssignment(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
        )

        assignment.full_clean()
        assignment.save()

        self.assertIsNone(assignment.end_date)

    def test_class_can_have_multiple_teacher_assignments(self):
        teacher_2 = User.objects.create_user(
        username="teacher_assignment_test_2",
        password="Test12345",
        role="teacher",
    )

        TeacherAssignment.objects.create(
        teacher=self.teacher,
        classroom=self.classroom,
        start_date="2026-09-01",
        end_date="2026-10-01",
    )

        TeacherAssignment.objects.create(
        teacher=teacher_2,
        classroom=self.classroom,
        start_date="2026-10-02",
        end_date="2026-11-01",
    )

        self.assertEqual(
            self.classroom.teacher_assignments.count(),
            2,
        ) 

    def test_serializer_accepts_valid_assignment(self):
        serializer = TeacherAssignmentSerializer(data={
            "teacher": self.teacher.id,
            "classroom": self.classroom.id,
            "start_date": "2026-09-01",
            "end_date": "2026-10-01",
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)


    def test_serializer_rejects_invalid_date_range(self):
        serializer = TeacherAssignmentSerializer(
            data={
                "teacher": self.teacher.id,
                "classroom": self.classroom.id,
                "start_date": "2026-10-01",
                "end_date": "2026-09-01",
            }
        )

        self.assertFalse(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertIn("end_date", serializer.errors)


    def test_serializer_accepts_missing_end_date(self):
        serializer = TeacherAssignmentSerializer(data={
            "teacher": self.teacher.id,
            "classroom": self.classroom.id,
            "start_date": "2026-09-01",
        })

        self.assertTrue(serializer.is_valid(), serializer.errors) 


    def test_education_can_create_teacher_assignment(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.post(
            "/api/teacher-assignments/",
            {
                "teacher": self.teacher.id,
                "classroom": self.classroom.id,
                "start_date": "2026-09-01",
                "end_date": "2026-10-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_cannot_create_teacher_assignment(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/teacher-assignments/",
            {
                "teacher": self.teacher.id,
                "classroom": self.classroom.id,
                "start_date": "2026-09-01",
                "end_date": "2026-10-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_assignment_with_invalid_dates(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.post(
            "/api/teacher-assignments/",
            {
                "teacher": self.teacher.id,
                "classroom": self.classroom.id,
                "start_date": "2026-10-01",
                "end_date": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_class_can_have_multiple_teacher_assignments_api(self):
        self.client.force_authenticate(user=self.education)

        teacher_2 = User.objects.create_user(
            username="teacher_assignment_test_2",
            password="Test12345",
            role="teacher",
        )

        response_1 = self.client.post(
            "/api/teacher-assignments/",
            {
                "teacher": self.teacher.id,
                "classroom": self.classroom.id,
                "start_date": "2026-09-01",
                "end_date": "2026-10-01",
            },
            format="json",
        )

        response_2 = self.client.post(
            "/api/teacher-assignments/",
            {
                "teacher": teacher_2.id,
                "classroom": self.classroom.id,
                "start_date": "2026-10-02",
                "end_date": "2026-11-01",
            },
            format="json",
        )

        self.assertEqual(
            response_1.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response_2.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            TeacherAssignment.objects.filter(
                classroom=self.classroom
            ).count(),
            2,
        ) 


    def test_education_can_list_teacher_assignments(self):
        self.client.force_authenticate(user=self.education)

        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.get(
            "/api/teacher-assignments/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1) 

    def test_education_can_retrieve_teacher_assignment(self):
        self.client.force_authenticate(user=self.education)

        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.get(
            f"/api/teacher-assignments/{assignment.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            assignment.id,
        ) 

    def test_education_can_update_teacher_assignment(self):
        self.client.force_authenticate(user=self.education)

        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.patch(
            f"/api/teacher-assignments/{assignment.id}/",
            {
                "end_date": "2026-10-15",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        assignment.refresh_from_db()

        self.assertEqual(
            str(assignment.end_date),
            "2026-10-15",
        )

    def test_update_teacher_assignment_with_invalid_dates(self):
        self.client.force_authenticate(user=self.education)

        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.patch(
            f"/api/teacher-assignments/{assignment.id}/",
            {
                "start_date": "2026-11-01",
                "end_date": "2026-10-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_education_can_delete_teacher_assignment(self):
        self.client.force_authenticate(user=self.education)

        assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.delete(
            f"/api/teacher-assignments/{assignment.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        assignment.refresh_from_db()

        self.assertTrue(assignment.is_deleted)

############Teacher_Classes############
    def test_teacher_can_list_own_classes(self):
        self.client.force_authenticate(user=self.teacher)

        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.get(
            "/api/teacher-classes/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        )

    def test_teacher_cannot_see_other_teacher_classes(self):
        self.client.force_authenticate(user=self.teacher)

        other_teacher = User.objects.create_user(
            username="other_teacher_test",
            password="Test12345",
            role="teacher",
        )

        TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        response = self.client.get(
            "/api/teacher-classes/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_teacher_can_see_past_classes(self):
        self.client.force_authenticate(user=self.teacher)

        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-01-01",
            end_date="2026-02-01",
        )

        response = self.client.get(
            "/api/teacher-classes/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        )

    def test_education_can_list_classes(self):
        self.client.force_authenticate(user=self.education)

        response = self.client.get(
            "/api/teacher-classes/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_multiple_teachers_can_have_same_class_at_different_times(self):
        other_teacher = User.objects.create_user(
            username="other_teacher_test",
            password="Test12345",
            role="teacher",
        )

        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-09-30",
        )

        TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=self.classroom,
            start_date="2026-10-01",
            end_date="2026-11-01",
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.get("/api/teacher-classes/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        )

        self.client.force_authenticate(user=other_teacher)

        response = self.client.get("/api/teacher-classes/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.classroom.id,
        )

    def test_assignment_cannot_overlap_with_existing_assignment(self):
        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-10-01",
        )

        teacher_2 = User.objects.create_user(
            username="teacher_assignment_test_2",
            password="Test12345",
            role="teacher",
        )

        assignment = TeacherAssignment(
            teacher=teacher_2,
            classroom=self.classroom,
            start_date="2026-09-15",
            end_date="2026-10-15",
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean() 

    def test_open_ended_assignment_cannot_overlap_with_new_assignment(self):
        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date=None,
        )

        teacher_2 = User.objects.create_user(
            username="teacher_assignment_test_2",
            password="Test12345",
            role="teacher",
        )

        assignment = TeacherAssignment(
            teacher=teacher_2,
            classroom=self.classroom,
            start_date="2026-10-01",
            end_date="2026-11-01",
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean() 

    def test_assignments_with_adjacent_dates_are_allowed(self):
        TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date="2026-09-01",
            end_date="2026-09-30",
        )

        teacher_2 = User.objects.create_user(
            username="teacher_assignment_test_2",
            password="Test12345",
            role="teacher",
        )

        assignment = TeacherAssignment(
            teacher=teacher_2,
            classroom=self.classroom,
            start_date="2026-10-01",
            end_date="2026-11-01",
        )

        assignment.full_clean()                                                                              
                                            