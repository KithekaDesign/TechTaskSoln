from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ReportViewSet, FreelancerAnalyticsView, FreelancerReportExportView, ClientAnalyticsView

router = DefaultRouter()
router.register(r'reports', ReportViewSet)

urlpatterns = router.urls + [
    path('reports/freelancer/analytics/', FreelancerAnalyticsView.as_view(), name='freelancer_analytics'),
    path('reports/freelancer/export/', FreelancerReportExportView.as_view(), name='freelancer_report_export'),
    path('reports/client/analytics/', ClientAnalyticsView.as_view(), name='client_analytics'),
]