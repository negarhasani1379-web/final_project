from rest_framework.viewsets import ModelViewSet

from account.permissions import IsEducation

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
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsEducation]    

