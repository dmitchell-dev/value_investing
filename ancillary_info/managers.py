from django.db.models import QuerySet


class CompaniesQueryset(QuerySet):

    def get_companies_joined(self):
        return (
            self.values(
                'id',
                'tidm',
                'company_name',
                'company_summary',
                'industry__industry_name',
                'comp_type__company_type',
                'market__share_listing',
                )
            )


class ParametersQueryset(QuerySet):

    def get_parameters_joined(self):
        return (
            self.values(
                'id',
                'param_name',
                'limit_logic',
                'limit_value',
                'param_description',
                'report_section__report_section',
                'report_section__report_section_last',
                'report_section__report_type__report_name',
                )
            )


class CalcVariablesQueryset(QuerySet):

    def get_calc_vars_joined(self):
        return (
            self.values(
                'parameter__param_name',
                'value',
                )
            )
