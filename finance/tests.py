from datetime import date, datetime, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from academic.models import Class, Session, TeacherAssignment, Term
from account.models import User, UserRole
from finance.models import Salary, SessionReport, SessionReportStatus, TeacherTermRate
from finance.serializers import SessionReportSerializer, TeacherTermRateSerializer
from finance.services import calculate_teacher_monthly_salary_amount
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
            session_date=timezone.now() - timedelta(days=1),
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
            session_date=timezone.now() - timedelta(days=1),
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
            session_date=timezone.now() + timedelta(days=1),
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
            session_date=timezone.now() - timedelta(days=1),
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

    def test_absent_count_cannot_be_negative(self):
        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Valid lesson.",
            "present_count": 15,
            "absent_count": -1,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "absent_count",
            serializer.errors,
        )

    def test_new_report_status_is_pending(self):
        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Testing default report status.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertEqual(report.status, "pending")


    def test_teacher_cannot_set_report_status(self):
        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Testing status protection.",
            "present_count": 15,
            "absent_count": 2,
            "status": "approved",
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertEqual(report.status, "pending")


    def test_new_report_review_comment_is_empty(self):
        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Testing review comment.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertEqual(report.review_comment, "")


    def test_session_report_is_marked_late_after_48_hours(self):
        old_session = Session.objects.create(
            classroom=self.classroom,
            session_number=2,
            session_date=timezone.now() - timedelta(days=3),
        )

        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": old_session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Late submission test.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertTrue(report.is_late) 


    def test_session_report_is_not_late_within_48_hours(self):
        recent_session = Session.objects.create(
            classroom=self.classroom,
            session_number=3,
            session_date=timezone.now() - timedelta(hours=47),
        )

        request = APIRequestFactory().post("/fake-url/")
        request.user = self.teacher

        data = {
            "session": recent_session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "On-time submission test.",
            "present_count": 15,
            "absent_count": 2,
        }

        serializer = SessionReportSerializer(
            data=data,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertFalse(report.is_late)         


class SessionModelTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name="Session Test School",
        )

        self.term = Term.objects.create(
            title="Session Test Term",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            term_type="normal",
        )

        self.classroom = Class.objects.create(
            title="Session Test Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

    def test_session_number_must_be_unique_per_class(self):
        Session.objects.create(
            classroom=self.classroom,
            session_number=1,
            session_date=timezone.now() - timedelta(days=2),
        )

        with self.assertRaises(Exception):
            Session.objects.create(
                classroom=self.classroom,
                session_number=1,
                session_date=timezone.now() - timedelta(days=1),
            )


    def test_session_date_must_be_unique_per_class(self):
        session_date = timezone.now() - timedelta(days=2)

        Session.objects.create(
            classroom=self.classroom,
            session_number=1,
            session_date=session_date,
        )

        with self.assertRaises(Exception):
            Session.objects.create(
                classroom=self.classroom,
                session_number=2,
                session_date=session_date,
            ) 


class SessionReportAPITests(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="api_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.school = School.objects.create(
            name="API Test School",
        )

        self.term = Term.objects.create(
            title="API Test Term",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            term_type="normal",
        )

        self.classroom = Class.objects.create(
            title="API Test Class",
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
            session_date=timezone.now() - timedelta(days=1),
        )

    def test_teacher_can_create_session_report(self):
        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Introduction to English grammar.",
            "present_count": 15,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["session"], self.session.id)
        self.assertEqual(
            response.data["teacher_assignment"],
            self.assignment.id,
        )
        self.assertEqual(response.data["status"], "pending")

    def test_teacher_can_get_monthly_report_summary(self):
        current_month = self.session.session_date.month
        current_year = self.session.session_date.year

        SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Approved report",
            present_count=15,
            absent_count=2,
            status=SessionReportStatus.APPROVED,
        )

        session_2 = Session.objects.create(
            classroom=self.classroom,
            session_number=2,
            session_date=self.session.session_date + timedelta(hours=1),
        )

        SessionReport.objects.create(
            session=session_2,
            teacher_assignment=self.assignment,
            lesson_summary="Rejected report",
            present_count=14,
            absent_count=3,
            status=SessionReportStatus.REJECTED,
        )

        session_3 = Session.objects.create(
            classroom=self.classroom,
            session_number=3,
            session_date=self.session.session_date + timedelta(hours=2),
        )

        SessionReport.objects.create(
            session=session_3,
            teacher_assignment=self.assignment,
            lesson_summary="Pending report",
            present_count=16,
            absent_count=1,
            status=SessionReportStatus.PENDING,
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/session-reports/my-summary/"
            f"?month={current_month}&year={current_year}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["month"], current_month)
        self.assertEqual(response.data["year"], current_year)
        self.assertEqual(response.data["approved"], 1)
        self.assertEqual(response.data["rejected"], 1)
        self.assertEqual(response.data["pending"], 1)    


    def test_non_teacher_cannot_create_session_report(self):
        education_user = User.objects.create_user(
            username="api_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        self.client.force_authenticate(user=education_user)

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Unauthorized report.",
            "present_count": 15,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 403)


    def test_teacher_cannot_create_report_for_another_teacher_assignment(self):
        other_teacher = User.objects.create_user(
            username="other_api_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        other_assignment = TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=self.classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": self.session.id,
            "teacher_assignment": other_assignment.id,
            "lesson_summary": "Unauthorized teacher assignment.",
            "present_count": 15,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)


    def test_teacher_cannot_create_report_for_future_session(self):
        future_session = Session.objects.create(
            classroom=self.classroom,
            session_number=2,
            session_date=timezone.now() + timedelta(days=1),
        )

        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": future_session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Future session report.",
            "present_count": 15,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)


    def test_session_must_belong_to_assignment_class_api(self):
        other_classroom = Class.objects.create(
            title="Other API Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        other_session = Session.objects.create(
            classroom=other_classroom,
            session_number=1,
            session_date=timezone.now() - timedelta(days=1),
        )

        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": other_session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Mismatched classroom.",
            "present_count": 15,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)


    def test_unauthenticated_user_cannot_create_session_report(self):
        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Unauthenticated request.",
            "present_count": 15,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_session_cannot_have_two_reports(self):
        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "First report.",
            "present_count": 15,
            "absent_count": 2,
        }

        first_response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(first_response.status_code, 201)

        second_response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(second_response.status_code, 400)


    def test_negative_present_count_returns_400(self):
        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Negative present count.",
            "present_count": -1,
            "absent_count": 2,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_negative_absent_count_returns_400(self):
        self.client.force_authenticate(user=self.teacher)

        data = {
            "session": self.session.id,
            "teacher_assignment": self.assignment.id,
            "lesson_summary": "Negative absent count.",
            "present_count": 15,
            "absent_count": -1,
        }

        response = self.client.post(
            "/api/session-reports/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)



    def test_teacher_can_list_own_session_reports(self):
        self.client.force_authenticate(user=self.teacher)

        SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="My report.",
            present_count=15,
            absent_count=2,
        )

        response = self.client.get(
            "/api/session-reports/list/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["teacher_assignment"],
            self.assignment.id,
        )


    def test_teacher_cannot_see_another_teacher_report(self):
        other_teacher = User.objects.create_user(
            username="other_list_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        other_assignment = TeacherAssignment.objects.create(
            teacher=other_teacher,
            classroom=self.classroom,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        other_session = Session.objects.create(
            classroom=self.classroom,
            session_number=2,
            session_date=timezone.now() - timedelta(days=2),
        )
        SessionReport.objects.create(
            session=other_session,
            teacher_assignment=other_assignment,
            lesson_summary="Other teacher report.",
            present_count=10,
            absent_count=5,
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            "/api/session-reports/list/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)



    def test_non_teacher_cannot_list_session_reports(self):
        education_user = User.objects.create_user(
            username="list_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.get(
            "/api/session-reports/list/"
        )

        self.assertEqual(response.status_code, 403)


    def test_unauthenticated_user_cannot_list_session_reports(self):
        response = self.client.get(
            "/api/session-reports/list/"
        )

        self.assertEqual(response.status_code, 401)


    def test_education_can_list_session_reports_for_review(self):
        education_user = User.objects.create_user(
            username="review_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Report for education review.",
            present_count=15,
            absent_count=2,
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.get(
            "/api/session-reports/review/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_teacher_cannot_access_session_report_review(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            "/api/session-reports/review/"
        )

        self.assertEqual(response.status_code, 403) 

    def test_finance_cannot_access_session_report_review(self):
        finance_user = User.objects.create_user(
            username="review_finance",
            password="Test12345",
            role=UserRole.FINANCE,
        )

        self.client.force_authenticate(user=finance_user)

        response = self.client.get(
            "/api/session-reports/review/"
        )

        self.assertEqual(response.status_code, 403) 


    def test_unauthenticated_user_cannot_access_session_report_review(self):
        response = self.client.get(
            "/api/session-reports/review/"
        )

        self.assertEqual(response.status_code, 401)


    def test_education_can_approve_session_report(self):
        education_user = User.objects.create_user(
            username="approve_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="English grammar lesson.",
            present_count=15,
            absent_count=2,
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "status": "approved",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.status, "approved")

    def test_education_cannot_change_session_report_content(self):
        education_user = User.objects.create_user(
            username="content_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Original lesson.",
            present_count=15,
            absent_count=2,
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "lesson_summary": "Changed lesson.",
                "present_count": 100,
                "absent_count": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.lesson_summary, "Original lesson.")
        self.assertEqual(report.present_count, 15)
        self.assertEqual(report.absent_count, 2)                                  

    def test_teacher_cannot_approve_own_session_report(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="English grammar lesson.",
            present_count=15,
            absent_count=2,
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "status": "approved",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_education_cannot_reject_without_comment(self):
        education_user = User.objects.create_user(
            username="reject_no_comment",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="English grammar lesson.",
            present_count=15,
            absent_count=2,
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "status": "rejected",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400) 

    def test_education_can_reject_session_report_with_comment(self):
        education_user = User.objects.create_user(
            username="reject_with_comment",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="English grammar lesson.",
            present_count=15,
            absent_count=2,
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "status": "rejected",
                "review_comment": "Attendance count needs correction.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.status, "rejected")
        self.assertEqual(
            report.review_comment,
            "Attendance count needs correction.",
        )


    def test_teacher_can_edit_rejected_session_report(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Original lesson.",
            present_count=15,
            absent_count=2,
            status="rejected",
            review_comment="Please correct the attendance count.",
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/",
            {
                "lesson_summary": "Corrected lesson.",
                "present_count": 14,
                "absent_count": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.lesson_summary, "Corrected lesson.")
        self.assertEqual(report.present_count, 14)
        self.assertEqual(report.absent_count, 3)


    def test_teacher_can_resubmit_rejected_session_report(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Original lesson.",
            present_count=15,
            absent_count=2,
            status="rejected",
            review_comment="Please correct the attendance count.",
        )

        self.client.force_authenticate(user=self.teacher)
        report.rejected_at = timezone.now()
        report.save(update_fields=["rejected_at"])

        response = self.client.patch(
            f"/api/session-reports/{report.id}/",
            {
                "lesson_summary": "Corrected lesson.",
                "present_count": 14,
                "absent_count": 3,
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.status, "pending")
        self.assertEqual(report.lesson_summary, "Corrected lesson.")
        self.assertEqual(report.present_count, 14)
        self.assertEqual(report.absent_count, 3) 
        self.assertIsNotNone(report.resubmitted_at)
        self.assertFalse(report.is_late)
        self.assertEqual(report.review_comment, "")


    def test_teacher_resubmit_is_late_after_48_hours(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Original lesson.",
            present_count=15,
            absent_count=2,
            status="rejected",
            review_comment="Please correct the lesson.",
            rejected_at=timezone.now() - timedelta(hours=49),
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/",
            {
                "lesson_summary": "Late corrected lesson.",
                "present_count": 14,
                "absent_count": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.status, "pending")
        self.assertIsNotNone(report.resubmitted_at)
        self.assertTrue(report.is_late)
        self.assertEqual(report.review_comment, "")    


    def test_teacher_cannot_edit_approved_session_report(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Approved lesson.",
            present_count=15,
            absent_count=2,
            status="approved",
            review_comment="",
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/",
            {
                "lesson_summary": "Trying to change approved report.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_education_cannot_modify_session_report_content(self):
        education_user = User.objects.create_user(
            username="education_no_content_change",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Original lesson.",
            present_count=15,
            absent_count=2,
            status="pending",
            review_comment="",
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "status": "approved",
                "lesson_summary": "Changed by education!",
                "present_count": 100,
                "absent_count": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertEqual(report.status, "approved")
        self.assertEqual(report.lesson_summary, "Original lesson.")
        self.assertEqual(report.present_count, 15)
        self.assertEqual(report.absent_count, 2)

    def test_teacher_cannot_approve_own_session_report(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="English grammar lesson.",
            present_count=15,
            absent_count=2,
            status="pending",
        )

        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/session-reports/{report.id}/review/",
            {
                "status": "approved",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_education_can_filter_session_reports_by_school(self):
        education_user = User.objects.create_user(
            username="education_filter_school",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="School filter test.",
            present_count=15,
            absent_count=2,
            status="pending",
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.get(
            f"/api/session-reports/review/?school={self.school.id}"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(report.id, returned_ids)

    def test_education_can_filter_session_reports_by_class(self):
        education_user = User.objects.create_user(
            username="education_filter_class",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Class filter test.",
            present_count=15,
            absent_count=2,
            status="pending",
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.get(
            f"/api/session-reports/review/?classroom={self.classroom.id}"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(report.id, returned_ids)


    def test_education_can_filter_session_reports_by_teacher(self):
        education_user = User.objects.create_user(
            username="education_filter_teacher",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Teacher filter test.",
            present_count=15,
            absent_count=2,
            status="pending",
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.get(
           f"/api/session-reports/review/?teacher={self.teacher.id}"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(report.id, returned_ids)


    def test_education_can_filter_session_reports_by_date_range(self):
        education_user = User.objects.create_user(
            username="education_filter_date",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher_assignment=self.assignment,
            lesson_summary="Date filter test.",
            present_count=15,
            absent_count=2,
            status="pending",
        )

        self.client.force_authenticate(user=education_user)

        response = self.client.get(
            "/api/session-reports/review/"
            f"?date_from={self.session.session_date.date()}"
            f"&date_to={self.session.session_date.date()}"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(report.id, returned_ids)


    def test_full_session_report_workflow(self):
        education_user = User.objects.create_user(
            username="workflow_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        # 1. Teacher creates the report
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/session-reports/",
            {
                "session": self.session.id,
                "teacher_assignment": self.assignment.id,
                "lesson_summary": "Initial lesson.",
                "present_count": 15,
                "absent_count": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        report_id = response.data["id"]

        # 2. Education rejects the report
        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report_id}/review/",
            {
                "status": "rejected",
                "review_comment": "Please correct the attendance count.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        # 3. Teacher edits and resubmits the rejected report
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/session-reports/{report_id}/",
            {
                "lesson_summary": "Corrected lesson.",
                "present_count": 14,
                "absent_count": 3,
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        # 4. Education approves the resubmitted report
        self.client.force_authenticate(user=education_user)

        response = self.client.patch(
            f"/api/session-reports/{report_id}/review/",
            {
                "status": "approved",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        report = SessionReport.objects.get(id=report_id)

        self.assertEqual(report.status, "approved")
        self.assertEqual(
            report.lesson_summary,
            "Corrected lesson.",
        )
        self.assertEqual(report.present_count, 14)
        self.assertEqual(report.absent_count, 3)


    def test_teacher_cannot_access_session_report_review_list(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            "/api/session-reports/review/"
        )

        self.assertEqual(response.status_code, 403) 



class TeacherTermRateSerializerTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="rate_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.term = Term.objects.create(
            title="Rate Test Term",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            term_type="normal",
        )

    def test_teacher_term_rate_serializer_valid(self):
        data = {
            "teacher": self.teacher.id,
            "term": self.term.id,
            "base_rate": "500000.00",
        }

        serializer = TeacherTermRateSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        rate = serializer.save()

        self.assertEqual(rate.teacher, self.teacher)
        self.assertEqual(rate.term, self.term)
        self.assertEqual(rate.base_rate, Decimal("500000.00"))
        self.assertFalse(rate.is_deleted)

class TeacherTermRateAPITests(APITestCase):

    def setUp(self):
        self.finance_user = User.objects.create_user(
            username="finance_rate_test",
            password="Test12345",
            role=UserRole.FINANCE,
        )

        self.teacher = User.objects.create_user(
            username="rate_api_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.education_user = User.objects.create_user(
            username="rate_api_education",
            password="Test12345",
            role=UserRole.EDUCATION,
        )

        self.term = Term.objects.create(
            title="Rate API Term",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            term_type="normal",
        )

        self.url = "/api/teacher-term-rates/"

    def test_finance_can_create_teacher_term_rate(self):
        self.client.force_authenticate(user=self.finance_user)

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "500000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["teacher"],
            self.teacher.id,
        )

        self.assertEqual(
            response.data["term"],
            self.term.id,
        )

        self.assertEqual(
            response.data["base_rate"],
            "500000.00",
        ) 

    def test_finance_can_list_teacher_term_rates(self):
        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal("500000.00"),
        )

        self.client.force_authenticate(user=self.finance_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["teacher"],
            self.teacher.id,
        ) 

    def test_teacher_cannot_create_teacher_term_rate(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "500000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_cannot_create_teacher_term_rate(self):
        self.client.force_authenticate(user=self.education_user)

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "500000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        ) 
    def test_unauthenticated_user_cannot_create_teacher_term_rate(self):
        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "500000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        ) 

    def test_teacher_term_rate_cannot_be_duplicated(self):
        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal("500000.00"),
        )

        self.client.force_authenticate(user=self.finance_user)

        response = self.client.post(
            self.url,
            {
                "teacher": self.teacher.id,
                "term": self.term.id,
                "base_rate": "600000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )                   


class SalaryModelTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="salary_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.other_teacher = User.objects.create_user(
            username="salary_other_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.school = School.objects.create(
            name="Salary Test School",
        )

        self.term = Term.objects.create(
            title="Salary Test Term",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            term_type="normal",
        )

    def test_salary_can_be_created(self):
        salary = Salary.objects.create(
            teacher=self.teacher,
            term=self.term,
            year=2026,
            month=9,
            calculated_amount=Decimal("2540000.00"),
            final_amount=Decimal("2540000.00"),
        )

        self.assertEqual(salary.teacher, self.teacher)
        self.assertEqual(salary.term, self.term)
        self.assertEqual(salary.year, 2026)
        self.assertEqual(salary.month, 9)

    def test_salary_amounts_are_decimal(self):
        salary = Salary.objects.create(
            teacher=self.teacher,
            term=self.term,
            year=2026,
            month=9,
            calculated_amount=Decimal("2540000.00"),
            final_amount=Decimal("2540000.00"),
        )

        self.assertEqual(
            salary.calculated_amount,
            Decimal("2540000.00"),
        )
        self.assertEqual(
            salary.final_amount,
            Decimal("2540000.00"),
        )

    def test_salary_is_unique_per_teacher_year_and_month(self):
        Salary.objects.create(
            teacher=self.teacher,
            term=self.term,
            year=2026,
            month=9,
            calculated_amount=Decimal("2000000.00"),
            final_amount=Decimal("2000000.00"),
        )

        with self.assertRaises(Exception):
            Salary.objects.create(
                teacher=self.teacher,
                term=self.term,
                year=2026,
                month=9,
                calculated_amount=Decimal("2500000.00"),
                final_amount=Decimal("2500000.00"),
            )

    def test_different_teacher_can_have_salary_for_same_month(self):
        Salary.objects.create(
            teacher=self.teacher,
            term=self.term,
            year=2026,
            month=9,
            calculated_amount=Decimal("2000000.00"),
            final_amount=Decimal("2000000.00"),
        )

        salary = Salary.objects.create(
            teacher=self.other_teacher,
            term=self.term,
            year=2026,
            month=9,
            calculated_amount=Decimal("2200000.00"),
            final_amount=Decimal("2200000.00"),
        )

        self.assertEqual(salary.teacher, self.other_teacher)

    def test_same_teacher_can_have_salary_for_different_month(self):
        Salary.objects.create(
            teacher=self.teacher,
            term=self.term,
            year=2026,
            month=9,
            calculated_amount=Decimal("2000000.00"),
            final_amount=Decimal("2000000.00"),
        )

        salary = Salary.objects.create(
            teacher=self.teacher,
            term=self.term,
            year=2026,
            month=10,
            calculated_amount=Decimal("2200000.00"),
            final_amount=Decimal("2200000.00"),
        )

        self.assertEqual(salary.month, 10)

class SalaryCalculationServiceTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="salary_service_teacher",
            password="Test12345",
            role=UserRole.TEACHER,
        )

        self.school = School.objects.create(
            name="Salary Service School",
        )

        self.term = Term.objects.create(
            title="September 2026",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            term_type="normal",
        )

        self.class_60 = Class.objects.create(
            title="60 Minute Class",
            school=self.school,
            term=self.term,
            session_duration=60,
        )

        self.class_90 = Class.objects.create(
            title="90 Minute Class",
            school=self.school,
            term=self.term,
            session_duration=90,
        )

        self.class_120 = Class.objects.create(
            title="120 Minute Class",
            school=self.school,
            term=self.term,
            session_duration=120,
        )

        self.assignment_60 = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.class_60,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        self.assignment_90 = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.class_90,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        self.assignment_120 = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.class_120,
            start_date=self.term.start_date,
            end_date=self.term.end_date,
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal("200000.00"),
        )


    def test_calculates_salary_from_approved_non_late_reports(self):
        SessionReport.objects.create(
            session=Session.objects.create(
                classroom=self.class_90,
                session_number=1,
                session_date=timezone.make_aware(
                    datetime(2026, 9, 5, 10, 0),
                ),
            ),
            teacher_assignment=self.assignment_90,
            lesson_summary="90 minute session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        SessionReport.objects.create(
            session=Session.objects.create(
                classroom=self.class_60,
                session_number=1,
                session_date=timezone.make_aware(
                    datetime(2026, 9, 10, 10, 0),
                ),
            ),
            teacher_assignment=self.assignment_60,
            lesson_summary="60 minute session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        SessionReport.objects.create(
            session=Session.objects.create(
                classroom=self.class_120,
                session_number=1,
                session_date=timezone.make_aware(
                    datetime(2026, 9, 15, 10, 0),
                ),
            ),
            teacher_assignment=self.assignment_120,
            lesson_summary="120 minute session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        amount = calculate_teacher_monthly_salary_amount(
            teacher=self.teacher,
            year=2026,
            month=9,
        )

        self.assertEqual(
            amount,
            Decimal("600000.00"),
        ) 

    def test_late_approved_report_is_excluded_from_salary(self):
        session = Session.objects.create(
            classroom=self.class_90,
            session_number=2,
            session_date=timezone.make_aware(
                datetime(2026, 9, 20, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=session,
            teacher_assignment=self.assignment_90,
            lesson_summary="Late approved session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=True,
        )

        amount = calculate_teacher_monthly_salary_amount(
            teacher=self.teacher,
            year=2026,
            month=9,
        )

        self.assertEqual(
            amount,
            Decimal("0.00"),
        ) 

    def test_salary_calculation_fails_when_month_has_unapproved_report(self):
        approved_session = Session.objects.create(
            classroom=self.class_90,
            session_number=3,
            session_date=timezone.make_aware(
                datetime(2026, 9, 5, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=approved_session,
            teacher_assignment=self.assignment_90,
            lesson_summary="Approved session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        pending_session = Session.objects.create(
            classroom=self.class_90,
            session_number=4,
            session_date=timezone.make_aware(
                datetime(2026, 9, 10, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=pending_session,
            teacher_assignment=self.assignment_90,
            lesson_summary="Pending session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.PENDING,
            is_late=False,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Salary cannot be calculated until all reports for the month are approved.",
        ):
            calculate_teacher_monthly_salary_amount(
                teacher=self.teacher,
                year=2026,
                month=9,
            ) 

    def test_reports_from_other_month_are_excluded(self):
        september_session = Session.objects.create(
            classroom=self.class_90,
            session_number=7,
            session_date=timezone.make_aware(
                datetime(2026, 9, 10, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=september_session,
            teacher_assignment=self.assignment_90,
            lesson_summary="September session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        october_session = Session.objects.create(
            classroom=self.class_90,
            session_number=8,
            session_date=timezone.make_aware(
                datetime(2026, 10, 10, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=october_session,
            teacher_assignment=self.assignment_90,
            lesson_summary="October session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        amount = calculate_teacher_monthly_salary_amount(
            teacher=self.teacher,
            year=2026,
            month=9,
        )

        self.assertEqual(
            amount,
            Decimal("200000.00"),
        ) 

    def test_summer_term_applies_ten_percent_bonus(self):
        summer_term = Term.objects.create(
            title="Summer 2026",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
            term_type="summer",
        )

        summer_class = Class.objects.create(
            title="Summer Class",
            school=self.school,
            term=summer_term,
            session_duration=90,
        )

        summer_assignment = TeacherAssignment.objects.create(
            teacher=self.teacher,
            classroom=summer_class,
            start_date=summer_term.start_date,
            end_date=summer_term.end_date,
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=summer_term,
            base_rate=Decimal("200000.00"),
        )

        session = Session.objects.create(
            classroom=summer_class,
            session_number=1,
            session_date=timezone.make_aware(
                datetime(2026, 8, 10, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=session,
            teacher_assignment=summer_assignment,
            lesson_summary="Summer session",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        amount = calculate_teacher_monthly_salary_amount(
            teacher=self.teacher,
            year=2026,
            month=8,
        )

        self.assertEqual(
            amount,
            Decimal("220000.00"),
        ) 

    def test_salary_calculation_fails_without_teacher_term_rate(self):
        session = Session.objects.create(
            classroom=self.class_90,
            session_number=9,
            session_date=timezone.make_aware(
                datetime(2026, 9, 20, 10, 0),
            ),
        )

        SessionReport.objects.create(
            session=session,
            teacher_assignment=self.assignment_90,
            lesson_summary="Session without rate",
            present_count=10,
            absent_count=0,
            status=SessionReportStatus.APPROVED,
            is_late=False,
        )

        TeacherTermRate.objects.filter(
            teacher=self.teacher,
            term=self.term,
        ).delete()

        with self.assertRaisesRegex(
            ValueError,
            "No teacher term rate exists for this teacher and term.",
        ):
            calculate_teacher_monthly_salary_amount(
                teacher=self.teacher,
                year=2026,
                month=9,
            )                       
