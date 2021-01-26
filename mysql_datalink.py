import mysql.connector as mysql
import os


db_username = os.environ['DJANGO_DB_USERNAME']
db_password = os.environ['DJANGO_DB_PASSWORD']
db_name = os.environ['DJANGO_DB_NAME']


class MysqlDatalink:
    """A class to connect to MyAnalytics Database."""

    def __init__(self):
        """Initialize attributes of a database connection."""

        self.db = mysql.connect(
                host="localhost",
                user=db_username,
                passwd=db_password,
                database=db_name
                )

        self.cursor = self.db.cursor()
