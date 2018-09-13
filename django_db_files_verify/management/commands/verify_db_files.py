from django.core.management.base import BaseCommand, CommandError
from verify_db.verify import VerifyFilerFields 

class Command(BaseCommand):
    help = 'Verify models files exists in storage'

    def handle(self, *args, **options):
        VerifyFilerFields()