from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Calculates Stats from Financial Reports"

    def handle(self, *args, **kwargs):
        pass
