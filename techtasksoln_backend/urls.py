"""
URL configuration for techtasksoln_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomLoginView
from projects.views import DashboardStatsView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ----- API routes (all under /api/) -----
    path('api/', include('projects.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('reports.urls')),
    path('api/', include('tracking.urls')),
    path('api/', include('fraud_detection.urls')),
    path('api/', include('messaging.urls')),
    path('api/auth/login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('accounts.urls')),
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('api/blockchain/', include('blockchain.urls')),
    path('api/proposals/', include('proposals.urls')),
    path('api/notifications/', include('notifications.urls')),

    # ----- Frontend page routes -----
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('verify-email/', TemplateView.as_view(template_name='verify-email.html'), name='verify_email_page'),
    path('notifications/', TemplateView.as_view(template_name='notificationsystem.html'), name='notifications'),
    path('chat/', TemplateView.as_view(template_name='messagingsystem.html'), name='chat'),

    # Client dashboard pages
    path('client/dashboard/', TemplateView.as_view(template_name='client_dashboard/dashboard.html'), name='client_dashboard'),
    path('client/projects/', TemplateView.as_view(template_name='client_dashboard/projectmanagement.html'), name='client_projects'),
    path('client/projects/new/', TemplateView.as_view(template_name='client_dashboard/newproject.html'), name='new_project'),
    path('client/freelancers/', TemplateView.as_view(template_name='client_dashboard/Freelancers.html'), name='client_freelancers'),
    path('client/reports/', TemplateView.as_view(template_name='client_dashboard/reports.html'), name='client_reports'),
    path('client/proposals/', TemplateView.as_view(template_name='client_dashboard/proposals.html'), name='client_proposals'),
    path('client/escrow/fund/<int:proposal_id>/', TemplateView.as_view(template_name='client_dashboard/fund_escrow.html'), name='fund_escrow'),
    path('client/projects/<int:project_id>/review/', TemplateView.as_view(template_name='client_dashboard/project_review.html'), name='project_review'),

    # Freelancer dashboard pages
    path('freelancer/dashboard/', TemplateView.as_view(template_name='freelancer_dashboard/Freelancersdashboard.html'), name='freelancer_dashboard'),
    path('freelancer/projects/', TemplateView.as_view(template_name='freelancer_dashboard/projects.html'), name='freelancer_projects'),
    path('freelancer/proposals/', TemplateView.as_view(template_name='freelancer_dashboard/proposal.html'), name='freelancer_proposals'),
    path('freelancer/earnings/', TemplateView.as_view(template_name='freelancer_dashboard/earningdashboard.html'), name='freelancer_earnings'),
    path('freelancer/workspace/', TemplateView.as_view(template_name='freelancer_dashboard/projectworkspace.html'), name='freelancer_workspace'),
    path('freelancer/profile/edit/', TemplateView.as_view(template_name='freelancer_dashboard/edit_profile.html'), name='freelancer_profile_edit'),
    path('freelancer/profile/<int:pk>/', TemplateView.as_view(template_name='freelancer_dashboard/profile.html'), name='freelancer_profile_page'),
    path('freelancer/reports/', TemplateView.as_view(template_name='freelancer_dashboard/reports.html'), name='freelancer_reports'),

    # Project detail page
    path('projects/<int:project_id>/', TemplateView.as_view(template_name='project_detail.html'), name='project_detail'),

    # Admin panel pages
    path('admin-panel/', TemplateView.as_view(template_name='admin_panel/admin_dashboard.html'), name='admin_dashboard'),
    path('admin-panel/users/', TemplateView.as_view(template_name='admin_panel/usermanagement.html'), name='admin_users'),
    path('admin-panel/projects/', TemplateView.as_view(template_name='admin_panel/projectmonitoring.html'), name='admin_projects'),
    path('admin-panel/fraud/', TemplateView.as_view(template_name='admin_panel/fraudmonitoring.html'), name='admin_fraud'),
    path('admin-panel/reports/', TemplateView.as_view(template_name='admin_panel/reports&analytics.html'), name='admin_reports'),

    path('client/workspace/<int:pk>/', TemplateView.as_view(template_name='client_dashboard/projectworkspace.html'), name='project_workspace'),

    # Settings page
    path('settings/', TemplateView.as_view(template_name='settings.html'), name='settings'),
]
