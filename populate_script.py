from sqlalch_project.ancillary_info.ancillary_info import AncillaryInfo
from sqlalch_project.financial_reports.financial import Financial
from sqlalch_project.share_prices.share_price import SharePrice
from sqlalch_project.calculated_stats.calculated_stats import CalculatedStats
from sqlalch_project.ranking_stats.ranking_stats import RankingStats


# Ancillary Info
myRepo = AncillaryInfo()
myRepo.populate_tables()
# result = myRepo.get_parameters_joined()
# result = myRepo.get_companies_joined()
# print(result)

# print(result.sample(10))

# Financial Reporting
myRepo = Financial()
myRepo.populate_tables()
# result = myRepo.get_financial_data()
# print(result.sample(10))

# Share Price
myRepo = SharePrice()
myRepo.populate_tables()
# result = myRepo.get_share_data()
# result = myRepo.get_share_joined()
# print(result.sample(10))

# Calculated Stats
myRepo = CalculatedStats()
myRepo.populate_tables()
# result = myRepo.get_share_data()
# result = myRepo.get_share_joined()
# print(result.sample(10))

# Calculated Stats
myRepo = RankingStats()
myRepo.populate_tables()
# result = myRepo.get_share_data()
# result = myRepo.get_share_joined()
# print(result.sample(10))
