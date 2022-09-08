import time
import schedule
from django.core.management.base import BaseCommand
from gsheets.script.script import main


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        main()
        schedule.every(5).minutes.do(main)  # Run every 'n' minutes
        while True:
            schedule.run_pending()
            time.sleep(1)