from django.utils import timezone
from rest_framework import serializers

from academic.models import TeacherAssignment
from finance.models import SessionReport


class SessionReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = SessionReport
        fields = [
            "id",
            "session",
            "teacher_assignment",
            "lesson_summary",
            "present_count",
            "absent_count",
            "status",
            "review_comment",
            "is_late",
        ]
        read_only_fields = [
            "status",
            "review_comment",
            "is_late",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        session = attrs.get("session")
        teacher_assignment = attrs.get("teacher_assignment")

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        if request.user.role != "teacher":
            raise serializers.ValidationError(
                "Only teachers can create session reports."
            )

        if teacher_assignment.teacher_id != request.user.id:
            raise serializers.ValidationError(
                "You can only submit reports for your own assignment."
            )

        if session.classroom_id != teacher_assignment.classroom_id:
            raise serializers.ValidationError(
                "The session does not belong to the assigned classroom."
            )

        if session.session_date >= timezone.localdate():
            raise serializers.ValidationError(
                "A report can only be submitted after the session."
            )

        return attrs