from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import csv
import io

from .models import Report
from .serializers import ReportSerializer
from projects.models import Project
from proposals.models import Proposal
from payments.models import Payment


# ── Existing view (unchanged) ─────────────────────────────────────────────────

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Report.objects.all().order_by('-created_at')
        return Report.objects.filter(reported_by=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


# ── New analytics view ────────────────────────────────────────────────────────

class FreelancerAnalyticsView(APIView):
    """
    Returns all analytics data for the logged-in freelancer.
    GET /api/reports/freelancer/analytics/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_freelancer:
            return Response(
                {'error': 'Only freelancers can access this report.'},
                status=403
            )

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        twelve_months_ago = now - timedelta(days=365)

        # ── PROPOSALS ────────────────────────────────────────────────
        proposals = Proposal.objects.filter(freelancer=user)
        total_proposals    = proposals.count()
        accepted_proposals = proposals.filter(status='ACCEPTED').count()
        rejected_proposals = proposals.filter(status='REJECTED').count()
        pending_proposals  = proposals.filter(status='PENDING').count()
        success_rate = (
            round(accepted_proposals / total_proposals * 100, 1)
            if total_proposals > 0 else 0
        )

        # ── PROJECTS ─────────────────────────────────────────────────
        active_projects = Project.objects.filter(
            proposals__freelancer=user,
            proposals__status='ACCEPTED',
            status='IN_PROGRESS'
        ).distinct().count()

        completed_projects = Project.objects.filter(
            proposals__freelancer=user,
            proposals__status='ACCEPTED',
            status='COMPLETED'
        ).distinct().count()

        total_projects  = active_projects + completed_projects
        completion_rate = (
            round(completed_projects / total_projects * 100, 1)
            if total_projects > 0 else 0
        )

        # ── EARNINGS ─────────────────────────────────────────────────
        payments = Payment.objects.filter(payee=user, status='RELEASED')

        total_earned = payments.aggregate(
            total=Sum('amount'))['total'] or 0
        this_month_earned = payments.filter(
            created_at__gte=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).aggregate(total=Sum('amount'))['total'] or 0
        last_30_days_earned = payments.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        avg_project_value = payments.aggregate(
            avg=Avg('amount'))['avg'] or 0

        # ── MONTHLY EARNINGS (last 12 months) ────────────────────────
        monthly_earnings = (
            payments
            .filter(created_at__gte=twelve_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        monthly_data = [
            {
                'month': entry['month'].strftime('%b %Y'),
                'total': float(entry['total'])
            }
            for entry in monthly_earnings
        ]

        # ── BREAKDOWNS (for charts) ───────────────────────────────────
        proposal_breakdown = [
            {'label': 'Accepted', 'value': accepted_proposals, 'color': '#22c55e'},
            {'label': 'Pending',  'value': pending_proposals,  'color': '#f59e0b'},
            {'label': 'Rejected', 'value': rejected_proposals, 'color': '#ef4444'},
        ]
        project_breakdown = [
            {'label': 'Completed',   'value': completed_projects, 'color': '#3b82f6'},
            {'label': 'In Progress', 'value': active_projects,    'color': '#8b5cf6'},
        ]

        return Response({
            'summary': {
                'total_earned':         float(total_earned),
                'this_month_earned':    float(this_month_earned),
                'last_30_days_earned':  float(last_30_days_earned),
                'avg_project_value':    round(float(avg_project_value), 2),
                'total_proposals':      total_proposals,
                'success_rate':         success_rate,
                'total_projects':       total_projects,
                'completed_projects':   completed_projects,
                'active_projects':      active_projects,
                'completion_rate':      completion_rate,
            },
            'monthly_earnings':   monthly_data,
            'proposal_breakdown': proposal_breakdown,
            'project_breakdown':  project_breakdown,
        })


class FreelancerReportExportView(APIView):
    """
    Exports the freelancer's analytics as a downloadable CSV.
    GET /api/reports/freelancer/export/?format=csv
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_freelancer:
            return Response({'error': 'Only freelancers can export reports.'}, status=403)

        now = timezone.now()
        twelve_months_ago = now - timedelta(days=365)

        payments = Payment.objects.filter(payee=user, status='RELEASED').select_related('project')

        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # ── Summary section ───────────────────────────────────────────
        writer.writerow(['TechTaskSoln — Freelancer Earnings Report'])
        writer.writerow(['Generated:', now.strftime('%Y-%m-%d %H:%M UTC')])
        writer.writerow(['Freelancer:', user.username, user.email])
        writer.writerow([])

        total_earned = payments.aggregate(total=Sum('amount'))['total'] or 0
        this_month   = payments.filter(
            created_at__gte=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).aggregate(total=Sum('amount'))['total'] or 0

        proposals = user.proposals.all() if hasattr(user, 'proposals') else []
        try:
            from proposals.models import Proposal as ProposalModel
            proposals = ProposalModel.objects.filter(freelancer=user)
            total_proposals    = proposals.count()
            accepted_proposals = proposals.filter(status='ACCEPTED').count()
            success_rate = round(accepted_proposals / total_proposals * 100, 1) if total_proposals > 0 else 0
        except Exception:
            total_proposals, accepted_proposals, success_rate = 0, 0, 0

        writer.writerow(['=== SUMMARY ==='])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Earned (USD)', f"${float(total_earned):,.2f}"])
        writer.writerow(['This Month Earned (USD)', f"${float(this_month):,.2f}"])
        writer.writerow(['Total Proposals', total_proposals])
        writer.writerow(['Accepted Proposals', accepted_proposals])
        writer.writerow(['Proposal Success Rate', f"{success_rate}%"])
        writer.writerow([])

        # ── Monthly earnings ──────────────────────────────────────────
        monthly = (
            payments
            .filter(created_at__gte=twelve_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        writer.writerow(['=== MONTHLY EARNINGS (Last 12 Months) ==='])
        writer.writerow(['Month', 'Amount (USD)'])
        for entry in monthly:
            writer.writerow([entry['month'].strftime('%B %Y'), f"${float(entry['total']):,.2f}"])
        writer.writerow([])

        # ── Individual transactions ───────────────────────────────────
        writer.writerow(['=== PAYMENT TRANSACTIONS ==='])
        writer.writerow(['Date', 'Project', 'Amount (USD)', 'Status'])
        for p in payments.order_by('-created_at'):
            writer.writerow([
                p.created_at.strftime('%Y-%m-%d'),
                p.project.title if hasattr(p, 'project') and p.project else 'N/A',
                f"${float(p.amount):,.2f}",
                p.status,
            ])

        csv_data = output.getvalue()
        output.close()

        filename = f"techtasksoln_report_{user.username}_{now.strftime('%Y%m%d')}.csv"
        response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ClientAnalyticsView(APIView):
    """
    Returns analytics data for the logged-in client.
    GET /api/reports/client/analytics/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_client:
            return Response(
                {'error': 'Only clients can access this report.'},
                status=403
            )

        now = timezone.now()

        # Projects
        total_projects = Project.objects.filter(client=user).count()
        open_projects = Project.objects.filter(client=user, status='OPEN').count()
        active_projects = Project.objects.filter(client=user, status='IN_PROGRESS').count()
        completed_projects = Project.objects.filter(client=user, status='COMPLETED').count()

        # Proposals
        total_proposals = Proposal.objects.filter(project__client=user).count()
        pending_proposals = Proposal.objects.filter(project__client=user, status='PENDING').count()
        accepted_proposals = Proposal.objects.filter(project__client=user, status='ACCEPTED').count()

        # Spending
        payments = Payment.objects.filter(payer=user)
        total_spent = payments.aggregate(total=Sum('amount'))['total'] or 0
        released_payments = payments.filter(status='RELEASED')
        total_released = released_payments.aggregate(total=Sum('amount'))['total'] or 0

        # Monthly spending
        twelve_months_ago = now - timedelta(days=365)
        monthly_spending = (
            released_payments
            .filter(created_at__gte=twelve_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        monthly_data = [
            {'month': entry['month'].strftime('%b %Y'), 'total': float(entry['total'])}
            for entry in monthly_spending
        ]

        return Response({
            'summary': {
                'total_projects': total_projects,
                'open_projects': open_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'total_proposals': total_proposals,
                'pending_proposals': pending_proposals,
                'accepted_proposals': accepted_proposals,
                'total_spent': float(total_spent),
                'total_released': float(total_released),
            },
            'monthly_spending': monthly_data,
        })