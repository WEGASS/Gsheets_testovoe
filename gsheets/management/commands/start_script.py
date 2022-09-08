from django.core.management.base import BaseCommand
from gsheets.script.script import main


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        main()
