from urllib.parse import urlencode

import httpx
from django.conf import settings

from api_import.logger import log
from api_import.vendors.base import VendorClient


class FMPClient(VendorClient):
    NAME = "FMP"
    BASE_URL = "https://financialmodelingprep.com/stable"
    API_KEY_AS_PARAM = "apikey"
    TIMEOUT = 15.0
    VERIFY = True

    @property
    def API_KEY(self):
        return settings.FMP_API_KEY

    def _handle_list_call(self, path="", params=None):
        """FMP returns JSON lists, not dicts — override base _handle_call."""
        if not params:
            params = {}
        params[self.API_KEY_AS_PARAM] = self.API_KEY

        encoded_params = urlencode(params, doseq=True)
        url = f"{self.BASE_URL}{path}?{encoded_params}"

        try:
            log.debug(f"Request {url}")
            client = httpx.Client(timeout=self.TIMEOUT, verify=self.VERIFY)
            response = client.get(url)

            if response.status_code == 200:
                return response.json()
            else:
                log.error(
                    f"Unexpected response accessing {self.NAME} data",
                    extra={"status_code": response.status_code, "url": url},
                )
                print(f"  HTTP {response.status_code}: {url}")
                return []
        except (httpx.RequestError, httpx.TimeoutException) as e:
            log.error(
                f"Exception raised accessing {self.NAME} data",
                extra={"error": e, "url": url},
            )
            raise e

    def get_financial_data(self, symbol, statement_type, limit=20):
        """Fetch financial statements.

        statement_type: 'income-statement', 'balance-sheet-statement', 'cash-flow-statement'
        Returns list of period dicts, most recent first.
        """
        return self._handle_list_call(
            path=f"/{statement_type}",
            params={"symbol": symbol, "limit": limit},
        )

    def get_latest_report_date(self, symbol, statement_type):
        """Returns the most recent fiscal date string for a given statement type."""
        data = self.get_financial_data(symbol, statement_type, limit=1)
        if data:
            return data[0].get("date")
        return None

    def get_share_price_history(self, symbol, from_date=None, to_date=None):
        """Fetch historical daily prices.

        Returns a dict with 'symbol' and 'historical' (list of price dicts).
        Each price dict has: date, open, high, low, close, adjClose, volume, etc.
        """
        params = {"symbol": symbol}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        return self._handle_list_call(
            path="/historical-price-full",
            params=params,
        )

    def get_latest_quote(self, symbol):
        """Fetch the latest quote for a symbol. Returns a single quote dict or None."""
        data = self._handle_list_call(
            path="/quote",
            params={"symbol": symbol},
        )
        if data:
            return data[0]
        return None

    def get_company_profile(self, symbol):
        """Fetch company profile metadata. Returns a single profile dict or None."""
        data = self._handle_list_call(
            path="/profile",
            params={"symbol": symbol},
        )
        if data:
            return data[0]
        return None
