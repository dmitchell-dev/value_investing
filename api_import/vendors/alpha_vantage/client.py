import logging

from django.conf import settings

from api_import.logger import log
from api_import.vendors.base import VendorClient


logger = logging.getLogger(__name__)


class AlphaVantageClient(VendorClient):
    NAME = "ALPHAVANTAGE"
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = settings.ALPHA_VANTAGE_API_KEY
    API_KEY_AS_PARAM = "apikey"
    TIMEOUT = 10.0
    VERIFY = True

    def get_share_data(self, location, symbol, type):
        """
        Note - api call for share price
        """

        # Format symbol for UK API calls
        if location == "UK":
            symbol = symbol + ".LON"

        # AV API does not seems to take into account
        # the . in some symbols with the API call
        if ".." in symbol:
            symbol = symbol.replace("..", ".")

        # Call API
        header, response = self._handle_call(
            params={
                "function": type,
                "symbol": symbol,
            }
        )

        # Select correct row
        header = header[1]

        if isinstance(response, dict):
            return (header, response)

        log.warning(f"Data not returned for symbol {symbol} processing")
        return []

    def get_financial_data(self, symbol, type):
        """
        Note - api call for share price
        """

        # Call API
        header, response = self._handle_call(
            params={
                "function": type,
                "symbol": symbol,
            }
        )

        # Select correct row
        header = header[1]

        if isinstance(response, dict):
            return (header, response)

        log.warning(f"Data not returned for symbol {symbol} processing")
        return []
