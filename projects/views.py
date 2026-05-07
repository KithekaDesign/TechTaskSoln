from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project
from proposals.models import Proposal
from .serializers import ProjectSerializer
from .permissions import IsClient, IsFreelancer


class DashboardStatsView(APIView):
    """Return dashboard statistics for the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_client:
            active_projects = Project.objects.filter(client=user, status='IN_PROGRESS').count()
            open_projects = Project.objects.filter(client=user, status='OPEN').count()
            completed_projects = Project.objects.filter(client=user, status='COMPLETED').count()
            total_proposals = Proposal.objects.filter(project__client=user).count()
            pending_proposals = Proposal.objects.filter(project__client=user, status='PENDING').count()

            return Response({
                'active_projects': active_projects,
                'open_projects': open_projects,
                'completed_projects': completed_projects,
                'total_proposals': total_proposals,
                'pending_proposals': pending_proposals,
                'total_projects': active_projects + open_projects + completed_projects,
            })
        elif user.is_freelancer:
            accepted_proposals = Proposal.objects.filter(freelancer=user, status='ACCEPTED').count()
            pending_proposals = Proposal.objects.filter(freelancer=user, status='PENDING').count()
            total_proposals = Proposal.objects.filter(freelancer=user).count()
            active_projects = Project.objects.filter(
                proposals__freelancer=user, proposals__status='ACCEPTED', status='IN_PROGRESS'
            ).distinct().count()

            return Response({
                'active_projects': active_projects,
                'accepted_proposals': accepted_proposals,
                'pending_proposals': pending_proposals,
                'total_proposals': total_proposals,
            })
        else:
            # Admin / staff stats
            total_users = 0
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                total_users = User.objects.count()
            except Exception:
                pass

            return Response({
                'total_projects': Project.objects.count(),
                'open_projects': Project.objects.filter(status='OPEN').count(),
                'in_progress_projects': Project.objects.filter(status='IN_PROGRESS').count(),
                'completed_projects': Project.objects.filter(status='COMPLETED').count(),
                'total_proposals': Proposal.objects.count(),
                'total_users': total_users,
            })


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        """Allow any authenticated user to list/retrieve, but only clients can create/update/delete."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action == 'mark_complete':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsClient()]

    def get_queryset(self):
        """
        ?mine=true  → Client sees only their own projects
        ?status=X   → Filter by status
        Default     → All projects (for freelancers browsing)
        """
        qs = Project.objects.all().order_by('-created_at')
        user = self.request.user

        mine = self.request.query_params.get('mine')
        if mine == 'true' and user.is_client:
            qs = qs.filter(client=user)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        return qs

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """
        Freelancer marks a project as completed.
        Only allowed when:
          - The user is the assigned freelancer (has accepted proposal)
          - Project status is IN_PROGRESS
          - Escrow is FUNDED
        """
        project = self.get_object()
        user = request.user

        # Verify the user is the assigned freelancer
        accepted = Proposal.objects.filter(
            project=project, freelancer=user, status='ACCEPTED'
        ).first()
        if not accepted:
            return Response({'error': 'Only the assigned freelancer can mark this complete.'},
                            status=status.HTTP_403_FORBIDDEN)

        if project.status != 'IN_PROGRESS':
            return Response({'error': 'Project is not in progress.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Verify escrow is funded
        try:
            from blockchain.models import EscrowTransaction
            escrow = EscrowTransaction.objects.get(project=project)
            if escrow.status != 'FUNDED':
                return Response({'error': 'Escrow is not funded yet.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'No escrow record found for this project.'},
                            status=status.HTTP_400_BAD_REQUEST)

        project.status = 'COMPLETED'
        project.save()

        # Notify client
        from projects.utils import create_notification
        create_notification(
            user=project.client,
            message=f'Freelancer {user.username} has marked "{project.title}" as completed. Please review and release funds.',
            title='Project Completed — Review Required',
            notif_type='COMPLETED',
            related_project_id=project.id,
        )

        return Response({
            'message': 'Project marked as completed. The client has been notified to review.',
            'project_id': project.id,
        })