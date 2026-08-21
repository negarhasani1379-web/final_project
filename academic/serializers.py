from datetime import date

from django.db.models import Q
from rest_framework import serializers

from account.models import User

from .models import Class, Session, TeacherAssignment, Term


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = (
            "id",
            "title",
            "start_date",
            "end_date",
            "term_type",
        )

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            self.instance.start_date if self.instance else None,
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date if self.instance else None,
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date."
            )

        overlapping = Term.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError(
                "This term overlaps with an existing term."
            )

        return attrs

class CurrentTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
        )

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = (
            "id",
            "title",
            "school",
            "term",
            "session_duration",
        )

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = (
            "id",
            "classroom",
            "session_number",
            "session_date",
        )        


class ClassDetailSerializer(ClassSerializer):
    current_teacher = serializers.SerializerMethodField()

    class Meta(ClassSerializer.Meta):
        fields = ClassSerializer.Meta.fields + (
            "current_teacher",
        )

    def get_current_teacher(self, obj):
        assignment = (
            TeacherAssignment.objects
            .filter(
                classroom=obj,
                is_deleted=False,
                end_date__isnull=True,
            )
            .select_related("teacher")
            .first()
        )

        if assignment:
            return CurrentTeacherSerializer(
                assignment.teacher
            ).data

        return None

            
class TeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAssignment
        fields = (
            "id",
            "teacher",
            "classroom",
            "start_date",
            "end_date",
        )

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        classroom = attrs.get("classroom")

    
        if end_date is not None and start_date is not None:
            if end_date < start_date:
                raise serializers.ValidationError(
                    {
                        "end_date": "End date cannot be before start date."
                    }
            )

   
        if classroom and start_date:
            overlapping = TeacherAssignment.objects.filter(
                classroom=classroom,
                start_date__lte=end_date or date.max,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=start_date)
            )

            if self.instance:
                overlapping = overlapping.exclude(
                    pk=self.instance.pk
                )

            if overlapping.exists():
                raise serializers.ValidationError(
                    "This classroom already has a teacher assigned during this period."
                )

        return attrs       