from django.core.management.base import BaseCommand
from django.core.management import call_command
from ancillary_info.models import Companies
from financial_reports.models import FinancialReports
from api_import.vendors.fmp.client import FMPClient

import pandas as pd


class Command(BaseCommand):
    help = "Check FMP for updated financial statements and import if newer data exists"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Check for updates but do not import",
        )

    def handle(self, *args, **options):
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        if options["symbol"] is None:
            comp_list = df_companies[df_companies["country__value"] == "US"]["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        fmp = FMPClient()
        companies_to_update = []

        for company_tidm in comp_list:
            curr_comp_loc = df_companies[
                df_companies["tidm"] == company_tidm
            ]["country__value"].values[0]

            if curr_comp_loc != "United States":
                continue

            # Get latest date in DB for this company
            latest_db = FinancialReports.objects.get_latest_date(company_tidm)
            db_date = latest_db.time_stamp if latest_db else None

            # Get latest date available from FMP
            fmp_date_str = fmp.get_latest_report_date(company_tidm, "income-statement")

            if not fmp_date_str:
                self.stdout.write(f"  {company_tidm}: no FMP data")
                continue

            fmp_date = pd.to_datetime(fmp_date_str).date()

            if db_date is None or fmp_date > db_date:
                status = "NEW DATA" if db_date is None else f"FMP {fmp_date} > DB {db_date}"
                self.stdout.write(f"  {company_tidm}: {status} — queued for import")
                companies_to_update.append(company_tidm)
            else:
                self.stdout.write(f"  {company_tidm}: up to date (latest: {db_date})")

        if companies_to_update and not options["dry_run"]:
            self.stdout.write(
                f"\nImporting {len(companies_to_update)} companies: {companies_to_update}"
            )
            call_command("financial_reports_import_fmp", symbol=companies_to_update)
        elif companies_to_update and options["dry_run"]:
            self.stdout.write(
                f"\nDry run — would import {len(companies_to_update)} companies: {companies_to_update}"
            )
        else:
            self.stdout.write("\nAll companies are up to date.")

        return f"Checked: {len(comp_list)}, Queued: {len(companies_to_update)}"
