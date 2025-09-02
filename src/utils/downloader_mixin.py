import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
from typing import List

import requests
from tqdm import tqdm


class DownloadStatus:
    DOWNLOADED = "Downloaded"
    SKIPPED = "Skipped"
    ERROR = "Error"


# Set up logger
logger = logging.getLogger(__name__)


class DownloaderMixin:
    """
    Parallel downloader mixin with a progress bar and status count

    Author: Laurent Sorba
    """

    urls: List[str] = []
    destinations: List[Path] = []

    @staticmethod
    def download_file(
        url: str, destination: Path, force_download=False, max_retries=3, timeout=60
    ) -> tuple[str, str]:
        """
        Download a file from a given URL to a specified destination.

        :param url: The URL of the file to download.
        :param destination: The local path where the file will be saved.
        :param force_download: If True, force download even if the file already exists. Default is False.
        :param max_retries: Maximum number of retries for 429 (Too Many Requests) and 503 (Service Unavailable) responses. Default is 3.
        :param timeout: Timeout for the download request in seconds. Default is 60.
        :return: A tuple containing the status of the download and the filename.
        """
        # File exists? or force download
        if os.path.exists(destination) and not force_download:
            logger.warning(f"File {destination} already exists, skipping.")
            return DownloadStatus.SKIPPED, destination.name

        response = None
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, stream=True, timeout=timeout)

                # If we get a 429 or a 503, retry if we have attempts left
                if (response.status_code == 429 or response.status_code == 503) and attempt < max_retries:
                    # Get retry delay from header, default to 5 seconds
                    retry_after = int(response.headers.get("Retry-After", 2 * (attempt + 1)))
                    logger.warning(f"Error when downloading {url}, retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                logger.debug(f"Downloading {url} to {destination}")

                with (
                    open(destination, "wb") as file,
                    tqdm(
                        desc="Downloading " + destination.name,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        leave=True,
                    ) as bar,
                ):
                    for data in response.iter_content(chunk_size=1024):
                        file.write(data)
                        bar.update(len(data))

                return DownloadStatus.DOWNLOADED, destination.name

            except requests.HTTPError as http_err:
                logger.error(f"HTTP error occurred while downloading {url}: {http_err}")
                return DownloadStatus.ERROR, destination.name
            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")
                return DownloadStatus.ERROR, destination.name

        # If we get here, we've exhausted all retries
        return DownloadStatus.ERROR, destination.name

    @classmethod
    def download_files(cls, force_download=False, max_retries=3, timeout=60) -> dict[str, list[str]]:
        """
        Download multiple files from a list of URLs to specified destinations in parallel.

        :param force_download: If True, force download even if the file already exists. Default is False.
        :param max_retries: Maximum number of retries for 429 (Too Many Requests) and 503 (Service Unavailable) responses. Default is 3.
        :param timeout: Timeout for the download request in seconds. Default is 60.

        :return: A dictionary with the count of each download status and associated filenames.
        """
        status_counts: dict[str, list[str]] = {
            DownloadStatus.DOWNLOADED: [],
            DownloadStatus.SKIPPED: [],
            DownloadStatus.ERROR: [],
        }

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(cls.download_file, url, dest, force_download, max_retries, timeout): (url, dest)
                for url, dest in zip(cls.urls, cls.destinations, strict=True)
            }
            for future in tqdm(
                as_completed(futures), total=len(futures), desc="Downloading files"
            ):
                status, filename = future.result()  # Get the download status and filename
                status_counts[status].append(filename)  # Update the status count

        return status_counts
