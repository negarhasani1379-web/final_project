from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ClassViewSet,
    TeacherAssignmentViewSet,
    TeacherClassListView,
    TermViewSet,
)

router = DefaultRouter()
router.register("terms", TermViewSet, basename="term")
router.register("classes",ClassViewSet,basename="class",)
router.register("teacher-assignments",TeacherAssignmentViewSet,basename="teacher-assignment",)


urlpatterns = router.urls + [
    path(
        "teacher-classes/",
        TeacherClassListView.as_view(),
        name="teacher-classes",
    ),
]