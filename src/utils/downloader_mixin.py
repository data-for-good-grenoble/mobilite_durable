import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
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
    def download_file(url: str, destination: Path, force_download=False) -> tuple[str, str]:
        """
        Download a file from a given URL to a specified destination.

        :param url: The URL of the file to download.
        :param destination: The local path where the file will be saved.
        :param force_download: If True, force download even if the file already exists. Default is False.
        :return: A tuple containing the status of the download and the filename.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # File exists?
            if os.path.exists(destination) and not force_download:
                logger.warning(f"File {destination} already exists, skipping.")
                return DownloadStatus.SKIPPED, destination.name

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
            logging.error(f"HTTP error occurred while downloading {url}: {http_err}")
            return DownloadStatus.ERROR, destination.name
        except Exception as e:
            logging.error(f"Error downloading {url}: {e}")
            return DownloadStatus.ERROR, destination.name

    @classmethod
    def download_files(cls) -> dict[str, list[str]]:
        """
        Download multiple files from a list of URLs to specified destinations in parallel.

        :return: A dictionary with the count of each download status and associated filenames.
        """
        status_counts = {
            DownloadStatus.DOWNLOADED: [],
            DownloadStatus.SKIPPED: [],
            DownloadStatus.ERROR: [],
        }

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(cls.download_file, url, dest): url
                for url, dest in zip(cls.urls, cls.destinations)
            }
            for future in tqdm(
                as_completed(futures), total=len(futures), desc="Downloading files"
            ):
                url = futures[future]
                status, filename = future.result()  # Get the download status and filename
                status_counts[status].append(
                    filename
                )  # Update the status count with the filename

        return status_counts
