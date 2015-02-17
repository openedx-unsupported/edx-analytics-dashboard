from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.utils import delete_auto_auth_users


User = get_user_model()


class Command(BaseCommand):
    """A command to remove all users created via the auto-auth endpoint."""

    help = 'Delete auto-auth users.'

    def handle(self, *args, **options):
        delete_auto_auth_users()
