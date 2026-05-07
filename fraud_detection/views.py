from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FraudFlag
from .serializers import FraudFlagSerializer


class FraudFlagViewSet(viewsets.ModelViewSet):
    queryset = FraudFlag.objects.all()
    serializer_class = FraudFlagSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return FraudFlag.objects.all().order_by('-created_at')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def resolve(self, request, pk=None):
        flag = self.get_object()
        flag.is_resolved = True
        flag.save()
        return Response({'message': 'Fraud flag resolved.'})