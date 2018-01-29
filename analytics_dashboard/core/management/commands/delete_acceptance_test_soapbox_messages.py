from django.core.management.base import BaseCommand

from core.utils import delete_fake_soapbox_messages


class Command(BaseCommand):
    """A command to delete the fake soapbox messages that the acceptance tests have completed checking."""
    help = 'Delete fake soapbox messages for testing.'

    def handle(self, *args, **options):
        delete_fake_soapbox_messages()
