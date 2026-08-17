from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from account.permissions import IsEducation, IsTeacher, IsTeacherOrEducation

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

    def get_queryset(self):
        queryset = Class.objects.filter(is_deleted=False)

        school_id = self.request.query_params.get("school")
        term_id = self.request.query_params.get("term")
        teacher_id = self.request.query_params.get("teacher")

        if school_id:
            queryset = queryset.filter(
                school_id=school_id
            )

        if term_id:
            queryset = queryset.filter(
                term_id=term_id
            )

        if teacher_id:
            queryset = queryset.filter(
                teacher_assignments__teacher_id=teacher_id,
                teacher_assignments__is_deleted=False,
            )

        return queryset.distinct()

class TeacherAssignmentViewSet(ModelViewSet):
    queryset = TeacherAssignment.objects.filter(is_deleted=False)
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsEducation]

class TeacherClassListView(APIView):
    permission_classes = [IsTeacherOrEducation]

    def get(self, request):
        if request.user.role == "teacher":
            classrooms = Class.objects.filter(
                teacher_assignments__teacher=request.user,
                teacher_assignments__is_deleted=False,
                is_deleted=False,
            ).distinct()

        else:
            classrooms = Class.objects.filter(
                is_deleted=False,
            )

        serializer = ClassSerializer(classrooms, many=True)

        return Response(serializer.data)