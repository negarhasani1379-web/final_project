from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.permissions import IsEducation, IsFinance, IsTeacher
from finance.models import SessionReport, TeacherTermRate
from finance.serializers import (
    SessionReportReviewSerializer,
    SessionReportSerializer,
    TeacherTermRateSerializer,
)


class SessionReportCreateView(generics.CreateAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsAuthenticated, IsTeacher]


class SessionReportListView(generics.ListAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return SessionReport.objects.filter(
            teacher_assignment__teacher=self.request.user
        )
    
class SessionReportReviewListView(generics.ListAPIView):

    serializer_class = SessionReportSerializer

    permission_classes = [IsAuthenticated, IsEducation]

    def get_queryset(self):
        queryset = SessionReport.objects.all()

        school_id = self.request.query_params.get("school")
        class_id = self.request.query_params.get("classroom")
        teacher_id = self.request.query_params.get("teacher")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if school_id:
            queryset = queryset.filter(
                session__classroom__school_id=school_id
            )

        if class_id:
            queryset = queryset.filter(
                session__classroom_id=class_id
            )

        if teacher_id:
            queryset = queryset.filter(
                teacher_assignment__teacher_id=teacher_id
            )

        if date_from:
            queryset = queryset.filter(
                session__session_date__date__gte=date_from
            )

        if date_to:
            queryset = queryset.filter(
                session__session_date__date__lte=date_to
            )

        return queryset
        
class SessionReportReviewUpdateView(generics.UpdateAPIView):
    queryset = SessionReport.objects.all()
    serializer_class = SessionReportReviewSerializer
    permission_classes = [IsAuthenticated, IsEducation]


class SessionReportUpdateView(generics.UpdateAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return SessionReport.objects.filter(
            teacher_assignment__teacher=self.request.user,
            status="rejected",
        )
    def perform_update(self, serializer):
        serializer.save(
            status="pending",
            review_comment="",
        )

class TeacherMonthlyReportSummaryView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")

        if not month or not year:
            return Response(
                {
                    "detail": "month and year are required."
                },
                status=400,
            )

        summary = SessionReport.objects.filter(
            teacher_assignment__teacher=request.user,
            session__session_date__month=month,
            session__session_date__year=year,
        ).aggregate(
            approved=Count(
                "id",
                filter=Q(status="approved"),
            ),
            rejected=Count(
                "id",
                filter=Q(status="rejected"),
            ),
            pending=Count(
                "id",
                filter=Q(status="pending"),
            ),
        )

        return Response(
            {
                "month": int(month),
                "year": int(year),
                **summary,
            }
        )   
    class TeacherTermRateListCreateView(generics.ListCreateAPIView):
        queryset = TeacherTermRate.objects.all()
        serializer_class = TeacherTermRateSerializer
        permission_classes = [IsAuthenticated, IsFinance]

