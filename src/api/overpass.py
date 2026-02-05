import logging
import time
from datetime import datetime

import requests

# Set up logger
logger = logging.getLogger(__name__)


class OverpassAPI:
    API_URL = "https://overpass-api.de/api/interpreter"

    @classmethod
    def query_overpass(
        cls,
        query: str,
        timeout: int,
        retry_sleep_in_seconds: int = 1,
        *,
        retry_in_case_of_504: bool = True,
    ) -> dict:
        """
        Query Overpass API.

        Args:
            query: Overpass QL query
            timeout: Query timeout in seconds

        Returns:
            JSON response from the API
        """
        start = datetime.now()
        response = requests.post(
            cls.API_URL,
            data={"data": query},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if retry_in_case_of_504 and response.status_code == 504:
                logger.warning(
                    f"Overpass API returned 504 error, retrying in {retry_sleep_in_seconds} seconds"
                )
                time.sleep(retry_sleep_in_seconds)
                return cls.query_overpass(
                    query,
                    timeout,
                    retry_in_case_of_504=False,
                )
            else:
                raise e
        end = datetime.now()
        elapsed = end - start
        logger.info(f"Getting overpass query results in {elapsed.seconds}s")
        return response.json()
