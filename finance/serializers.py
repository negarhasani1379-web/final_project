from django.utils import timezone
from rest_framework import serializers

from account.models import User, UserRole
from finance.models import Salary, SessionReport, TeacherTermRate


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
            "resubmitted_at",
            "is_late",
        ]
        read_only_fields = [
            "status",
            "review_comment",
            "resubmitted_at",
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
    
    def update(self, instance, validated_data):
        if instance.status == "rejected":
            resubmitted_at = timezone.now()

            validated_data["resubmitted_at"] = resubmitted_at
            validated_data["status"] = "pending"
            validated_data["review_comment"] = ""

            if instance.rejected_at:
                validated_data["is_late"] = (
                    resubmitted_at - instance.rejected_at
                ).total_seconds() > 48 * 60 * 60

        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        session = validated_data["session"]

        now = timezone.now()
        session_datetime = session.session_date

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
    def update(self, instance, validated_data):
        if validated_data.get("status") == "rejected":
            validated_data["rejected_at"] = timezone.now()

        return super().update(instance, validated_data)
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
            "rejected_at",
            "resubmitted_at",
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
            "rejected_at",
            "resubmitted_at",
        ] 

class TeacherTermRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherTermRate
        fields = [
            "id",
            "teacher",
            "term",
            "base_rate",
        ]
        read_only_fields = [
            "id",
        ]

class SalarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Salary
        fields = [
            "id",
            "teacher",
            "term",
            "year",
            "month",
            "calculated_amount",
            "final_amount",
            "adjustment_reason",
        ]
        read_only_fields = [
            "id",
            "teacher",
            "term",
            "year",
            "month",
            "calculated_amount",
            "final_amount",
            "adjustment_reason",
        ]

class TeacherMonthlySalaryCalculateSerializer(serializers.Serializer):

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            role=UserRole.TEACHER
        )
    )

    year = serializers.IntegerField()

    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
    )
