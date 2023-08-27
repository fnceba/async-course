from django.core.management.base import BaseCommand
from task_tracker.listener import EventListener


class Command(BaseCommand):
    help = 'Launches Listener'
    def handle(self, *args, **options):
        td = EventListener()
        td.start()
        self.stdout.write("Started Consumer Thread")