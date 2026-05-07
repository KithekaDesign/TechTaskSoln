from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import FreelancerProfile
from blockchain.models import EscrowTransaction
from notifications.models import Notification
from projects.models import Project
from proposals.models import Proposal


User = get_user_model()


class ProposalAcceptanceFlowTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='StrongPass123',
            is_client=True,
        )
        self.freelancer = User.objects.create_user(
            username='freelancer1',
            email='freelancer1@example.com',
            password='StrongPass123',
            is_freelancer=True,
        )
        self.other_freelancer = User.objects.create_user(
            username='freelancer2',
            email='freelancer2@example.com',
            password='StrongPass123',
            is_freelancer=True,
        )

        FreelancerProfile.objects.create(
            user=self.freelancer,
            skills='Solidity, Django',
            experience_level='Senior',
            hourly_rate=50,
            eth_wallet_address='0x1234567890123456789012345678901234567890',
        )
        FreelancerProfile.objects.create(
            user=self.other_freelancer,
            skills='React',
            experience_level='Mid',
            hourly_rate=30,
            eth_wallet_address='0x0987654321098765432109876543210987654321',
        )

        self.project = Project.objects.create(
            client=self.client_user,
            title='Escrow Project',
            description='Test project',
            budget='200.00',
            required_skills='Django, Solidity',
            deadline='2026-05-01',
        )

        self.proposal = Proposal.objects.create(
            project=self.project,
            freelancer=self.freelancer,
            cover_letter='I can build this.',
            bid_amount='1.50',
            delivery_time=5,
        )
        self.other_proposal = Proposal.objects.create(
            project=self.project,
            freelancer=self.other_freelancer,
            cover_letter='Pick me instead.',
            bid_amount='1.20',
            delivery_time=7,
        )

        self.client.force_authenticate(user=self.client_user)

    def test_accepting_proposal_creates_or_updates_linked_escrow(self):
        response = self.client.post(reverse('accept_proposal', kwargs={'pk': self.proposal.id}))

        self.assertEqual(response.status_code, 200)

        self.proposal.refresh_from_db()
        self.other_proposal.refresh_from_db()
        self.project.refresh_from_db()

        escrow = EscrowTransaction.objects.get(project=self.project)

        self.assertEqual(self.proposal.status, 'ACCEPTED')
        self.assertEqual(self.other_proposal.status, 'REJECTED')
        self.assertEqual(self.project.status, 'IN_PROGRESS')
        self.assertEqual(escrow.amount_eth, Decimal('1.50'))
        self.assertEqual(escrow.freelancer, self.freelancer)
        self.assertEqual(
            escrow.freelancer_wallet,
            '0x1234567890123456789012345678901234567890',
        )
        self.assertEqual(response.data['redirect'], f'/client/escrow/fund/{self.proposal.id}/')

        self.assertTrue(
            Notification.objects.filter(
                user=self.freelancer,
                notif_type='ACCEPTED',
                related_project_id=self.project.id,
            ).exists()
        )

    def test_funding_context_returns_exact_accepted_proposal_and_escrow(self):
        self.client.post(reverse('accept_proposal', kwargs={'pk': self.proposal.id}))

        response = self.client.get(reverse('proposal_funding_context', kwargs={'pk': self.proposal.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['proposal']['id'], self.proposal.id)
        self.assertEqual(response.data['proposal']['status'], 'ACCEPTED')
        self.assertEqual(response.data['escrow']['project'], self.project.id)
        self.assertEqual(response.data['escrow']['freelancer_username'], 'freelancer1')
