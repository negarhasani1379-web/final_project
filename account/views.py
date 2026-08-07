from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsTeacher
from .serializers import MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TeacherTestView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        return Response({
            "message": "Welcome Teacher"
        })


