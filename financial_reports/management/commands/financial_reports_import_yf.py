import yfinance as yf
from django.core.management.base import BaseCommand, CommandError
from ancillary_info.models import (
    Companies, CompanyType, CompSource, Countries, Currencies,
    Exchanges, Industries, Params, ParamsApi, Sectors,
)
from financial_reports.models import FinancialReports
from django.db import transaction

import pandas as pd
import numpy as np


# yfinance returns per-share values — do NOT divide by 1B
PER_SHARE_FIELDS = {"Diluted EPS"}

# yfinance country name → Countries table value
COUNTRY_MAP = {
    "United States": "United States",
    "USA": "United States",
    "United Kingdom": "United Kingdom",
    "Germany": "Germany",
    "France": "France",
    "Japan": "Japan",
    "Canada": "Canada",
    "Australia": "Australia",
}

# yfinance currency code → Currencies symbol
CURRENCY_MAP = {
    "USD": "$",
    "GBP": "£",
    "EUR": "€",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "A$",
}


class Command(BaseCommand):
    help = "Imports Financial Data From yfinance (US and international)"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        df_params_api = pd.DataFrame(list(ParamsApi.objects.get_params_api_joined()))

        if df_params_api.empty or "datasource__source_name" not in df_params_api.columns:
            raise CommandError("No ParamsApi mappings found. Run: python manage.py seed_reference_data")

        df_params_api = df_params_api[
            df_params_api["datasource__source_name"] == "Yahoo Finance"
        ]

        if df_params_api.empty:
            raise CommandError("No Yahoo Finance ParamsApi mappings found. Run: python manage.py seed_reference_data")

        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))
        existing_tidms = df_companies["tidm"].values if not df_companies.empty else []

        if options["symbol"] is None:
            if df_companies.empty:
                raise CommandError("No companies found in the database.")
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]
            missing = [s for s in comp_list if s not in existing_tidms]
            if missing:
                for symbol in missing:
                    company = self._auto_create_company(symbol)
                    if company:
                        self.stdout.write(f"  Created company: {company.company_name} ({symbol})")
                        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))
                    else:
                        raise CommandError(
                            f"Could not fetch profile for {symbol} from yfinance. "
                            "Check the symbol is valid."
                        )

        num_comps = len(comp_list)
        comp_num = 0
        total_rows_created = 0
        total_rows_updated = 0

        statements = [
            ("income_stmt",    "income statement"),
            ("balance_sheet",  "balance sheet"),
            ("cashflow",       "cash flow"),
        ]

        for company_tidm in comp_list:
            comp_num += 1
            print(f"yfinance Import {comp_num} of {num_comps}: {company_tidm}")

            comp_idx = df_companies[df_companies["tidm"] == company_tidm].index[0]
            curr_comp_id = df_companies["id"].iat[comp_idx]

            ticker = yf.Ticker(company_tidm)

            for attr, label in statements:
                df_raw = getattr(ticker, attr)

                if df_raw is None or df_raw.empty:
                    print(f"  No {label} data for {company_tidm}")
                    continue

                # yfinance 1.x: index=dates, columns=fields → transpose to fields as index
                # yfinance 0.x: index=fields, columns=dates → use as-is
                if pd.api.types.is_datetime64_any_dtype(df_raw.index):
                    df_raw = df_raw.T

                # Reshape to long format manually to avoid pandas/yfinance melt incompatibilities
                records = []
                for date_col in df_raw.columns:
                    for field_name in df_raw.index:
                        records.append({
                            "variable": str(field_name),
                            "time_stamp": date_col,
                            "value": df_raw.at[field_name, date_col],
                        })
                df_data = pd.DataFrame(records)

                df_data.insert(0, "company_id", curr_comp_id)

                # Generate parameter IDs
                df_data = self._generate_param_id(df_params_api, df_data)

                if df_data.empty:
                    continue

                # Scale monetary values (actual → billions), keep per-share fields
                df_data = self._scale_values(df_data, df_params_api)

                # Format timestamps
                df_data["time_stamp"] = pd.to_datetime(df_data["time_stamp"]).dt.date

                # Replace NaN with None
                df_data = df_data.where(pd.notnull(df_data), None)

                # Update/Create split
                df_new, df_new_existing, df_old_existing = self._create_update_split(
                    df_data, company_tidm
                )

                if not df_new_existing.empty:
                    num_rows_updated = self._update_rows(df_new_existing, df_old_existing)
                    total_rows_updated += num_rows_updated

                if not df_new.empty:
                    num_rows_created = self._create_rows(df_new)
                    total_rows_created += num_rows_created

        return f"Created: {str(total_rows_created)}, Updated: {str(total_rows_updated)}"

    @staticmethod
    def _generate_param_id(df_params_api, df_data):
        param_name_list = df_params_api["param_name_api"].tolist()
        param_id_list = df_params_api["param__id"].tolist()

        df_data = df_data[df_data["variable"].isin(param_name_list)].copy()
        df_data["parameter_id"] = df_data["variable"].replace(param_name_list, param_id_list)
        df_data.drop(["variable"], axis=1, inplace=True)

        return df_data

    @staticmethod
    def _scale_values(df_data, df_params_api):
        """Divide monetary values by 1B; leave per-share fields unchanged."""
        per_share_param_ids = df_params_api[
            df_params_api["param_name_api"].isin(PER_SHARE_FIELDS)
        ]["param__id"].tolist()

        df_data["value"] = pd.to_numeric(df_data["value"], errors="coerce")

        mask = ~df_data["parameter_id"].isin(per_share_param_ids)
        df_data.loc[mask, "value"] = df_data.loc[mask, "value"] / 1_000_000_000

        return df_data

    def _create_update_split(self, new_df, company_tidm):
        existing_old_df = pd.DataFrame(
            list(FinancialReports.objects.get_financial_data_filtered(company_tidm))
        )

        if not new_df.empty:
            new_df["time_stamp_txt"] = new_df["time_stamp"].astype(str)

        if not existing_old_df.empty:
            existing_old_df["time_stamp_txt"] = existing_old_df["time_stamp"].astype(str)

            new_midx = pd.MultiIndex.from_arrays(
                [new_df[col] for col in ["time_stamp_txt", "parameter_id"]]
            )
            existing_midx = pd.MultiIndex.from_arrays(
                [existing_old_df[col] for col in ["time_stamp_txt", "parameter"]]
            )

            split_idx = np.where(new_midx.isin(existing_midx), "existing", "new")

            df_new_existing = new_df[split_idx == "existing"]
            df_old_existing = existing_old_df
            df_new = new_df[split_idx == "new"]
        else:
            df_new = new_df
            df_new_existing = pd.DataFrame()
            df_old_existing = pd.DataFrame()

        return df_new, df_new_existing, df_old_existing

    def _create_rows(self, df_create):
        reports = [
            FinancialReports(
                company=Companies.objects.get(id=row["company_id"]),
                parameter=Params.objects.get(id=row["parameter_id"]),
                time_stamp=row["time_stamp"],
                value=row["value"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = FinancialReports.objects.bulk_create(reports)
        return len(list_of_objects)

    def _update_rows(self, df_new_existing, df_old_existing):
        num_rows_updated = 0

        df_new_existing["value"] = df_new_existing["value"].astype("float").map("{:.4f}".format)
        df_old_existing["value"] = df_old_existing["value"].astype("float").map("{:.4f}".format)

        new_midx_value = pd.MultiIndex.from_arrays(
            [df_new_existing[col] for col in ["time_stamp_txt", "parameter_id", "value"]]
        )
        new_midx = pd.MultiIndex.from_arrays(
            [df_new_existing[col] for col in ["time_stamp_txt", "parameter_id"]]
        )
        df_new_existing["mul_col_idx"] = new_midx

        existing_midx_value = pd.MultiIndex.from_arrays(
            [df_old_existing[col] for col in ["time_stamp_txt", "parameter", "value"]]
        )
        existing_midx = pd.MultiIndex.from_arrays(
            [df_old_existing[col] for col in ["time_stamp_txt", "parameter"]]
        )
        df_old_existing["mul_col_idx"] = existing_midx

        split_idx = np.where(new_midx_value.isin(existing_midx_value), "existing", "new")
        df_to_update = df_new_existing[split_idx == "new"]

        if not df_to_update.empty:
            df_to_update = df_to_update.reset_index()
            df_to_update["id"] = np.nan

            for index, row in df_to_update.iterrows():
                df_to_update.at[index, "id"] = df_old_existing[
                    df_old_existing["mul_col_idx"].isin([row["mul_col_idx"]])
                ]["id"].values[0]
            df_to_update = df_to_update.set_index("id")

            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    FinancialReports.objects.filter(id=index).update(value=row["value"])
                    num_rows_updated += 1

        return num_rows_updated

    def _auto_create_company(self, symbol):
        info = yf.Ticker(symbol).info
        if not info or info.get("trailingPps") is None and info.get("longName") is None:
            return None

        country_raw = info.get("country", "United States")
        country_name = COUNTRY_MAP.get(country_raw, country_raw)
        currency_code = info.get("currency", "USD")
        currency_symbol = CURRENCY_MAP.get(currency_code, currency_code)

        exchange_raw = info.get("exchange", "NASDAQ")
        # yfinance exchange codes: NMS→NASDAQ, NYQ→NYSE, LSE→LSE
        exchange_map = {"NMS": "NASDAQ", "NYQ": "NYSE", "NGM": "NASDAQ", "PCX": "NYSE"}
        exchange_name = exchange_map.get(exchange_raw, exchange_raw)

        exchange, _ = Exchanges.objects.get_or_create(value=exchange_name)
        country, _ = Countries.objects.get_or_create(value=country_name)
        currency, _ = Currencies.objects.get_or_create(symbol=currency_symbol, defaults={"value": 1.0})
        industry, _ = Industries.objects.get_or_create(value=info.get("industry", "Unknown"))
        sector, _ = Sectors.objects.get_or_create(value=info.get("sector", "Unknown"))
        comp_type, _ = CompanyType.objects.get_or_create(value="Equity")
        comp_source, _ = CompSource.objects.get_or_create(value="Yahoo Finance")

        company, _ = Companies.objects.get_or_create(
            tidm=symbol,
            defaults={
                "company_name": info.get("longName", symbol),
                "company_summary": info.get("longBusinessSummary", ""),
                "exchange": exchange,
                "country": country,
                "currency": currency,
                "industry": industry,
                "sector": sector,
                "comp_type": comp_type,
                "company_source": comp_source,
            },
        )
        return company
