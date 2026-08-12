from rest_framework.routers import DefaultRouter

from .views import ClassViewSet, TermViewSet

router = DefaultRouter()
router.register("terms", TermViewSet, basename="term")
router.register("classes",ClassViewSet,basename="class",)

urlpatterns = router.urls