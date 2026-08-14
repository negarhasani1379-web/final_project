from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from account.permissions import IsEducation, IsTeacher

from .models import Class, TeacherAssignment, Term
from .serializers import ClassSerializer, TeacherAssignmentSerializer, TermSerializer


class TermViewSet(ModelViewSet):
    queryset = Term.objects.filter(is_deleted=False)
    serializer_class = TermSerializer
    permission_classes = [IsEducation]

class ClassViewSet(ModelViewSet):
    queryset = Class.objects.filter(is_deleted=False)
    serializer_class = ClassSerializer
    permission_classes = [IsEducation]

class TeacherAssignmentViewSet(ModelViewSet):
    queryset = TeacherAssignment.objects.filter(is_deleted=False)
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsEducation]

class TeacherClassListView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        classrooms = Class.objects.filter(
            teacher_assignments__teacher=request.user,
            teacher_assignments__is_deleted=False,
            is_deleted=False,
        ).distinct()

        serializer = ClassSerializer(classrooms, many=True)

        return Response(serializer.data)