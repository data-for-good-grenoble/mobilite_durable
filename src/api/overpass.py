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
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        backoff_multiplier: float = 5.0,
    ) -> dict:
        """
        Query Overpass API with exponential retry.

        Args:
            query: Overpass QL query
            timeout: Query timeout in seconds
            max_retries: Maximum number of retry attempts
            initial_retry_delay: Initial delay in seconds before first retry
            max_retry_delay: Maximum delay cap in seconds
            backoff_multiplier: Multiplier for exponential backoff

        Returns:
            JSON response from the API
        """
        start = datetime.now()
        retry_delay = initial_retry_delay
        response = None

        for attempt in range(max_retries + 1):
            try:
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
            except requests.HTTPError as e:
                if (
                    attempt < max_retries
                    and response is not None
                    and response.status_code in (429, 504)
                ):
                    logger.warning(
                        f"Overpass API returned {response.status_code} error. "
                        f"Retry attempt {attempt + 1}/{max_retries} in {retry_delay} seconds"
                    )
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * backoff_multiplier, max_retry_delay)
                else:
                    raise e
            except requests.Timeout as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Overpass API timeout. "
                        f"Retry attempt {attempt + 1}/{max_retries} in {retry_delay} seconds"
                    )
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * backoff_multiplier, max_retry_delay)
                else:
                    raise e
        raise ValueError("Exceeded maximum retry attempts for Overpass API query")
