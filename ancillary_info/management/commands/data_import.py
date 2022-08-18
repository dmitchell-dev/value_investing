from django.core.management.base import BaseCommand

from ancillary_info.models import Companies
from django.core import management


class Command(BaseCommand):
    help = "populates and updates all tables"

    def add_arguments(self, parser):
        parser.add_argument("--comp_pk", nargs="+", type=str)
        parser.add_argument(
            "--from_scratch",
            type=str,
            nargs="?",
            default=False,
            help="Include ancillary table imports",
        )

    def handle(self, *args, **options):

        return_results = []

        # Specific symbols or all
        if options["comp_pk"] is None:
            pk = None
            company_tidm = None
        else:
            pk = int(options["comp_pk"][0])
            company_tidm = Companies.objects.filter(id=pk).values()[0]["tidm"]

        # try:
        # Ancillary Import if required
        if options["from_scratch"]:
            ancillary_num = management.call_command("ancillary_import")
            ancillary_result = f"Ancillary Tables; {ancillary_num}"
            return_results.append(ancillary_result)

        # Financial Import
        if options["comp_pk"] is None:
            reports_num = management.call_command(
                "financial_reports_import_tikr",
            )
        else:
            reports_num = management.call_command(
                "financial_reports_import_tikr", "--symbol", company_tidm
            )
        reports_result = f"Financial Reports; {reports_num}"
        return_results.append(reports_result)

        # # Financial Import Alpha Vantage
        # if options["comp_pk"] is None:
        #     reports_av_num = management.call_command(
        #         'financial_reports_import_av',
        #         )
        # else:
        #     reports_av_num = management.call_command(
        #         'financial_reports_import_av',
        #         '--symbol', company_tidm
        #         )
        # reports_av_result = f"Financial Reports Alpha Vantage; {reports_av_num}"
        # return_results.append(reports_av_result)

        # Share Price Import TIKR
        if options["comp_pk"] is None:
            share_price_num = management.call_command(
                "share_price_import_tikr",
            )
        else:
            share_price_num = management.call_command(
                "share_price_import_tikr", "--symbol", company_tidm
            )
        share_price_result = f"Share Price TIKR; {share_price_num}"
        return_results.append(share_price_result)

        # # Share Price Import Alpha Vantage
        # if options["comp_pk"] is None:
        #     share_price_num = management.call_command(
        #         'share_price_import_av',
        #         )
        # else:
        #     share_price_num = management.call_command(
        #         'share_price_import_av',
        #         '--symbol', company_tidm
        #         )
        # share_price_result = f"Share Price Alpha Vantage; {share_price_num}"
        # return_results.append(share_price_result)

        # Share split Calcs
        if options["comp_pk"] is None:
            share_split_num = management.call_command(
                "share_split_calcs",
            )
        else:
            share_split_num = management.call_command(
                "share_split_calcs", "--symbol", company_tidm
            )
        share_split_result = f"Share Split; {share_split_num}"
        return_results.append(share_split_result)

        # Default Variables import
        if options["comp_pk"] is None:
            default_var_num = management.call_command(
                "detault_dfc_variables",
            )
        else:
            default_var_num = management.call_command(
                "detault_dfc_variables", "--symbol", company_tidm
            )
        default_var_result = f"Default Variables; {default_var_num}"
        return_results.append(default_var_result)

        # Calculate Stats
        if options["comp_pk"] is None:
            calc_stats_num = management.call_command(
                "calculate_stats",
            )
        else:
            calc_stats_num = management.call_command(
                "calculate_stats", "--symbol", company_tidm
            )
        calc_stats_result = f"Calculate Stats; {calc_stats_num}"
        return_results.append(calc_stats_result)

        # Update Dashboard
        dash_stats = management.call_command("generate_dashboard")
        dash_stats_result = f"Dashboard; {dash_stats}"
        return_results.append(dash_stats_result)

        # Can only return strings from management commands
        return_string = "-".join(return_results)

        print("###### SUMMARY UPDATE STATS ROWS ADDED ######")
        print(reports_result)
        # print(reports_av_result)
        # print(share_price_result)
        print(share_split_result)
        print(default_var_result)
        print(calc_stats_result)
        print(dash_stats_result)

        return return_string

        # except Exception as e:
        # messages.add_message(request, messages.ERROR, f"{str(e)}")
