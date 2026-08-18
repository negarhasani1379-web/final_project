from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from finance.serializers import SessionReportSerializer


class SessionReportCreateView(generics.CreateAPIView):
    serializer_class = SessionReportSerializer
    permission_classes = [IsAuthenticated]
