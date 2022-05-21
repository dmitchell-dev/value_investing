from database_interaction import DatabaseInteraction

table_name = "ranking_data"

table_object = DatabaseInteraction(table_name)

table_object.populate_ranking_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()
