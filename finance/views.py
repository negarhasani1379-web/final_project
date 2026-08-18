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
    queryset = SessionReport.objects.all()
    serializer_class = SessionReportSerializer
    permission_classes = [IsAuthenticated, IsEducation]    
    
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
