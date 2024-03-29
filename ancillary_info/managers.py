from django.db.models import QuerySet


class CompaniesQueryset(QuerySet):
    def get_companies_joined(self):
        return self.values(
            "id",
            "tidm",
            "company_name",
            "company_summary",
            "industry__value",
            "comp_type__value",
            "exchange__value",
            "country__value",
            "company_source__value",
            "currency__symbol",
            "currency__value",
        )

    def get_companies_tidm(self):
        return self.values(
            "id",
            "tidm",
        )

    def get_companies_joined_filtered(self, tidm):
        return self.values(
            "id",
            "tidm",
            "company_name",
            "company_summary",
            "industry__value",
            "comp_type__value",
            "exchange__value",
            "country__value",
            "company_source__value",
            "currency__symbol",
            "currency__value",
        ).filter(tidm=tidm)


class ParamsQueryset(QuerySet):
    def get_params_joined(self):
        return self.values(
            "id",
            "param_name",
            "param_name_col",
            "limit_logic",
            "limit_value",
            "data_type",
            "param_description",
        )


class ParamsApiQueryset(QuerySet):
    def get_params_api_joined(self):
        return self.values(
            "id",
            "param_name_api",
            "datasource__source_name",
            "param__id",
            "param__param_name_col",
            "param__limit_logic",
            "param__limit_value",
            "param__data_type",
            "param__param_description",
        )


class CalcVariablesQueryset(QuerySet):
    def get_calc_vars_joined(self):
        return self.values(
            "parameter__param_name",
            "value",
        )


class DcfVariablesQueryset(QuerySet):
    def get_table_joined_filtered(self, tidm):
        return self.values(
            "est_growth_rate",
            "est_disc_rate",
            "est_ltg_rate",
            "company_id",
            "company__tidm",
        ).filter(company__tidm=tidm)

    def get_table_joined(self):
        return self.values(
            "est_growth_rate",
            "est_disc_rate",
            "est_ltg_rate",
            "company__tidm",
        )
