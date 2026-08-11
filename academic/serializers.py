from rest_framework import serializers

from .models import Term


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