import logging

from django.conf import settings

from share_prices.logger import log
from share_prices.vendors.base import VendorClient


logger = logging.getLogger(__name__)


class AlphaVantageClient(VendorClient):
    NAME = "ALPHAVANTAGE"
    BASE_URL = "www.alphavantage.co/query?function="
    API_KEY = settings.ALPHA_VANTAGE_API_KEY
    API_KEY_AS_PARAM = "apikey"
    TIMEOUT = 10.0
    VERIFY = True

    def get_share_price(self, symbol):
        """
        Note - api call for share price
        """
        response = self._handle_call(
            params={
                "function": "TIME_SERIES_WEEKLY",
                "symbol": symbol,
            }
        )

        if isinstance(response, list):
            return response

        log.warning(f"Data not returned for symbol {symbol} processing")
        return []

    def get_income_statement(self, symbol):
        """
        Note - api call for share price
        """
        response = self._handle_call(
            params={
                "function": "INCOME_STATEMENT",
                "symbol": symbol,
            }
        )

        if isinstance(response, list):
            return response

        log.warning(f"Data not returned for symbol {symbol} processing")
        return []

    def get_balance_sheet(self, symbol):
        """
        Note - api call for share price
        """
        response = self._handle_call(
            params={
                "function": "BALANCE_SHEET",
                "symbol": symbol,
            }
        )

        if isinstance(response, list):
            return response

        log.warning(f"Data not returned for symbol {symbol} processing")
        return []

    def get_cash_flow_statement(self, symbol):
        """
        Note - api call for share price
        """
        response = self._handle_call(
            params={
                "function": "CASH_FLOW",
                "symbol": symbol,
            }
        )

        if isinstance(response, list):
            return response

        log.warning(f"Data not returned for symbol {symbol} processing")
        return []
