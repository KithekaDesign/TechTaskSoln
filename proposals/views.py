from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from projects.models import Project

from .models import Proposal
from .serializers import ProposalSerializer


class SubmitProposalView(generics.CreateAPIView):
    """
    POST /api/proposals/submit/
    Freelancer submits a proposal for a project.
    """
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_freelancer:
            return Response({'error': 'Only freelancers can submit proposals.'}, status=403)

        project_id = request.data.get('project')
        project = get_object_or_404(Project, pk=project_id)

        if Proposal.objects.filter(project=project, freelancer=request.user).exists():
            return Response({'error': 'You have already submitted a proposal for this project.'}, status=400)

        if project.client == request.user:
            return Response({'error': 'You cannot submit a proposal on your own project.'}, status=400)

        if project.status != 'OPEN':
            return Response({'error': 'This project is no longer accepting proposals.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(freelancer=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyProposalsView(generics.ListAPIView):
    """
    GET /api/proposals/mine/
    Freelancer sees all their submitted proposals.
    """
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(
            freelancer=self.request.user
        ).select_related('project', 'freelancer').order_by('-created_at')


class ProjectProposalsView(generics.ListAPIView):
    """
    GET /api/proposals/project/<project_id>/
    Client sees all proposals for their project.
    """
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, pk=project_id, client=self.request.user)
        return Proposal.objects.filter(
            project=project
        ).select_related('project', 'freelancer').order_by('-created_at')


class ProposalFundingContextView(APIView):
    """
    GET /api/proposals/<id>/funding-context/
    Returns the proposal and linked escrow used by the funding page.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        proposal = get_object_or_404(
            Proposal.objects.select_related('project', 'freelancer', 'project__client'),
            pk=pk,
        )

        is_allowed = (
            request.user.is_staff or
            proposal.project.client == request.user or
            proposal.freelancer == request.user
        )
        if not is_allowed:
            return Response({'error': 'You do not have permission to view this proposal.'}, status=403)

        escrow_data = None
        try:
            from blockchain.models import EscrowTransaction
            from blockchain.serializers import EscrowTransactionSerializer

            escrow = EscrowTransaction.objects.select_related('project', 'client', 'freelancer').get(
                project=proposal.project
            )
            escrow_data = EscrowTransactionSerializer(escrow).data
        except Exception:
            escrow_data = None

        return Response({
            'proposal': ProposalSerializer(proposal).data,
            'escrow': escrow_data,
            'can_fund_escrow': proposal.project.client == request.user,
        })


class AcceptProposalView(APIView):
    """
    POST /api/proposals/<id>/accept/
    Client accepts a proposal and prepares escrow funding.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(
            Proposal.objects.select_related('project', 'freelancer', 'project__client'),
            pk=pk,
        )

        if proposal.project.client != request.user:
            return Response({'error': 'Only the project client can accept proposals.'}, status=403)

        if proposal.status != 'PENDING':
            return Response({'error': f'Proposal is already {proposal.status}.'}, status=400)

        project = proposal.project
        rejected_qs = Proposal.objects.filter(project=project).exclude(pk=pk)
        rejected_freelancers = list(rejected_qs.select_related('freelancer'))
        escrow = None

        with transaction.atomic():
            proposal.status = 'ACCEPTED'
            proposal.save(update_fields=['status'])

            project.status = 'IN_PROGRESS'
            project.save(update_fields=['status'])

            rejected_qs.update(status='REJECTED')

            try:
                from accounts.models import FreelancerProfile
                from blockchain.models import EscrowTransaction

                freelancer_wallet = ''
                try:
                    profile = FreelancerProfile.objects.get(user=proposal.freelancer)
                    freelancer_wallet = profile.eth_wallet_address or ''
                except FreelancerProfile.DoesNotExist:
                    pass

                escrow, _ = EscrowTransaction.objects.update_or_create(
                    project=project,
                    defaults={
                        'client': request.user,
                        'freelancer': proposal.freelancer,
                        'client_wallet': '',
                        'freelancer_wallet': freelancer_wallet,
                        'amount_eth': proposal.bid_amount,
                        'status': 'EMPTY',
                        'tx_hash_funded': None,
                        'tx_hash_released': None,
                        'tx_hash_refunded': None,
                    },
                )
            except Exception as exc:
                import logging

                logging.getLogger(__name__).warning(f"Failed to create escrow record: {exc}")

        Notification.objects.create(
            user=proposal.freelancer,
            notif_type='ACCEPTED',
            title='Proposal Accepted!',
            message=f'Your proposal for "{project.title}" has been accepted. The client will now fund the escrow.',
            related_proposal_id=proposal.id,
            related_project_id=project.id,
        )

        for rejected in rejected_freelancers:
            Notification.objects.create(
                user=rejected.freelancer,
                notif_type='REJECTED',
                title='Proposal Not Selected',
                message=f'Your proposal for "{project.title}" was not selected this time.',
                related_project_id=project.id,
            )

        return Response({
            'message': 'Proposal accepted. Freelancer has been notified.',
            'proposal': ProposalSerializer(proposal).data,
            'escrow_id': escrow.id if escrow else None,
            'project_id': project.id,
            'redirect': f'/client/escrow/fund/{proposal.id}/',
        })


class RejectProposalView(APIView):
    """
    POST /api/proposals/<id>/reject/
    Client rejects a single proposal.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)

        if proposal.project.client != request.user:
            return Response({'error': 'Only the project client can reject proposals.'}, status=403)

        if proposal.status != 'PENDING':
            return Response({'error': f'Proposal is already {proposal.status}.'}, status=400)

        proposal.status = 'REJECTED'
        proposal.save()

        Notification.objects.create(
            user=proposal.freelancer,
            notif_type='REJECTED',
            title='Proposal Not Selected',
            message=f'Your proposal for "{proposal.project.title}" was not selected.',
            related_project_id=proposal.project.id,
        )

        return Response({'message': 'Proposal rejected.'})

# ── ADD to proposals/views.py ─────────────────────────────────────────────

class ProposalDetailView(generics.RetrieveAPIView):
    """
    GET /api/proposals/<id>/detail/
    Returns full proposal with freelancer profile — used by escrow fund page.
    """
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Client can see proposals for their projects, freelancer can see their own
        from projects.models import Project
        if user.is_client:
            return Proposal.objects.filter(project__client=user)
        return Proposal.objects.filter(freelancer=user)
