from django.urls import path

from finance.views import SessionReportCreateView

urlpatterns = [
    path(
        "session-reports/",
        SessionReportCreateView.as_view(),
        name="session-report-create",
    ),
]