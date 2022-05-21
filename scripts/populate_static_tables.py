from database_interaction import DatabaseInteraction

# Populate Static tables
table_name_list = [
    "markets",
    "company_type",
    "industry_risk",
    "report_type",
    "calc_variables",
    "industries",
    "report_section",
    "parameters",
    "companies",
]

for table in table_name_list:
    table_object = DatabaseInteraction(table)

    table_object.populate_static_table()

    data = table_object.get_data()
    print(data)

    table_object.db.close()
