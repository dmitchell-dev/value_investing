from database_interaction import DatabaseInteraction

table_name = "share_price"

table_object = DatabaseInteraction(table_name)

table_object.populate_share_price_table()

data = table_object.get_data()
print(data.head())

table_object.db.close()
