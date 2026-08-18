from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from academic.models import Class, Session, TeacherAssignment, Term
from account.models import User, UserRole
from finance.models import SessionReport
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
            session_date=date.today() - timedelta(days=2),
        )

        with self.assertRaises(Exception):
            Session.objects.create(
                classroom=self.classroom,
                session_number=1,
                session_date=date.today() - timedelta(days=1),
            )


    def test_session_date_must_be_unique_per_class(self):
        session_date = date.today() - timedelta(days=2)

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
            session_date=date.today() - timedelta(days=1),
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
            session_date=date.today() + timedelta(days=1),
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
            session_date=date.today() - timedelta(days=1),
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
            session_date=date.today() - timedelta(days=2),
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