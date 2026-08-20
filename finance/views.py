from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from account.permissions import IsEducation, IsTeacher
from finance.models import SessionReport
from finance.serializers import (
    SessionReportReviewSerializer,
    SessionReportSerializer,
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
