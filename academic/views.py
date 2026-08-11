from rest_framework.viewsets import ModelViewSet

from account.permissions import IsEducation

from .models import Term
from .serializers import TermSerializer


class TermViewSet(ModelViewSet):
    queryset = Term.objects.filter(is_deleted=False)
    serializer_class = TermSerializer
    permission_classes = [IsEducation]