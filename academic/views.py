from rest_framework.viewsets import ModelViewSet

from account.permissions import IsEducation

from .models import Term, Class
from .serializers import ClassSerializer, TermSerializer


class TermViewSet(ModelViewSet):
    queryset = Term.objects.filter(is_deleted=False)
    serializer_class = TermSerializer
    permission_classes = [IsEducation]

class ClassViewSet(ModelViewSet):
    queryset = Class.objects.filter(is_deleted=False)
    serializer_class = ClassSerializer
    permission_classes = [IsEducation]    