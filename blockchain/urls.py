from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EscrowViewSet, FreelancerWalletSummaryView, ContractAddressView

router = DefaultRouter()
router.register(r'escrow', EscrowViewSet, basename='escrow')

urlpatterns = router.urls + [
    path('wallet-summary/', FreelancerWalletSummaryView.as_view(), name='wallet_summary'),
    path('escrow/contract-address/', ContractAddressView.as_view(), name='contract_address'),
]