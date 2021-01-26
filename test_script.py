from sqlalch_project.ancillary_info.ancillary_info import AncillaryInfo
from sqlalch_project.financial_reports.financial import Financial


# Ancillary Info
myRepo = AncillaryInfo()
# myRepo.populate_tables()
# result = myRepo.get_parameters_joined()
# result = myRepo.get_companies_joined()
# print(result)

# print(result.sample(10))

# Financial Reporting
myRepo = Financial()
myRepo.populate_tables()
# result = myRepo.get_financial_data()
# print(result.sample(10))
