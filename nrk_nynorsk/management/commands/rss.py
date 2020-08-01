from django.core.management.base import BaseCommand, CommandError

from nrk_nynorsk import rss


class Command(BaseCommand):
    help = "Fetch new articles using RSS"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        rss.main()
