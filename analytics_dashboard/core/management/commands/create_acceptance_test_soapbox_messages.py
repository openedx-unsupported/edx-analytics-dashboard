from django.core.management.base import BaseCommand

from core.utils import create_fake_soapbox_messages


class Command(BaseCommand):
    """A command to create fake soapbox messages that the acceptance tests will check if displayed."""
    help = 'Create fake soapbox messages for testing.'

    def handle(self, *args, **options):
        create_fake_soapbox_messages()
