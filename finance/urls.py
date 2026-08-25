from django.urls import path

from finance.views import (
    SalaryListView,
    SessionReportCreateView,
    SessionReportListView,
    SessionReportReviewListView,
    SessionReportReviewUpdateView,
    SessionReportUpdateView,
    TeacherMonthlyReportSummaryView,
    TeacherMonthlySalaryBulkCalculateView,
    TeacherMonthlySalaryCalculateView,
    TeacherOwnSalaryHistoryView,
    TeacherTermRateListCreateView,
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
    path(
        "session-reports/<int:pk>/",
        SessionReportUpdateView.as_view(),
        name="session-report-update",
    ),
   
   path(
        "session-reports/my-summary/",
        TeacherMonthlyReportSummaryView.as_view(),
        name="teacher-monthly-report-summary",
        ),

    path(
        "teacher-term-rates/",
        TeacherTermRateListCreateView.as_view(),
        name="teacher-term-rate-list-create",
    ),

    path(
        "teacher-monthly-salary/calculate/",
        TeacherMonthlySalaryCalculateView.as_view(),
        name="teacher-monthly-salary-calculate",
    ),

    path(
        "teacher-monthly-salary/calculate-all/",
        TeacherMonthlySalaryBulkCalculateView.as_view(),
        name="teacher-monthly-salary-bulk-calculate",
    ),

    path(
        "salaries/",
        SalaryListView.as_view(),
        name="salary-list",
    ),

    path(
        "my-salaries/",
        TeacherOwnSalaryHistoryView.as_view(),
        name="teacher-own-salary-history",
    ),    


] 

