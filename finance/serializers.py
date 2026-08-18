from datetime import date, datetime, time

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

        session = attrs.get(
            "session",
            self.instance.session if self.instance else None,
        )
        teacher_assignment = attrs.get(
            "teacher_assignment",
            self.instance.teacher_assignment if self.instance else None,
        )

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

        if session.session_date >= timezone.now():
            raise serializers.ValidationError(
                "A report can only be submitted after the session."
            )

        return attrs
    
    def create(self, validated_data):
        session = validated_data["session"]

        now = timezone.localtime()

        session_datetime = timezone.make_aware(
            datetime.combine(
                session.session_date,
                time.min,
            )
        )

        validated_data["is_late"] = (
            now - session_datetime
        ).total_seconds() > 48 * 60 * 60

        return super().create(validated_data)    


class SessionReportReviewSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        status = attrs.get("status")
        review_comment = attrs.get("review_comment")

        if status == "rejected" and not review_comment:
            raise serializers.ValidationError(
                "Review comment is required when rejecting a session report."
            )

        return attrs
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
            "id",
            "session",
            "teacher_assignment",
            "lesson_summary",
            "present_count",
            "absent_count",
            "is_late",
        ]    