from rest_framework.viewsets import ModelViewSet

from .models import School
from .serializers import SchoolSerializer


class SchoolViewSet(ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


