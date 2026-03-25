"""
Seeds only the reference/lookup tables required for import commands to work.
Does NOT create any companies, financial reports, share prices, or portfolio data.

Usage: python manage.py seed_reference_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from ancillary_info.models import (
    CompSource, CompanyType, Countries, Currencies, Datasource,
    DecisionType, Exchanges, Industries, Params, ParamsApi, ReportType, Sectors,
)

from pages.management.commands.seed_data import PARAMS_DATA


YF_PARAMS_API_MAPPINGS = [
    # (yfinance field name, param_name_col)
    ("Total Revenue",                           "revenue"),
    ("Gross Profit",                            "gross_profit"),
    ("Operating Income",                        "op_income"),
    ("Net Income",                              "net_income"),
    ("Interest Expense",                        "interest_expense"),
    ("Diluted EPS",                             "eps"),
    ("Diluted Average Shares",                  "shares_outstanding"),
    ("Total Assets",                            "total_assets"),
    ("Stockholders Equity",                     "total_equity"),
    ("Long Term Debt",                          "lt_debt"),
    ("Current Assets",                          "total_current_assets"),
    ("Current Liabilities",                     "total_current_liabilities"),
    ("Total Liabilities Net Minority Interest", "total_liabilities"),
    ("Cash And Cash Equivalents",               "total_cash"),
    ("Operating Cash Flow",                     "op_cashflow"),
    ("Capital Expenditure",                     "capex"),
    ("Free Cash Flow",                          "fcf"),
    ("Common Stock Dividend Paid",              "dividend_payout"),
    ("Depreciation And Amortization",           "dna"),
]

FMP_PARAMS_API_MAPPINGS = [
    ("revenue",                     "revenue"),
    ("grossProfit",                  "gross_profit"),
    ("operatingIncome",              "op_income"),
    ("netIncome",                    "net_income"),
    ("interestExpense",              "interest_expense"),
    ("epsDiluted",                   "eps"),
    ("weightedAverageShsOutDil",     "shares_outstanding"),
    ("totalAssets",                  "total_assets"),
    ("totalStockholdersEquity",      "total_equity"),
    ("longTermDebt",                 "lt_debt"),
    ("totalCurrentAssets",           "total_current_assets"),
    ("totalCurrentLiabilities",      "total_current_liabilities"),
    ("totalLiabilities",             "total_liabilities"),
    ("cashAndShortTermInvestments",  "total_cash"),
    ("operatingCashFlow",            "op_cashflow"),
    ("capitalExpenditure",           "capex"),
    ("freeCashFlow",                 "fcf"),
    ("commonDividendsPaid",          "dividend_payout"),
    ("depreciationAndAmortization",  "dna"),
]


class Command(BaseCommand):
    help = "Seeds reference/lookup tables only (Params, ParamsApi, Datasource, etc.) — no fake data"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding lookup tables...")
        self._seed_lookups()

        self.stdout.write("Seeding parameters...")
        params = self._seed_params()

        self.stdout.write("Seeding FMP API parameter mappings...")
        self._seed_fmp_params_api(params)

        self.stdout.write("Seeding Yahoo Finance API parameter mappings...")
        self._seed_yf_params_api(params)

        self.stdout.write(self.style.SUCCESS("Done. Reference data is ready."))

    def _seed_lookups(self):
        for v in ["NASDAQ", "NYSE", "LSE", "EURONEXT"]:
            Exchanges.objects.get_or_create(value=v)

        for v in ["Equity", "ETF", "Fund", "Bond"]:
            CompanyType.objects.get_or_create(value=v)

        for v in ["United States", "United Kingdom", "Germany", "France", "Japan"]:
            Countries.objects.get_or_create(value=v)

        for sym, rate in [("$", 1.0), ("£", 0.79), ("€", 0.86), ("¥", 0.0067)]:
            Currencies.objects.get_or_create(symbol=sym, defaults={"value": rate})

        for v in ["Income Statement", "Balance Sheet", "Cash Flow", "Calculated"]:
            ReportType.objects.get_or_create(value=v)

        for v in ["No", "Yes", "Bought", "Sold", "Watching"]:
            DecisionType.objects.get_or_create(value=v)

        for v in ["Manual", "Alpha Vantage", "Yahoo Finance", "FMP"]:
            CompSource.objects.get_or_create(value=v)

        for v in ["Alpha Vantage", "Yahoo Finance", "FMP"]:
            Datasource.objects.get_or_create(source_name=v)

    def _seed_params(self):
        params = {}
        report_type_map = {v: ReportType.objects.get(value=v)
                           for v in ["Income Statement", "Balance Sheet", "Cash Flow", "Calculated"]}
        for name, col, rt, ll, lv, dt, desc in PARAMS_DATA:
            obj, _ = Params.objects.get_or_create(
                param_name=name,
                defaults={
                    "report_type": report_type_map[rt],
                    "param_name_col": col,
                    "limit_logic": ll,
                    "limit_value": lv,
                    "data_type": dt,
                    "param_description": desc,
                },
            )
            params[col] = obj
        return params

    def _seed_fmp_params_api(self, params):
        fmp_source = Datasource.objects.get(source_name="FMP")
        for fmp_field, param_col in FMP_PARAMS_API_MAPPINGS:
            param_obj = params.get(param_col)
            if param_obj is None:
                self.stdout.write(self.style.WARNING(f"  Skipping {fmp_field} — param '{param_col}' not found"))
                continue
            ParamsApi.objects.get_or_create(
                param_name_api=fmp_field,
                datasource=fmp_source,
                defaults={"param": param_obj},
            )

    def _seed_yf_params_api(self, params):
        yf_source = Datasource.objects.get(source_name="Yahoo Finance")
        for yf_field, param_col in YF_PARAMS_API_MAPPINGS:
            param_obj = params.get(param_col)
            if param_obj is None:
                self.stdout.write(self.style.WARNING(f"  Skipping {yf_field} — param '{param_col}' not found"))
                continue
            ParamsApi.objects.get_or_create(
                param_name_api=yf_field,
                datasource=yf_source,
                defaults={"param": param_obj},
            )
