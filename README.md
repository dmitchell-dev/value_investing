# value_investing

This is a personal site being developed to help with value investing.

The raw core company report and share data is download in csv format. This is imported and saved in a database. Ultimately this data may be imported from APIs.

The various metrics are then calulated and again stored in the database.

These metrics will then be presented on the Django site to help with selection. The metrics will be presented on top level and company dashboards. Timeseries data such as share price and metrics over time will also be presented. Eventually share portfolio and decision tracking will be added.

I used SQLAlchemy initially instead of Django ORM. This was to help learn using an ORM, generating the metrics, and using a more clean architecture, initially without the overhead of Django. It is not a completely clean architecture as data types being passed are dataframes and not something like JSON. But an order of magnitude better than the starting class (database_interaction).

The aim of this site is to not only help with value investing, it will also improve:
* General Python Skills
* OOP
* Database skills
* Import data from various sources
* Move towards a more clean architecture
* Improve Django skills with management commands, Dashboard and timeseries data presentation

## APPL is used as an example

## Initialising Project with initial data
* python manage.py ancillary_import

* python manage.py financial_reports_import_tikr --symbol AAPL
* python manage.py financial_reports_import_av --symbol AAPL

* python manage.py share_price_import_tikr --symbol AAPL
* python manage.py share_price_import_av --symbol AAPL

* python manage.py share_split_calcs --symbol AAPL
* python manage.py detault_dfc_variables --symbol AAPL
* python manage.py calculate_stats --symbol AAPL
* python manage.py generate_dashboard

* python manage.py generate_portfolio