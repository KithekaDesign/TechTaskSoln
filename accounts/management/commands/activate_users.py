"""
Management command: activate_users
===================================
Fixes users who are stuck in an unverified / inactive state.

Usage:
    # Activate ALL unverified / inactive users at once (useful in dev):
    python manage.py activate_users --all

    # Activate a single user by username:
    python manage.py activate_users --username john

    # Activate a single user by email:
    python manage.py activate_users --email john@example.com

    # List all users and their verification status:
    python manage.py activate_users --list
"""

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Activate / verify users who are stuck in unverified state'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Activate ALL unverified/inactive users')
        parser.add_argument('--username', type=str, help='Activate a specific user by username')
        parser.add_argument('--email', type=str, help='Activate a specific user by email')
        parser.add_argument('--list', action='store_true', help='List all users and their status')

    def _activate(self, user):
        user.is_email_verified = True
        user.is_active = True
        user.email_otp = None
        user.otp_created_at = None
        user.save()
        self.stdout.write(self.style.SUCCESS(  # type: ignore[attr-defined]
            f'  [OK] Activated: {user.username} ({user.email}) '
            f'[{"freelancer" if user.is_freelancer else "client" if user.is_client else "staff"}]'
        ))

    def handle(self, *args, **options):
        if options['list']:
            users = User.objects.all().order_by('date_joined')
            self.stdout.write(self.style.MIGRATE_HEADING('\nAll users:'))  # type: ignore[attr-defined]
            self.stdout.write(f'{"Username":<25} {"Email":<35} {"Active":<8} {"Verified":<10} {"Role"}')
            self.stdout.write('-' * 90)
            for u in users:
                role = 'superuser' if u.is_superuser else 'staff' if u.is_staff else 'freelancer' if u.is_freelancer else 'client'
                self.stdout.write(
                    f'{u.username:<25} {u.email:<35} {str(u.is_active):<8} {str(u.is_email_verified):<10} {role}'
                )
            return

        if options['all']:
            stuck = User.objects.filter(is_email_verified=False) | User.objects.filter(is_active=False)
            stuck = stuck.distinct()
            count = stuck.count()
            if count == 0:
                self.stdout.write(self.style.WARNING('No stuck users found. All users are already active & verified.'))  # type: ignore[attr-defined]
                return
            self.stdout.write(self.style.MIGRATE_HEADING(f'\nActivating {count} user(s)...'))  # type: ignore[attr-defined]
            for user in stuck:
                self._activate(user)
            self.stdout.write(self.style.SUCCESS(f'\nDone. {count} user(s) activated.'))  # type: ignore[attr-defined]
            return

        if options['username']:
            try:
                user = User.objects.get(username=options['username'])
                self._activate(user)
            except User.DoesNotExist:  # type: ignore[attr-defined]
                self.stdout.write(self.style.ERROR(f'User "{options["username"]}" not found.'))  # type: ignore[attr-defined]
            return

        if options['email']:
            try:
                user = User.objects.get(email=options['email'])
                self._activate(user)
            except User.DoesNotExist:  # type: ignore[attr-defined]
                self.stdout.write(self.style.ERROR(f'No user with email "{options["email"]}" found.'))  # type: ignore[attr-defined]
            return

        # No flags provided
        self.stdout.write(self.style.WARNING(  # type: ignore[attr-defined]
            'No option specified. Use --all, --username, --email, or --list.\n'
            'Run: python manage.py activate_users --help'
        ))
