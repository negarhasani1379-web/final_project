from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, UserRole
from .permissions import IsEducation, IsTeacher
from .serializers import (
    MyTokenObtainPairSerializer,
    TeacherListSerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TeacherTestView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        return Response({
            "message": "Welcome Teacher"
        })
    

class TeacherListView(APIView):
    permission_classes = [IsEducation]

    def get(self, request):
        teachers = User.objects.filter(
            role=UserRole.TEACHER
        )

        serializer = TeacherListSerializer(
            teachers,
            many=True,
        )

        return Response(serializer.data)



