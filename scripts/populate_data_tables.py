from database_interaction import DatabaseInteraction

table_name = "reporting_data"

table_object = DatabaseInteraction(table_name)

table_object.populate_data_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()
