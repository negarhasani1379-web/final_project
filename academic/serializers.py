from rest_framework import serializers

from .models import Class, TeacherAssignment, Term


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

        return attrs


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

        if end_date is not None and start_date is not None:
            if end_date < start_date:
                raise serializers.ValidationError(
                    {
                        "end_date": "End date cannot be before start date."
                    }
                )

        return attrs        