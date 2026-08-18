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
