from database_interaction import DatabaseInteraction

table_name = "calculated_data"

table_object = DatabaseInteraction(table_name)

table_object.populate_calculated_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()
