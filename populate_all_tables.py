from database_interaction import DatabaseInteraction

# Populate Static tables
table_name_list = ["markets",
                   "company_type",
                   "industry_risk",
                   "report_type",
                   "industries",
                   "report_section",
                   "parameters",
                   "calc_variables",
                   "companies"]

for table in table_name_list:
    table_object = DatabaseInteraction(table)

    table_object.populate_static_table()

    data = table_object.get_data()
    print(data)

    table_object.db.close()

# Populate company report data
table_name = "reporting_data"

table_object = DatabaseInteraction(table_name)

table_object.populate_data_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()

# Populate Share Prices
table_name = "share_price"

table_object = DatabaseInteraction(table_name)

table_object.populate_share_price_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()

# Populate Calculated data
table_name = "calculated_data"

table_object = DatabaseInteraction(table_name)

table_object.populate_calculated_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()

# Populate Rank Table
table_name = "ranking_data"

table_object = DatabaseInteraction(table_name)

table_object.populate_ranking_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()
