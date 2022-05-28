from urllib.parse import urlencode

import httpx

from api_import.logger import log


class VendorClient:
    NAME = ""
    BASE_URL = ""
    API_KEY = ""
    API_KEY_AS_PARAM = ""
    VERIFY = True
    TIMEOUT = 10.0

    def _handle_call(self, path="", params=None):
        if not params:
            params = {}

        if self.API_KEY_AS_PARAM:
            params[self.API_KEY_AS_PARAM] = self.API_KEY

        encoded_params = urlencode(params, doseq=True)
        url = f"{self.BASE_URL}{path}?{encoded_params}"

        try:
            log.debug(f"Request {url}")
            client = httpx.Client(timeout=self.TIMEOUT, verify=self.VERIFY)
            response = client.get(url)

            if response.status_code == 200:
                _, header = response.json()
                return (header, response.json())
            else:
                log.error(
                    f"Unexpected response accessing {self.NAME} data",
                    extra={"status_code": response.status_code, "url": url},
                )
        except (httpx.RequestError, httpx.TimeoutException) as e:
            # log then raise.
            log.error(
                f"Exception raised accessing {self.NAME} data",
                extra={"error": e, "url": url},
            )
            raise e
