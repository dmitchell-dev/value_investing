import pandas as pd
import numpy as np

from django.core.management.base import BaseCommand
from ancillary_info.models import (
    Params,
    Companies,
    DcfVariables,
)
from share_prices.models import SharePrices
from financial_reports.models import FinancialReports
from calculated_stats.models import CalculatedStats

from django.db import transaction

from calculated_stats.managers import (
    total_equity,
    share_price,
    market_cap,
    enterprise_value,
    free_cash_flow,
    capital_employed,
    dividends_per_share,
    debt_to_eq_ratio,
    current_ratio,
    return_on_equity,
    equity_per_share,
    price_per_earnings,
    price_book_value,
    earnings_yield,
    annual_yield,
    div_cover,
    dcf_intrinsic_value,
    roce,
    roic,
    owner_earnings,
    net_margin,
    gross_margin,
    operating_margin,
    interest_coverage,
    dividend_payout_ratio,
    margin_of_safety,
    latest_margin_of_safety,
)


class Command(BaseCommand):
    help = "Calculates Stats from Financial Reports"

    def add_arguments(self, parser):
        parser.add_argument("--symbol", nargs="+", type=str)

    def handle(self, *args, **options):
        # Get ancillary data
        df_params = pd.DataFrame(list(Params.objects.get_params_joined()))
        df_companies = pd.DataFrame(list(Companies.objects.get_companies_joined()))

        # Specific symbols or all
        if options["symbol"] is None:
            comp_list = df_companies["tidm"].to_list()
        else:
            comp_list = options["symbol"]

        # Calculate values for each company
        # Get list of companies
        num_companies = len(comp_list)
        company_num = 0
        total_rows_created = 0
        total_rows_updated = 0

        for company_tidm in comp_list:
            company_num = company_num + 1
            print(f"Company {company_num} of {num_companies}, {company_tidm}")

            # Get DCF Variables
            df_dcf_variables = pd.DataFrame(
                list(DcfVariables.objects.get_table_joined_filtered(company_tidm))
            )

            # Get Share Price
            df_share_price = pd.DataFrame(
                list(SharePrices.objects.get_share_joined_filtered(company_tidm))
            )

            # Get Financial Data
            df = pd.DataFrame(
                list(
                    FinancialReports.objects.get_financial_data_joined_filtered(
                        company_tidm
                    )
                )
            )

            df_pivot = df.pivot(
                columns="time_stamp",
                index="parameter__param_name",
                values="value",
            )
            df_pivot = df_pivot.astype(float)

            # Calculations
            calc_list = []

            df_t_e = total_equity(df_pivot)
            if not df_t_e.empty:
                calc_list.append(df_t_e)

            if not df_share_price.empty and "time_stamp" in df_share_price.columns:
                df_share_price_reduced = share_price(df_pivot, df_share_price)
            else:
                df_share_price_reduced = pd.DataFrame()

            if not df_share_price_reduced.empty:
                calc_list.append(df_share_price_reduced)

            df_m_c = market_cap(df_pivot, df_share_price_reduced)
            if not df_m_c.empty:
                calc_list.append(df_m_c)

            df_e_v = enterprise_value(df_pivot, df_m_c)
            if not df_e_v.empty:
                calc_list.append(df_e_v)

            df_fcf = free_cash_flow(df_pivot)
            if not df_fcf.empty:
                calc_list.append(df_fcf)

            df_c_e = capital_employed(df_pivot)
            if not df_c_e.empty:
                calc_list.append(df_c_e)

            df_dps = dividends_per_share(df_pivot)
            if not df_dps.empty:
                calc_list.append(df_dps)

            df_d_e = debt_to_eq_ratio(df_pivot, df_t_e)
            if not df_d_e.empty:
                calc_list.append(df_d_e)

            df_cr = current_ratio(df_pivot)
            if not df_cr.empty:
                calc_list.append(df_cr)

            df_roe = return_on_equity(df_pivot, df_t_e)
            if not df_roe.empty:
                calc_list.append(df_roe)

            df_eps = equity_per_share(df_pivot, df_t_e)
            if not df_eps.empty:
                calc_list.append(df_eps)

            df_ppe = price_per_earnings(df_pivot, df_m_c)
            if not df_ppe.empty:
                calc_list.append(df_ppe)

            df_pbv = price_book_value(df_pivot, df_m_c, df_eps)
            if not df_pbv.empty:
                calc_list.append(df_pbv)

            df_e_yield = earnings_yield(df_pivot, df_e_v)
            if not df_e_yield.empty:
                calc_list.append(df_e_yield)

            df_a_yield = annual_yield(df_pivot, df_m_c)
            if not df_a_yield.empty:
                calc_list.append(df_a_yield)

            df_div_cover = div_cover(df_pivot)
            if not df_div_cover.empty:
                calc_list.append(df_div_cover)

            df_dcf_intrinsic_value = dcf_intrinsic_value(
                df_pivot, df_dcf_variables, df_fcf
            )
            if not df_dcf_intrinsic_value.empty:
                calc_list.append(df_dcf_intrinsic_value)

            df_roce = roce(df_pivot, df_c_e)
            if not df_roce.empty:
                calc_list.append(df_roce)

            df_roic = roic(df_pivot, df_t_e)
            if not df_roic.empty:
                calc_list.append(df_roic)

            df_owner_earnings = owner_earnings(df_pivot)
            if not df_owner_earnings.empty:
                calc_list.append(df_owner_earnings)

            df_net_margin = net_margin(df_pivot)
            if not df_net_margin.empty:
                calc_list.append(df_net_margin)

            df_gross_margin = gross_margin(df_pivot)
            if not df_gross_margin.empty:
                calc_list.append(df_gross_margin)

            df_operating_margin = operating_margin(df_pivot)
            if not df_operating_margin.empty:
                calc_list.append(df_operating_margin)

            df_interest_coverage = interest_coverage(df_pivot)
            if not df_interest_coverage.empty:
                calc_list.append(df_interest_coverage)

            df_dividend_payout_ratio = dividend_payout_ratio(df_pivot)
            if not df_dividend_payout_ratio.empty:
                calc_list.append(df_dividend_payout_ratio)

            if not df_dcf_intrinsic_value.empty:
                df_margin_of_safety = margin_of_safety(
                    df_share_price_reduced, df_dcf_intrinsic_value
                )
                if not df_margin_of_safety.empty:
                    calc_list.append(df_margin_of_safety)

                df_latest_margin_of_safety = latest_margin_of_safety(
                    df_dcf_intrinsic_value,
                    df_share_price_reduced,
                    df_share_price,
                )
                if not df_latest_margin_of_safety.empty:
                    calc_list.append(df_latest_margin_of_safety)

            if not calc_list:
                print(f"  No calculated stats for {company_tidm}, skipping.")
                continue

            # Merge all dataframes
            df_calculated = pd.concat(calc_list)

            df_calculated = df_calculated.round(decimals=2)

            # Generate parameter_id and replace index

            df_unpivot = self._replace_with_id(
                df_calculated, company_tidm, df_params, df_companies
            )

            # Check datetime format
            df_unpivot = self._datetime_format(df_unpivot)

            # Replace infinity values
            df_unpivot["value"] = df_unpivot["value"].astype(str)
            df_unpivot["value"] = df_unpivot["value"].replace(["inf", "-inf"], None)

            # Update/Create split
            df_new, df_new_existing, df_old_existing = self._create_update_split(
                df_unpivot, company_tidm
            )

            # Update existing rows
            if not df_new_existing.empty:
                num_rows_updated = self._update_rows(df_new_existing, df_old_existing)
                total_rows_updated = total_rows_updated + num_rows_updated

            # Create any new rows
            if not df_new.empty:
                num_rows_created = self._create_rows(df_new)
                total_rows_created = total_rows_created + num_rows_created

        return f"Created: {str(total_rows_created)}, Updated: {str(total_rows_updated)}"

    def _replace_with_id(self, df_calculated, company_tidm, df_params, df_companies):
        param_id_list = []
        param_list = df_calculated.index
        for param in param_list:

            param_id = df_params[df_params.param_name == param].id.values[0]
            param_id_list.append(param_id)

        df_calculated.index = param_id_list

        # company id
        company_id = df_companies[df_companies["tidm"] == company_tidm].id.values[0]

        df_unpivot = pd.melt(
            df_calculated, var_name="time_stamp", value_name="value", ignore_index=False
        )

        df_unpivot["company_id"] = company_id
        df_unpivot["parameter_id"] = df_unpivot.index

        return df_unpivot

    def _datetime_format(self, df):
        date_fmts = ("%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y")
        for fmt in date_fmts:
            try:
                df["time_stamp"] = pd.to_datetime(df["time_stamp"], format=fmt)
                break
            except ValueError:
                pass

        return df

    def _create_update_split(self, new_df, company_tidm):

        existing_old_df = pd.DataFrame(
            list(CalculatedStats.objects.get_table_filtered(company_tidm))
        )

        if not new_df.empty:
            new_df["time_stamp_txt"] = new_df["time_stamp"].astype(str)

        if not existing_old_df.empty:
            existing_old_df["time_stamp_txt"] = existing_old_df["time_stamp"].astype(
                str
            )

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

        # Save to database
        reports = [
            CalculatedStats(
                company=Companies.objects.get(id=row["company_id"]),
                parameter=Params.objects.get(id=row["parameter_id"]),
                time_stamp=row["time_stamp"],
                value=row["value"],
            )
            for i, row in df_create.iterrows()
        ]
        list_of_objects = CalculatedStats.objects.bulk_create(reports)

        total_rows_added = len(list_of_objects)

        return total_rows_added

    def _update_rows(self, df_new_existing, df_old_existing):
        """Checks if the values in the new df are different from the old df,
        if yes, updates the database"""

        num_rows_updated = 0

        # Format value columns correctly
        df_new_existing["value"] = df_new_existing["value"].astype("float")
        df_old_existing["value"] = df_old_existing["value"].astype("float")
        df_new_existing["value"] = df_new_existing["value"].map("{:.2f}".format)
        df_old_existing["value"] = df_old_existing["value"].map("{:.2f}".format)

        # Create multi columnindexes for both with and without value
        new_midx_value = pd.MultiIndex.from_arrays(
            [
                df_new_existing[col]
                for col in ["time_stamp_txt", "parameter_id", "value"]
            ]
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

        split_idx = np.where(
            new_midx_value.isin(existing_midx_value), "existing", "new"
        )

        # Only values to update
        df_to_update = df_new_existing[split_idx == "new"]

        if not df_to_update.empty:
            df_to_update["id"] = np.nan

            df_to_update = df_to_update.reset_index()

            # Transfer row id across to new df
            for index, row in df_to_update.iterrows():
                df_to_update.at[index, "id"] = df_old_existing[
                    df_old_existing["mul_col_idx"].isin([row["mul_col_idx"]])
                ]["id"].values[0]
            df_to_update = df_to_update.set_index("id")

            # Update Database
            with transaction.atomic():
                for index, row in df_to_update.iterrows():
                    # print(index, row['value'])
                    CalculatedStats.objects.filter(id=index).update(value=row["value"])
                    num_rows_updated = num_rows_updated + 1

        return num_rows_updated
