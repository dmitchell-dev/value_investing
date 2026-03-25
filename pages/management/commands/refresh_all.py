"""
Management command to refresh all calculated data in one step.

Usage:
    python manage.py refresh_all
    python manage.py refresh_all --flush   # re-seed first (dev only)
    python manage.py refresh_all --symbol AAPL MSFT  # specific companies only
"""
from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = "Seed (optional), calculate stats, and regenerate dashboard in one step"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush and re-seed data before recalculating (dev only)",
        )
        parser.add_argument(
            "--symbol",
            nargs="+",
            type=str,
            help="Limit calculate_stats to specific ticker symbols",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Seeding data...")
            management.call_command("seed_data", flush=True)
            self.stdout.write(self.style.SUCCESS("Seed complete."))

        self.stdout.write("Calculating stats...")
        calc_kwargs = {}
        if options["symbol"]:
            calc_kwargs["symbol"] = options["symbol"]
        management.call_command("calculate_stats", **calc_kwargs)
        self.stdout.write(self.style.SUCCESS("Stats complete."))

        self.stdout.write("Generating dashboard...")
        management.call_command("generate_dashboard")
        self.stdout.write(self.style.SUCCESS("Dashboard complete."))
