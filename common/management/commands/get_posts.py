from django.core.management.base import NoArgsCommand
from common.utils import get_all_uids

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        get_all_uids()