"""
Management command to populate the database with realistic dummy data.
Usage: python manage.py seed_data
       python manage.py seed_data --flush   (clears existing data first)
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from ancillary_info.models import (
    Companies, CompanyType, CompSource, Countries, Currencies,
    DcfVariables, Datasource, DecisionType, Exchanges, Industries,
    Params, ParamsApi, ReportType, Sectors,
)
from calculated_stats.models import CalculatedStats
from dashboard_company.models import DashboardCompany
from financial_reports.models import FinancialReports
from portfolio.models import Cash, Portfolio, Transactions, WishList
from share_prices.models import SharePrices


# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

COMPANIES_DATA = [
    {
        "tidm": "AAPL",
        "name": "Apple Inc.",
        "summary": (
            "Apple Inc. designs, manufactures, and markets smartphones, personal computers, "
            "tablets, wearables, and accessories worldwide. Its flagship products include "
            "iPhone, Mac, iPad, Apple Watch, and AirPods. Apple also offers a range of "
            "services including the App Store, Apple Music, iCloud, and Apple TV+."
        ),
        "exchange": "NASDAQ",
        "country": "United States",
        "currency": ("$", 1.0),
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "comp_type": "Equity",
        "comp_source": "Manual",
        # Financial profile (annual, in billions USD, most recent year first)
        "revenue":      [394.3, 383.3, 365.8, 274.5, 260.2, 265.6, 229.2],
        "net_income":   [97.0,  99.8,  94.7,  57.4,  55.3,  59.5,  48.4],
        "eps":          [6.11,  6.15,  5.67,  3.31,  3.00,  2.97,  2.33],
        "dividends":    [0.94,  0.91,  0.88,  0.82,  0.77,  0.73,  0.70],
        "fcf":          [90.2,  89.5,  92.9,  73.4,  66.2,  58.9,  52.3],
        "total_equity": [62.1,  50.7,  65.0,  66.2,  90.5, 107.1, 119.1],
        "total_assets": [352.6, 335.0, 346.1, 323.9, 338.5, 365.7, 375.3],
        "lt_debt":      [91.8,  98.1, 109.3, 119.7, 112.4,  93.7,  75.4],
        "capex":        [10.7,  10.7,  11.1,   8.3,   7.3,   9.1,  10.5],
        "op_cashflow":  [110.5, 122.2, 104.0,  80.7,  69.4,  77.4,  63.6],
        "share_price":  189.3,
        "dcf_iv":       215.0,
        "growth_rate":  0.08,
        "disc_rate":    0.10,
        "ltg_rate":     0.03,
    },
    {
        "tidm": "MSFT",
        "name": "Microsoft Corporation",
        "summary": (
            "Microsoft Corporation develops, licenses, and supports software, services, "
            "devices, and solutions worldwide. Its segments include Productivity and "
            "Business Processes, Intelligent Cloud, and More Personal Computing. "
            "Key products include Windows, Azure, Office 365, and Xbox."
        ),
        "exchange": "NASDAQ",
        "country": "United States",
        "currency": ("$", 1.0),
        "sector": "Technology",
        "industry": "Software—Infrastructure",
        "comp_type": "Equity",
        "comp_source": "Manual",
        "revenue":      [211.9, 198.3, 168.1, 143.0, 110.4, 125.8, 96.0],
        "net_income":   [72.4,  69.4,  61.3,  44.3,  16.6,  39.2, 22.1],
        "eps":          [9.72,  9.21,  8.05,  5.76,  2.13,  5.06,  2.71],
        "dividends":    [2.72,  2.48,  2.24,  2.04,  1.84,  1.68,  1.56],
        "fcf":          [59.5,  56.1,  48.3,  38.2,  32.3,  26.1,  24.3],
        "total_equity": [206.2, 166.5, 141.9, 118.3,  82.7, 102.3,  71.2],
        "total_assets": [411.9, 364.8, 333.8, 301.3, 258.8, 250.3, 193.7],
        "lt_debt":      [47.2,  41.6,  50.1,  59.6,  67.0,  72.2,  76.1],
        "capex":        [28.1,  23.9,  20.6,  15.4,  11.6,  11.5,   8.1],
        "op_cashflow":  [87.9,  89.0,  76.7,  60.7,  43.9,  52.2,  33.3],
        "share_price":  415.2,
        "dcf_iv":       480.0,
        "growth_rate":  0.12,
        "disc_rate":    0.09,
        "ltg_rate":     0.04,
    },
    {
        "tidm": "ULVR",
        "name": "Unilever PLC",
        "summary": (
            "Unilever PLC is a fast-moving consumer goods company that operates through "
            "Beauty & Wellbeing, Personal Care, Home Care, Nutrition, and Ice Cream segments. "
            "Its brands include Dove, Hellmann's, Knorr, Lipton, and Ben & Jerry's. "
            "The company operates in over 190 countries worldwide."
        ),
        "exchange": "LSE",
        "country": "United Kingdom",
        "currency": ("£", 0.79),
        "sector": "Consumer Staples",
        "industry": "Household & Personal Products",
        "comp_type": "Equity",
        "comp_source": "Manual",
        "revenue":      [59.6, 60.1, 52.4, 50.7, 51.0, 52.7, 53.7],
        "net_income":   [5.9,  6.3,  6.7,  5.6,  6.1,  6.5,  6.7],
        "eps":          [2.21, 2.35, 2.50, 2.07, 2.23, 2.35, 2.44],
        "dividends":    [1.71, 1.69, 1.65, 1.65, 1.65, 1.60, 1.55],
        "fcf":          [5.2,  5.8,  5.5,  4.9,  5.0,  5.3,  5.1],
        "total_equity": [11.5, 12.0, 12.7, 11.8, 12.2, 13.5, 14.1],
        "total_assets": [65.7, 65.1, 67.3, 63.9, 62.1, 64.5, 66.2],
        "lt_debt":      [23.1, 24.5, 25.3, 23.8, 22.5, 21.1, 20.0],
        "capex":        [1.3,  1.4,  1.5,  1.3,  1.2,  1.3,  1.4],
        "op_cashflow":  [6.8,  7.3,  7.1,  6.5,  6.3,  6.9,  6.7],
        "share_price":  38.75,
        "dcf_iv":       44.50,
        "growth_rate":  0.05,
        "disc_rate":    0.08,
        "ltg_rate":     0.025,
    },
    {
        "tidm": "BP.",
        "name": "BP PLC",
        "summary": (
            "BP PLC is an integrated oil and gas company. It operates through Gas & Low Carbon "
            "Energy, Oil Production & Operations, and Customers & Products segments. "
            "The company explores for and produces oil and natural gas, refines, supplies, "
            "and trades, and is transitioning towards renewable energy sources."
        ),
        "exchange": "LSE",
        "country": "United Kingdom",
        "currency": ("£", 0.79),
        "sector": "Energy",
        "industry": "Oil & Gas Integrated",
        "comp_type": "Equity",
        "comp_source": "Manual",
        "revenue":      [213.0, 248.0, 157.7, 183.0, 180.6, 222.9, 240.2],
        "net_income":   [10.8,  16.8,  -5.7,   4.0,  -6.5,  12.7,   9.1],
        "eps":          [0.52,  0.80, -0.27,  0.19, -0.31,  0.63,  0.44],
        "dividends":    [0.24,  0.22,  0.21,  0.21,  0.10,  0.21,  0.24],
        "fcf":          [6.9,  13.7,   2.6,   5.4,  -2.1,  13.9,   8.4],
        "total_equity": [88.5,  89.0,  91.3,  99.3, 102.1, 109.5, 111.2],
        "total_assets": [278.3, 288.2, 273.5, 282.2, 281.9, 296.0, 303.1],
        "lt_debt":      [44.0,  35.5,  38.9,  51.7,  66.7,  58.8,  52.1],
        "capex":        [15.2,  16.3,  12.1,  13.8,  11.2,  14.7,  16.1],
        "op_cashflow":  [22.1,  29.7,  14.3,  18.2,   7.8,  26.4,  20.9],
        "share_price":  4.52,
        "dcf_iv":       5.20,
        "growth_rate":  0.03,
        "disc_rate":    0.10,
        "ltg_rate":     0.02,
    },
    {
        "tidm": "HSBA",
        "name": "HSBC Holdings PLC",
        "summary": (
            "HSBC Holdings PLC provides banking and financial services worldwide. "
            "It operates through Wealth and Personal Banking, Commercial Banking, and "
            "Global Banking and Markets segments. The company serves individuals, "
            "businesses, institutions, and governments across over 60 countries."
        ),
        "exchange": "LSE",
        "country": "United Kingdom",
        "currency": ("£", 0.79),
        "sector": "Financial Services",
        "industry": "Banks—Diversified",
        "comp_type": "Equity",
        "comp_source": "Manual",
        "revenue":      [66.1, 55.6, 49.6, 50.4, 56.1, 53.8, 56.1],
        "net_income":   [14.8, 17.5, -1.0,  6.1, -0.8,  8.7,  5.0],
        "eps":          [0.75, 0.87, -0.05, 0.30, -0.04, 0.41, 0.23],
        "dividends":    [0.61, 0.30,  0.15,  0.30,  0.30, 0.51, 0.51],
        "fcf":          [8.3,  9.1,   2.1,   4.5,  -1.2,  7.3,  4.8],
        "total_equity": [198.1,189.3, 183.4, 191.5, 187.3, 186.5, 190.2],
        "total_assets": [3038, 2919,  2984,  2715,  2922,  2715,  2558],
        "lt_debt":      [188.2,191.3, 204.6, 189.2, 171.4, 149.2, 142.1],
        "capex":        [2.1,  2.3,   1.9,   2.2,   2.5,   2.8,   3.0],
        "op_cashflow":  [16.5, 19.2,   4.8,   9.1,   3.2,  12.1,   8.3],
        "share_price":  6.72,
        "dcf_iv":       7.50,
        "growth_rate":  0.04,
        "disc_rate":    0.09,
        "ltg_rate":     0.02,
    },
    {
        "tidm": "GSK",
        "name": "GSK PLC",
        "summary": (
            "GSK PLC is a science-led global healthcare company with a purpose to improve "
            "the quality of human life by enabling people to do more, feel better, and live "
            "longer. The company has three global businesses: Pharmaceuticals, Vaccines, "
            "and Consumer Healthcare."
        ),
        "exchange": "LSE",
        "country": "United Kingdom",
        "currency": ("£", 0.79),
        "sector": "Healthcare",
        "industry": "Drug Manufacturers—General",
        "comp_type": "Equity",
        "comp_source": "Manual",
        "revenue":      [30.3, 29.3, 34.1, 33.8, 33.1, 36.2, 32.7],
        "net_income":   [3.1,  4.2,  5.4,  6.2,  3.8,  2.8,  2.3],
        "eps":          [0.63, 0.85, 1.09, 1.25, 0.77, 0.55, 0.45],
        "dividends":    [0.57, 0.56, 0.80, 0.80, 0.80, 0.80, 0.80],
        "fcf":          [3.8,  4.9,  5.8,  5.1,  4.0,  3.1,  2.5],
        "total_equity": [7.0,  6.4,  8.2,  6.1,  5.9,  6.2,  7.0],
        "total_assets": [54.1, 53.0, 71.5, 70.8, 69.0, 45.3, 43.1],
        "lt_debt":      [18.6, 19.5, 27.3, 26.8, 24.1, 20.2, 18.5],
        "capex":        [1.5,  1.6,  1.8,  1.7,  1.9,  2.0,  2.1],
        "op_cashflow":  [5.9,  6.7,  7.8,  7.1,  5.8,  4.6,  3.9],
        "share_price":  14.82,
        "dcf_iv":       17.00,
        "growth_rate":  0.06,
        "disc_rate":    0.09,
        "ltg_rate":     0.025,
    },
]

PARAMS_DATA = [
    # (name, col_name, report_type, limit_logic, limit_value, data_type, description)
    ("Revenue",              "revenue",            "Income Statement", ">", "0",   "float", "Total revenue / turnover"),
    ("Net Income",           "net_income",         "Income Statement", ">", "0",   "float", "Net income after tax"),
    ("EPS",                  "eps",                "Income Statement", ">", "0",   "float", "Earnings per share (diluted)"),
    ("Dividends Per Share",  "dividends",          "Income Statement", ">", "0",   "float", "Dividends paid per share"),
    ("Capital Expenditure",  "capex",              "Cash Flow",        "<", "0",   "float", "Capital expenditure"),
    ("Operating Cash Flow",  "op_cashflow",        "Cash Flow",        ">", "0",   "float", "Net cash from operating activities"),
    ("Free Cash Flow",       "fcf",                "Cash Flow",        ">", "0",   "float", "Operating cash flow minus capex"),
    ("Total Assets",         "total_assets",       "Balance Sheet",    ">", "0",   "float", "Total assets"),
    ("Total Equity",         "total_equity",       "Balance Sheet",    ">", "0",   "float", "Total shareholders equity"),
    ("Long Term Debt",       "lt_debt",            "Balance Sheet",    "<", "inf", "float", "Long-term debt and borrowings"),
    ("Debt to Equity",       "debt_to_equity",     "Calculated",       "<", "1",   "float", "Total debt divided by equity"),
    ("Return on Equity",     "return_on_equity",   "Calculated",       ">", "0.1", "float", "Net income / total equity"),
    ("Price to Earnings",    "price_to_earnings",  "Calculated",       "<", "25",  "float", "Share price / EPS"),
    ("DCF Intrinsic Value",  "dcf_intrinsic_value","Calculated",       ">", "0",   "float", "Discounted cash flow intrinsic value"),
    ("Margin of Safety",     "margin_of_safety",   "Calculated",       ">", "0.2", "float", "Margin of safety vs current price"),
]


class Command(BaseCommand):
    help = "Seed the database with realistic dummy value investing data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing data...")
            self._flush()

        self.stdout.write("Seeding lookup tables...")
        lookups = self._seed_lookups()

        self.stdout.write("Seeding parameters...")
        params = self._seed_params(lookups)

        self.stdout.write("Seeding companies...")
        companies = self._seed_companies(lookups)

        self.stdout.write("Seeding DCF variables...")
        self._seed_dcf_variables(companies)

        self.stdout.write("Seeding financial reports...")
        self._seed_financial_reports(companies, params)

        self.stdout.write("Seeding share prices...")
        self._seed_share_prices(companies)

        self.stdout.write("Seeding dashboard companies...")
        self._seed_dashboard_companies(companies, lookups)

        self.stdout.write("Seeding portfolio data...")
        self._seed_portfolio(companies, lookups)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Seeded {len(companies)} companies with full financial data."
        ))

    # ------------------------------------------------------------------
    def _flush(self):
        Portfolio.objects.all().delete()
        WishList.objects.all().delete()
        Cash.objects.all().delete()
        Transactions.objects.all().delete()
        DashboardCompany.objects.all().delete()
        SharePrices.objects.all().delete()
        CalculatedStats.objects.all().delete()
        FinancialReports.objects.all().delete()
        DcfVariables.objects.all().delete()
        Companies.objects.all().delete()
        ParamsApi.objects.all().delete()
        Params.objects.all().delete()
        Exchanges.objects.all().delete()
        CompanyType.objects.all().delete()
        Industries.objects.all().delete()
        Sectors.objects.all().delete()
        Currencies.objects.all().delete()
        Countries.objects.all().delete()
        ReportType.objects.all().delete()
        DecisionType.objects.all().delete()
        CompSource.objects.all().delete()
        Datasource.objects.all().delete()

    # ------------------------------------------------------------------
    def _seed_lookups(self):
        exchanges = {v: Exchanges.objects.get_or_create(value=v)[0]
                     for v in ["NASDAQ", "NYSE", "LSE", "EURONEXT"]}

        comp_types = {v: CompanyType.objects.get_or_create(value=v)[0]
                      for v in ["Equity", "ETF", "Fund", "Index"]}

        industries = {v: Industries.objects.get_or_create(value=v)[0]
                      for v in [
                          "Consumer Electronics", "Software—Infrastructure",
                          "Household & Personal Products", "Oil & Gas Integrated",
                          "Banks—Diversified", "Drug Manufacturers—General",
                      ]}

        sectors = {v: Sectors.objects.get_or_create(value=v)[0]
                   for v in ["Technology", "Consumer Staples", "Energy",
                              "Financial Services", "Healthcare", "Industrials"]}

        currencies = {}
        for sym, val in [("$", 1.0), ("£", 0.79), ("€", 0.87)]:
            obj, _ = Currencies.objects.get_or_create(symbol=sym, defaults={"value": val})
            currencies[sym] = obj

        countries = {v: Countries.objects.get_or_create(value=v)[0]
                     for v in ["United States", "United Kingdom", "Germany", "France"]}

        report_types = {v: ReportType.objects.get_or_create(value=v)[0]
                        for v in ["Income Statement", "Balance Sheet", "Cash Flow",
                                  "Calculated", "Share Price"]}

        decision_types = {v: DecisionType.objects.get_or_create(value=v)[0]
                          for v in ["Bought", "Sold", "Deposit", "Withdrawal",
                                    "Dividend", "Fee"]}

        comp_sources = {v: CompSource.objects.get_or_create(value=v)[0]
                        for v in ["Manual", "Alpha Vantage", "Yahoo Finance"]}

        datasources = {v: Datasource.objects.get_or_create(source_name=v)[0]
                       for v in ["Alpha Vantage", "Yahoo Finance"]}

        return {
            "exchanges": exchanges,
            "comp_types": comp_types,
            "industries": industries,
            "sectors": sectors,
            "currencies": currencies,
            "countries": countries,
            "report_types": report_types,
            "decision_types": decision_types,
            "comp_sources": comp_sources,
            "datasources": datasources,
        }

    # ------------------------------------------------------------------
    def _seed_params(self, lookups):
        params = {}
        for name, col, rt, ll, lv, dt, desc in PARAMS_DATA:
            obj, _ = Params.objects.get_or_create(
                param_name=name,
                defaults={
                    "report_type": lookups["report_types"][rt],
                    "param_name_col": col,
                    "limit_logic": ll,
                    "limit_value": lv,
                    "data_type": dt,
                    "param_description": desc,
                },
            )
            params[col] = obj
        return params

    # ------------------------------------------------------------------
    def _seed_companies(self, lookups):
        companies = {}
        for d in COMPANIES_DATA:
            sym, val = d["currency"]
            obj, _ = Companies.objects.get_or_create(
                tidm=d["tidm"],
                defaults={
                    "company_name": d["name"],
                    "company_summary": d["summary"],
                    "exchange": lookups["exchanges"][d["exchange"]],
                    "country": lookups["countries"][d["country"]],
                    "currency": lookups["currencies"][sym],
                    "sector": lookups["sectors"][d["sector"]],
                    "industry": lookups["industries"][d["industry"]],
                    "comp_type": lookups["comp_types"][d["comp_type"]],
                    "company_source": lookups["comp_sources"][d["comp_source"]],
                },
            )
            companies[d["tidm"]] = (obj, d)
        return companies

    # ------------------------------------------------------------------
    def _seed_dcf_variables(self, companies):
        for tidm, (company, d) in companies.items():
            DcfVariables.objects.get_or_create(
                company=company,
                defaults={
                    "est_growth_rate": d["growth_rate"],
                    "est_disc_rate": d["disc_rate"],
                    "est_ltg_rate": d["ltg_rate"],
                },
            )

    # ------------------------------------------------------------------
    def _seed_financial_reports(self, companies, params):
        # Annual dates going back 7 years from most recent fiscal year end
        base_year = 2024
        dates = [date(base_year - i, 12, 31) for i in range(7)]

        param_map = {
            "revenue":       "revenue",
            "net_income":    "net_income",
            "eps":           "eps",
            "dividends":     "dividends",
            "fcf":           "fcf",
            "total_equity":  "total_equity",
            "total_assets":  "total_assets",
            "lt_debt":       "lt_debt",
            "capex":         "capex",
            "op_cashflow":   "op_cashflow",
        }

        reports = []
        for tidm, (company, d) in companies.items():
            for field, param_col in param_map.items():
                if param_col not in params:
                    continue
                param = params[param_col]
                values = d[field]
                for i, dt in enumerate(dates):
                    if i < len(values):
                        reports.append(FinancialReports(
                            company=company,
                            parameter=param,
                            time_stamp=dt,
                            value=values[i],
                        ))

        FinancialReports.objects.bulk_create(reports, ignore_conflicts=True)

        # Calculated stats (string values)
        calc_reports = []
        calc_params = {
            "debt_to_equity":    "debt_to_equity",
            "return_on_equity":  "return_on_equity",
            "price_to_earnings": "price_to_earnings",
        }
        for tidm, (company, d) in companies.items():
            for i, dt in enumerate(dates):
                if i < len(d["net_income"]):
                    dte = d["total_equity"][i] if d["total_equity"][i] != 0 else 1
                    roe = round(d["net_income"][i] / dte, 3)
                    ltd = d["lt_debt"][i]
                    dte_ratio = round(ltd / dte, 2)
                    eps_val = d["eps"][i] if d["eps"][i] != 0 else 1
                    pe = round(d["share_price"] / eps_val, 1) if i == 0 else round(
                        d["share_price"] * (0.9 ** i) / eps_val, 1
                    )

                    for col, val in [
                        ("debt_to_equity", str(dte_ratio)),
                        ("return_on_equity", str(roe)),
                        ("price_to_earnings", str(pe)),
                    ]:
                        if col in params:
                            calc_reports.append(CalculatedStats(
                                company=company,
                                parameter=params[col],
                                time_stamp=dt,
                                value=val,
                            ))

        CalculatedStats.objects.bulk_create(calc_reports, ignore_conflicts=True)

    # ------------------------------------------------------------------
    def _seed_share_prices(self, companies):
        prices = []
        end_date = date(2024, 12, 31)
        start_date = date(2019, 1, 1)

        for tidm, (company, d) in companies.items():
            base_price = d["share_price"]
            current = base_price
            dt = start_date
            # Walk backwards from base price with random walk
            price_series = [base_price]
            for _ in range((end_date - start_date).days):
                change = current * random.gauss(0.0003, 0.012)
                current = max(current + change, base_price * 0.3)
                price_series.append(round(current, 4))
            price_series.reverse()

            dt = start_date
            for p in price_series:
                # Skip weekends
                if dt.weekday() < 5:
                    prices.append(SharePrices(
                        company=company,
                        time_stamp=dt,
                        value=round(p, 4),
                        value_adjusted=round(p * 0.998, 4),
                        volume=random.randint(1_000_000, 50_000_000),
                    ))
                dt += timedelta(days=1)
                if dt > end_date:
                    break

        SharePrices.objects.bulk_create(prices, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(f"  Created {len(prices)} share price records")

    # ------------------------------------------------------------------
    def _seed_dashboard_companies(self, companies, lookups):
        decision = lookups["decision_types"]["Bought"]
        today = date(2024, 12, 31)

        for tidm, (company, d) in companies.items():
            ne = d["net_income"][0]
            te = d["total_equity"][0] if d["total_equity"][0] != 0 else 1
            eps = d["eps"][0] if d["eps"][0] != 0 else 1
            price = d["share_price"]
            iv = d["dcf_iv"]
            mos = round((iv - price) / iv, 3) if iv > 0 else 0
            sym = d["currency"][0]

            DashboardCompany.objects.update_or_create(
                company=company,
                defaults={
                    "decision_type": decision,
                    "tidm": tidm,
                    "company_name": d["name"],
                    "company_summary": d["summary"],
                    "share_listing": d["exchange"],
                    "company_type": d["comp_type"],
                    "industry_name": d["industry"],
                    "revenue": d["revenue"][0],
                    "earnings": ne,
                    "dividends": d["dividends"][0],
                    "capital_expenditure": d["capex"][0],
                    "net_income": ne,
                    "total_equity": te,
                    "share_price": price,
                    "debt_to_equity": round(d["lt_debt"][0] / te, 2),
                    "current_ratio": round(random.uniform(1.2, 2.5), 2),
                    "return_on_equity": round(ne / te, 3),
                    "equity_per_share": round(te / random.uniform(15e9, 20e9), 2),
                    "price_to_earnings": round(price / eps, 1),
                    "price_to_equity": round(price / (te / random.uniform(15e9, 20e9)), 1),
                    "earnings_yield": round(eps / price, 4),
                    "annual_yield_return": round(d["dividends"][0] / price, 4),
                    "fcf": d["fcf"][0],
                    "dividend_cover": round(eps / d["dividends"][0], 2) if d["dividends"][0] else 0,
                    "capital_employed": round(te + d["lt_debt"][0], 1),
                    "roce": round(ne / (te + d["lt_debt"][0]), 3),
                    "dcf_intrinsic_value": iv,
                    "margin_safety": mos,
                    "latest_margin_of_safety": mos,
                    "estimated_growth_rate": d["growth_rate"],
                    "estimated_discount_rate": d["disc_rate"],
                    "estimated_long_term_growth_rate": d["ltg_rate"],
                    "pick_source": "Manual",
                    "exchange_country": d["country"],
                    "currency_symbol": sym,
                    "latest_financial_date": today,
                    "latest_share_price_date": today,
                    "latest_share_price": price,
                    "market_cap": round(price * random.uniform(15e9, 20e9), 0),
                },
            )

    # ------------------------------------------------------------------
    def _seed_portfolio(self, companies, lookups):
        bought = lookups["decision_types"]["Bought"]
        sold = lookups["decision_types"]["Sold"]
        deposit = lookups["decision_types"]["Deposit"]
        withdrawal = lookups["decision_types"]["Withdrawal"]
        dividend = lookups["decision_types"]["Dividend"]
        fee = lookups["decision_types"]["Fee"]

        # --- Cash transactions (use bulk_create to bypass custom save) ---
        cash_records = [
            # Initial deposit
            Cash(decision=deposit, date_dealt=date(2021, 1, 5),
                 cash_value=20000.0, cash_balance=20000.0),
            Cash(decision=deposit, date_dealt=date(2021, 6, 1),
                 cash_value=10000.0, cash_balance=30000.0),
            Cash(decision=bought, company=list(companies.values())[0][0],
                 date_dealt=date(2021, 6, 15),
                 cash_value=5000.0, cash_balance=25000.0),
            Cash(decision=bought, company=list(companies.values())[1][0],
                 date_dealt=date(2021, 9, 10),
                 cash_value=4000.0, cash_balance=21000.0),
            Cash(decision=dividend, company=list(companies.values())[0][0],
                 date_dealt=date(2022, 3, 15),
                 cash_value=250.0, cash_balance=21250.0),
            Cash(decision=fee, date_dealt=date(2022, 3, 15),
                 cash_value=12.50, cash_balance=21237.50),
            Cash(decision=bought, company=list(companies.values())[2][0],
                 date_dealt=date(2022, 4, 1),
                 cash_value=3500.0, cash_balance=17737.50),
            Cash(decision=dividend, company=list(companies.values())[1][0],
                 date_dealt=date(2022, 9, 20),
                 cash_value=180.0, cash_balance=17917.50),
            Cash(decision=deposit, date_dealt=date(2023, 1, 10),
                 cash_value=5000.0, cash_balance=22917.50),
            Cash(decision=bought, company=list(companies.values())[3][0],
                 date_dealt=date(2023, 2, 14),
                 cash_value=2800.0, cash_balance=20117.50),
            Cash(decision=dividend, company=list(companies.values())[2][0],
                 date_dealt=date(2023, 6, 30),
                 cash_value=310.0, cash_balance=20427.50),
            Cash(decision=fee, date_dealt=date(2023, 6, 30),
                 cash_value=9.99, cash_balance=20417.51),
        ]
        Cash.objects.bulk_create(cash_records)

        # --- Transactions (use save() so balances auto-calculate) ---
        tidms = list(companies.keys())

        # AAPL: buy 25 shares
        co_aapl, d_aapl = companies[tidms[0]]
        t1 = Transactions(
            company=co_aapl, decision=bought,
            date_dealt=date(2021, 6, 15), date_settled=date(2021, 6, 17),
            reference="REF-001", num_stock=25, num_stock_balance=0,
            price=150.20, fees=10.0,
        )
        t1.save()

        # MSFT: buy 10 shares
        co_msft, d_msft = companies[tidms[1]]
        t2 = Transactions(
            company=co_msft, decision=bought,
            date_dealt=date(2021, 9, 10), date_settled=date(2021, 9, 13),
            reference="REF-002", num_stock=10, num_stock_balance=0,
            price=295.50, fees=10.0,
        )
        t2.save()

        # ULVR: buy 80 shares
        co_ulvr, d_ulvr = companies[tidms[2]]
        t3 = Transactions(
            company=co_ulvr, decision=bought,
            date_dealt=date(2022, 4, 1), date_settled=date(2022, 4, 5),
            reference="REF-003", num_stock=80, num_stock_balance=0,
            price=38.50, fees=10.0,
        )
        t3.save()

        # BP: buy 500 shares
        co_bp, d_bp = companies[tidms[3]]
        t4 = Transactions(
            company=co_bp, decision=bought,
            date_dealt=date(2023, 2, 14), date_settled=date(2023, 2, 16),
            reference="REF-004", num_stock=500, num_stock_balance=0,
            price=4.80, fees=10.0,
        )
        t4.save()

        # AAPL: buy 10 more shares
        t5 = Transactions(
            company=co_aapl, decision=bought,
            date_dealt=date(2023, 8, 20), date_settled=date(2023, 8, 22),
            reference="REF-005", num_stock=10, num_stock_balance=0,
            price=175.00, fees=10.0,
        )
        t5.save()

        # MSFT: sell 5 shares
        t6 = Transactions(
            company=co_msft, decision=sold,
            date_dealt=date(2024, 1, 15), date_settled=date(2024, 1, 17),
            reference="REF-006", num_stock=5, num_stock_balance=0,
            price=385.00, fees=10.0,
        )
        t6.save()

        # --- Wish List ---
        wish_data = [
            (companies[tidms[4]], 6.50,  6.72,  0.20, 0.19, 0.25, 7.50),
            (companies[tidms[5]], 13.90, 14.82, 0.22, 0.18, 0.25, 17.00),
        ]
        for (company, d), rsp, csp, rmos, cmos, bmos, iv in wish_data:
            WishList.objects.get_or_create(
                company=company,
                defaults={
                    "reporting_stock_price": rsp,
                    "current_stock_price": csp,
                    "reporting_mos": rmos,
                    "current_mos": cmos,
                    "buy_mos": bmos,
                    "dcf_intrinsic_value": iv,
                    "latest_financial_date": date(2024, 12, 31),
                    "latest_share_price_date": date(2024, 12, 31),
                },
            )

        # --- Portfolio summary ---
        portfolio_data = [
            # (company, d), price, num, initial_cost
            (companies[tidms[0]], 189.3, 35, 150.20 * 25 + 175.00 * 10),
            (companies[tidms[1]], 415.2,  5, 295.50 * 10),
            (companies[tidms[2]],  38.75, 80,  38.50 * 80),
            (companies[tidms[3]],   4.52, 500,   4.80 * 500),
        ]
        total_value = sum(p * n for _, p, n, _ in portfolio_data)

        for (company, d), price, num, initial_cost in portfolio_data:
            latest_holding = price * num
            fees_bought = 20.0
            fees_sold = 10.0 if company == companies[tidms[1]][0] else 0.0
            sold_income = 385.0 * 5 if company == companies[tidms[1]][0] else 0.0
            profit = latest_holding + sold_income - initial_cost - fees_bought - fees_sold

            Portfolio.objects.update_or_create(
                company=company,
                defaults={
                    "latest_share_price": price,
                    "latest_shares_num": num,
                    "latest_shares_holding": latest_holding,
                    "fees_bought": fees_bought,
                    "fees_sold": fees_sold,
                    "fees_total": fees_bought + fees_sold,
                    "initial_shares_holding": latest_holding,
                    "sold_shares_income": sold_income,
                    "income_from_selling": sold_income,
                    "total_profit": round(profit, 2),
                    "initial_shares_cost": round(initial_cost, 2),
                    "share_value_change": round(latest_holding - initial_cost, 2),
                    "share_pct_change": round((latest_holding - initial_cost) / initial_cost * 100, 2),
                    "company_pct_holding": round(latest_holding / total_value * 100, 2),
                },
            )
