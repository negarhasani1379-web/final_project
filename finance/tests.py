from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from academic.models import Class, Session, TeacherAssignment, Term
from account.models import User, UserRole
from finance.serializers import SessionReportSerializer
from school.models import School


class SessionReportSerializerTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher_test",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.school = School.objects.create(
            name="Test School",
        )

        self.term = Term.objects.create(
            title="Test Term",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            term_type="normal",
        )

        self.classroom = Class.objects.create(
            title="Test Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        self.assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        self.session = Session.objects.create(
            classroom=self.classroom,
            session_number=1,
            session_date=date.today() - timedelta(days=1),
        )

    def test_teacher_can_create_report_for_own_session(self):
        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Introduction to English grammar.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertEqual(report.session, self.session)
        self.assertEqual(
            report.teacher_assignment,
            self.assignment,
        )
        self.assertEqual(report.present_count, 15)
        self.assertEqual(report.absent_count, 2)
        self.assertEqual(report.status, "pending")

    def test_teacher_cannot_create_report_for_another_teacher_class(self):
        other_teacher = User.objects.create_user(
            username="other_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        other_classroom = Class.objects.create(
            title="Other Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        other_assignment = TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=other_classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        other_session = Session.objects.create(
            classroom=other_classroom,
            session_number=1,
            session_date=date.today() - timedelta(days=1),
        )

        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": other_session.id,
            "teacher_assignment": other_assignment.id,
            "lesson_summary": "Trying to access another teacher's class.",
            "present_count": 10,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "You can only submit reports for your own assignment.",
            str(serializer.errors),
        )    


    def test_teacher_cannot_create_report_for_future_session(self):
        future_session = Session.objects.create(
            classroom=self.classroom,
            session_number=2,
            session_date=date.today() + timedelta(days=1),
        )

        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": future_session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Future lesson.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "A report can only be submitted after the session.",
            str(serializer.errors),
        )

    def test_education_officer_cannot_create_report(self):
        education_user = User.objects.create_user(
            username="education_test",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        request = APIRequestFactory().post("/fake-url/")
        request.user = education_user

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Education officer trying to create report.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "Only teachers can create session reports.",
            str(serializer.errors),
        ) 


    def test_session_must_belong_to_assignment_class(self):
        other_classroom = Class.objects.create(
            title="Another Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        other_session = Session.objects.create(
            classroom=other_classroom,
            session_number=1,
            session_date=date.today() - timedelta(days=1),
        )

        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": other_session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Mismatched session and assignment.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "The session does not belong to the assigned classroom.",
            str(serializer.errors),
        )

    def test_present_count_cannot_be_negative(self):
        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Valid lesson.",
            "present_count": -1,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "present_count",
            serializer.errors,
        )           