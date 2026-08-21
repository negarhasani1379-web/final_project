from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MyTokenObtainPairView,
    TeacherListView,
    TeacherTestView,
)

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("teacher-test/", TeacherTestView.as_view(), name="teacher-test",),
    path("teachers/",TeacherListView.as_view(),name="teacher-list",),
]