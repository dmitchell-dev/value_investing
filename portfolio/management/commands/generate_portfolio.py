from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates portfolio stats"

    def handle(self, *args, **kwargs):
        print("generate_portfolio")
