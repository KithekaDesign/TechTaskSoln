from django.urls import path
from .views import (
    SubmitProposalView, MyProposalsView,
    ProjectProposalsView, ProposalFundingContextView,
    AcceptProposalView, RejectProposalView, ProposalDetailView
)

urlpatterns = [
    path('submit/', SubmitProposalView.as_view(), name='submit_proposal'),
    path('mine/', MyProposalsView.as_view(), name='my_proposals'),
    path('project/<int:project_id>/', ProjectProposalsView.as_view(), name='project_proposals'),
    path('<int:pk>/funding-context/', ProposalFundingContextView.as_view(), name='proposal_funding_context'),
    path('<int:pk>/accept/', AcceptProposalView.as_view(), name='accept_proposal'),
    path('<int:pk>/reject/', RejectProposalView.as_view(), name='reject_proposal'),
    path('<int:pk>/detail/', ProposalDetailView.as_view(), name='proposal_detail'),
]
