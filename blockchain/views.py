from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EscrowTransaction
from .serializers import EscrowTransactionSerializer
from .web3_client import get_escrow_status


class EscrowViewSet(viewsets.ModelViewSet):
    serializer_class = EscrowTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return EscrowTransaction.objects.all().order_by('-created_at')
        return (
            EscrowTransaction.objects.filter(client=user) |
            EscrowTransaction.objects.filter(freelancer=user)
        ).distinct().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Create a pending escrow record in Django.
        Actual funding happens on the frontend via MetaMask.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=request.user, status='EMPTY')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def blockchain_status(self, request, pk=None):
        """Fetch live escrow status directly from the blockchain."""
        escrow = self.get_object()
        project_id = str(escrow.project.id)
        chain_status = get_escrow_status(project_id)

        if 'error' in chain_status:
            return Response(
                {'error': chain_status['error']},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Sync Django DB status with blockchain
        escrow.status = chain_status['status']
        escrow.save(update_fields=['status'])

        return Response({
            'django_record': EscrowTransactionSerializer(escrow).data,
            'blockchain': chain_status
        })

    @action(detail=True, methods=['post'])
    def sync_status(self, request, pk=None):
        """
        Called by frontend after a MetaMask transaction completes.
        Updates Django DB to match blockchain state.
        Includes idempotency check and notification triggers.
        """
        escrow = self.get_object()
        tx_hash = request.data.get('tx_hash')
        tx_type = request.data.get('tx_type')  # funded / released / refunded / disputed

        # ── Ownership validation ────────────────────────────────────────
        user = request.user
        if tx_type in ('funded',) and user != escrow.client:
            return Response({'error': 'Only the client can fund this escrow.'},
                            status=status.HTTP_403_FORBIDDEN)
        if tx_type in ('released',) and user != escrow.client:
            return Response({'error': 'Only the client can release funds.'},
                            status=status.HTTP_403_FORBIDDEN)

        # ── Idempotency check ───────────────────────────────────────────
        if tx_type == 'funded' and escrow.tx_hash_funded == tx_hash:
            return Response({'message': 'Already synced.', 'data': EscrowTransactionSerializer(escrow).data})
        if tx_type == 'released' and escrow.tx_hash_released == tx_hash:
            return Response({'message': 'Already synced.', 'data': EscrowTransactionSerializer(escrow).data})
        if tx_type == 'refunded' and escrow.tx_hash_refunded == tx_hash:
            return Response({'message': 'Already synced.', 'data': EscrowTransactionSerializer(escrow).data})

        # ── Update state ────────────────────────────────────────────────
        from notifications.models import Notification

        if tx_type == 'funded':
            escrow.tx_hash_funded = tx_hash
            escrow.status = 'FUNDED'
            # Update client wallet from request if provided
            client_wallet = request.data.get('client_wallet')
            if client_wallet:
                escrow.client_wallet = client_wallet
            # Notify freelancer
            Notification.objects.create(
                user=escrow.freelancer,
                notif_type='FUNDED',
                title='Escrow Funded!',
                message=f'The client has funded {escrow.amount_eth} ETH for "{escrow.project.title}". You can start working!',
                related_project_id=escrow.project.id,
            )

        elif tx_type == 'released':
            escrow.tx_hash_released = tx_hash
            escrow.status = 'RELEASED'
            # Update freelancer earnings
            try:
                from accounts.models import FreelancerProfile
                fp = FreelancerProfile.objects.get(user=escrow.freelancer)
                fp.total_earnings += escrow.amount_eth
                fp.save(update_fields=['total_earnings'])
            except Exception:
                pass
            # Notify freelancer
            Notification.objects.create(
                user=escrow.freelancer,
                notif_type='RELEASED',
                title='Payment Released!',
                message=f'{escrow.amount_eth} ETH has been released to your wallet for "{escrow.project.title}".',
                related_project_id=escrow.project.id,
            )

        elif tx_type == 'refunded':
            escrow.tx_hash_refunded = tx_hash
            escrow.status = 'REFUNDED'
            # Notify both parties
            Notification.objects.create(
                user=escrow.freelancer,
                notif_type='GENERAL',
                title='Escrow Refunded',
                message=f'The escrow for "{escrow.project.title}" has been refunded to the client.',
                related_project_id=escrow.project.id,
            )

        elif tx_type == 'disputed':
            escrow.status = 'DISPUTED'
            # Notify both parties
            Notification.objects.create(
                user=escrow.freelancer,
                notif_type='DISPUTED',
                title='Dispute Raised',
                message=f'A dispute has been raised for "{escrow.project.title}". An admin will review.',
                related_project_id=escrow.project.id,
            )
            Notification.objects.create(
                user=escrow.client,
                notif_type='DISPUTED',
                title='Dispute Raised',
                message=f'A dispute has been raised for "{escrow.project.title}". An admin will review.',
                related_project_id=escrow.project.id,
            )

        escrow.save()
        return Response(EscrowTransactionSerializer(escrow).data)


class FreelancerWalletSummaryView(APIView):
    """
    GET /api/blockchain/wallet-summary/
    Returns aggregated wallet/escrow data for the logged-in freelancer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        escrows = EscrowTransaction.objects.filter(freelancer=user)

        funded = escrows.filter(status='FUNDED')
        released = escrows.filter(status='RELEASED')
        disputed = escrows.filter(status='DISPUTED')

        from django.db.models import Sum

        pending_eth = funded.aggregate(total=Sum('amount_eth'))['total'] or 0
        released_eth = released.aggregate(total=Sum('amount_eth'))['total'] or 0
        disputed_eth = disputed.aggregate(total=Sum('amount_eth'))['total'] or 0

        # Get freelancer's wallet address
        wallet_address = ''
        try:
            from accounts.models import FreelancerProfile
            fp = FreelancerProfile.objects.get(user=user)
            wallet_address = fp.eth_wallet_address or ''
        except Exception:
            pass

        # Recent transactions (last 20)
        recent = escrows.order_by('-updated_at')[:20]
        transactions = EscrowTransactionSerializer(recent, many=True).data

        return Response({
            'wallet_address': wallet_address,
            'pending_escrow_eth': float(pending_eth),
            'released_eth': float(released_eth),
            'disputed_eth': float(disputed_eth),
            'total_earned_eth': float(released_eth),
            'total_transactions': escrows.count(),
            'transactions': transactions,
        })
    
import os
 
class ContractAddressView(APIView):
    """
    GET /api/escrow/contract-address/
    Returns the deployed contract address from environment.
    """
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        address = os.environ.get('CONTRACT_ADDRESS', '')
        if not address:
            return Response({'error': 'Contract address not configured.'}, status=500)
        return Response({'address': address})