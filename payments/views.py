from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return payments where the user is either payer or payee."""
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all().order_by('-created_at')
        return Payment.objects.filter(
            payer=user
        ) | Payment.objects.filter(
            payee=user
        )

    def perform_create(self, serializer):
        serializer.save(payer=self.request.user)

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        payment = self.get_object()
        if payment.payer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the payer can release this payment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        payment.status = 'RELEASED'
        payment.save()
        return Response({'message': 'Payment released successfully.'})

    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'DISPUTED'
        payment.save()
        return Response({'message': 'Payment disputed. Admin will review.'})
