import logging
from datetime import datetime

import requests

from utils.logger import setup_logger

# Set up logger
logger = setup_logger(level=logging.DEBUG, name=__name__)


class OverpassAPI:
    API_URL = "https://overpass-api.de/api/interpreter"

    @classmethod
    def query_overpass(cls, query: str, timeout: int) -> dict:
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
        response.raise_for_status()
        end = datetime.now()
        elapsed = end - start
        logger.info(f"Getting overpass query results in {elapsed.seconds}s")
        return response.json()
