# value_investing

This is a personal site being developed to help with value investing.

The raw core company report and share data is download in csv format. This is imported and saved in a database. Ultimately this data may be imported from APIs.

The various metrics are then calulated and again stored in the database.

These metrics will then be presented on a Django site to help with selection.

I am using SQLAlchemy to start with instead of Django ORM. This is to help learn using an ORM, generating the metrics, and clean architecture, initially without the overhead of Django.

The aim of this site is to not only help with value investing, it will also improve:
* General Python Skills
* OOP
* Database skills
* Import data from various sources
* Move towards a more clean architecture