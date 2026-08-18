from django.urls import path

from finance.views import (
    SessionReportCreateView,
    SessionReportListView,
    SessionReportReviewListView,
    SessionReportReviewUpdateView,
)

urlpatterns = [
    path(
        "session-reports/",
        SessionReportCreateView.as_view(),
        name="session-report-create",
    ),
    path(
        "session-reports/list/",
        SessionReportListView.as_view(),
        name="session-report-list",
    ),
    path(
    "session-reports/review/",
    SessionReportReviewListView.as_view(),
    name="session-report-review-list",
    ),

    path(
        "session-reports/<int:pk>/review/",
        SessionReportReviewUpdateView.as_view(),
        name="session-report-review-update",
    ),
]