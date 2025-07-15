"""
This module provides functionality to manage GTFS data pipeline tasks
such as filtering and downloading datasets from transport.data.gouv.fr.

Author: Laurent Sorba

Reference: https://github.com/data-for-good-grenoble/mobilite_durable/issues/4

TODO
- make it fit better the ProcessorMixin
  - output is not one file but a set of GTFS, for now storing the dataset json from the API
- filter better the GTFS
- delete files which are not in the datasets anymore
- asynchronous downloads
- progress bar: download, process
"""

import glob
import json
import logging
import os
import zipfile
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import requests

from src.processors.utils import ProcessorMixin
from src.settings import DATA_FOLDER
from src.utils.logger import setup_logger

# Set up logger
logger = logging.getLogger(__name__)


class TransportDataGouvProcessor(ProcessorMixin):
    """
    Processor for downloading GTFS data from transport.data.gouv.fr

    This processor:
    1. Fetches datasets from the transport.data.gouv.fr API
    2. Filters for public-transit datasets
       and checks that data is recent and has a valid GTFS format
    3. Downloads and saves the GTFS files, skips already downloaded GTFS files
       optionally force download, gets the latest updates and deletes the old GTFS files.
    """

    # Define paths
    input_dir = DATA_FOLDER / "transportdatagouv"
    input_file = input_dir / "datasets.json"
    output_dir = input_dir
    output_file = output_dir / "filtered_datasets.json"

    # API URL
    API_URL = "https://transport.data.gouv.fr/api/datasets"

    # Force download even if the GTFS already exists
    force_download = False

    # Number of days a resource is considered valid
    resource_validity_days_threshold = 365

    # Limit to x datasets for testing
    test_limit = None

    # Needed from ProcessorMixin
    api_class = True

    @classmethod
    def fetch_from_api(cls, **kwargs):
        """Fetch datasets from transport.data.gouv.fr API"""
        response = requests.get(cls.API_URL)
        response.raise_for_status()
        datasets = response.json()
        return datasets

    @classmethod
    def fetch_from_file(cls, path, **kwargs):
        """Load datasets from a JSON file"""
        with open(path, "r") as f:
            return json.load(f)

    @classmethod
    def save(cls, content, path: Path) -> None:
        """Save content to a file"""
        super().save(content, path)

        # If it's a JSON file, save as JSON
        if path.suffix == ".json":
            with open(path, "w") as f:
                json.dump(content, f, indent=2)
        # Otherwise, assume it's binary content
        else:
            with open(path, "wb") as f:
                f.write(content)

    @classmethod
    def pre_process(cls, content, **kwargs):
        """
        Filter datasets for:
        - type="public-transit"
        - resources containing "bus" mode
        - resources updated within the last year
        - resources have the available flag set to True
        - resources last updated within the last year
        - metadata end_date not in the past (if it exists)

        TODO:
        - some resources can contain both bus and another mode, for now download if at least one bus resource is available
        - some resources can have long-distance lines across Europe like flixbus
        """
        filtered_datasets = []
        # Create a timezone-aware datetime
        valid_days_threshold = datetime.now().replace(
            tzinfo=datetime.now().astimezone().tzinfo
        ) - timedelta(days=cls.resource_validity_days_threshold)
        today = datetime.now().replace(tzinfo=datetime.now().astimezone().tzinfo)

        for dataset in content:
            # Check if dataset is public-transit type
            if dataset.get("type") != "public-transit":
                continue

            # Find resources with bus mode that are less than a year old
            valid_resources = []
            for resource in dataset.get("resources", []):
                # Check if resource has bus mode
                if "bus" not in resource.get("modes", []):
                    continue

                if "GTFS" not in resource.get("format", ""):
                    logger.info(
                        f"Not a GTFS resource: {dataset.get('id', 'unknown')}. Skipping."
                    )
                    continue

                if "is_available" in resource and resource["is_available"] is False:
                    logger.info(
                        f"Resource flagged as not available: {dataset.get('id', 'unknown')}. Skipping."
                    )
                    continue

                # Check metadata end_date if it exists
                if "metadata" in resource and "end_date" in resource["metadata"]:
                    end_date_str = resource["metadata"]["end_date"]
                    try:
                        # Parse the end_date (assuming format YYYY-MM-DD)
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(
                            tzinfo=today.tzinfo
                        )
                        if end_date < today:
                            logger.info(
                                f"Resource end_date {end_date_str} is in the past for dataset {dataset.get('id', 'unknown')}. Skipping."
                            )
                            continue
                    except ValueError:
                        logger.warning(
                            f"Invalid end_date format '{end_date_str}' for dataset {dataset.get('id', 'unknown')}. Skipping."
                        )
                        continue

                # Check if the resource is recent
                if "updated" in resource:
                    updated_date = datetime.fromisoformat(
                        resource["updated"].replace("Z", "+00:00")
                    )
                    if updated_date < valid_days_threshold:
                        logger.warning(
                            f"Dataset {dataset.get('id', 'unknown')} last updated in {updated_date}. Skipping."
                        )
                        continue

                valid_resources.append(resource)

            # If we found valid resources, add this dataset to our filtered list
            if valid_resources:
                # Replace the original resources with only the valid ones
                dataset_copy = dataset.copy()
                dataset_copy["resources"] = valid_resources
                filtered_datasets.append(dataset_copy)
                logger.info(
                    f"Added dataset {dataset.get('id', 'unknown')} with {len(valid_resources)} valid resources"
                )

        return filtered_datasets

    @classmethod
    def download_gtfs_files(cls, datasets):
        """Download GTFS files from the filtered datasets"""

        status_counts = {
            TransportDataGouvProcessor.DownloadStatus.DOWNLOADED: 0,
            TransportDataGouvProcessor.DownloadStatus.SKIPPED: 0,
            TransportDataGouvProcessor.DownloadStatus.ERROR: 0,
        }

        # Ensure the output directory exists
        cls.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting downloads to {cls.output_dir.absolute()}")
        logger.debug(f"Output directory exists: {cls.output_dir.exists()}")

        # For each dataset
        for dataset_index, dataset in enumerate(datasets):
            # Limit to test_limit datasets for testing
            if cls.test_limit and dataset_index >= cls.test_limit:
                logger.info(
                    f"Test limit reached ({cls.test_limit} datasets). Stopping downloads."
                )
                break

            dataset_id = dataset.get("id", "unknown")
            logger.info(
                f"Processing dataset {dataset_id} ({dataset_index + 1}/{min(cls.test_limit, len(datasets))})"
            )

            # For each resource in the dataset
            for i, resource in enumerate(dataset.get("resources", [])):
                status = cls.download_GTFS_from_resource(dataset_id, resource, True)
                status_counts[status] += 1

        logger.info(
            f"Download summary: "
            f"{status_counts[TransportDataGouvProcessor.DownloadStatus.DOWNLOADED]} files downloaded, "
            f"{status_counts[TransportDataGouvProcessor.DownloadStatus.SKIPPED]} files skipped, "
            f"{status_counts[TransportDataGouvProcessor.DownloadStatus.ERROR]} errors"
        )

    @classmethod
    def delete_files(cls, file_dataset_id, file_datagouv_id):
        # Construct the pattern for the files to delete
        pattern = f"*_{file_dataset_id}_{file_datagouv_id}.zip"

        # Use glob to find all files matching the pattern
        search_pattern = os.path.join(cls.output_dir, pattern)
        files_to_delete = glob.glob(search_pattern)

        # Delete each file found
        for file in files_to_delete:
            try:
                os.remove(file)
                logger.info(f"\t\tDeleted {file}.")
            except Exception as ex:
                logger.error(f"\t\tError deleting {file}: {ex}")

    @classmethod
    def check_zipfile(cls, output_path):
        """Validate that it's a valid ZIP file"""
        # Verify the file was created
        if not output_path.exists():
            raise Exception(f"File is not found {output_path.absolute()}")

        try:
            with zipfile.ZipFile(output_path) as zf:
                file_list = zf.namelist()
                logger.debug(f"\t\tZIP file contains {len(file_list)} files")
        except zipfile.BadZipFile:
            raise Exception(f"Downloaded file is not a valid ZIP file: {output_path}")

    @classmethod
    def run(cls, reload_pipeline: bool = False) -> None:
        """Run the processor to download GTFS data"""

        content = cls.fetch(reload_pipeline=reload_pipeline)

        if cls.output_file and (reload_pipeline or not cls.output_file.exists()):
            output_content = cls.pre_process(content)
            cls.save(output_content, cls.output_file)

        # TODO Overridden run() function
        # To download the GTFS files: we have more than 1 output_file
        if cls.output_file.exists():
            with open(cls.output_file, "r") as f:
                filtered_datasets = json.load(f)
                cls.download_gtfs_files(filtered_datasets)
                logger.info(
                    f"Processed finished. Found {sum(len(d.get('resources', [])) for d in filtered_datasets)} GTFS files from {len(filtered_datasets)} datasets"
                )

    class DownloadStatus(Enum):
        DOWNLOADED = "downloaded"
        SKIPPED = "skipped"
        ERROR = "error"

    @classmethod
    def download_GTFS_from_resource(cls, dataset_id, resource, delete_old_files=True):
        """Get URL from resource and download the GTFS file to output directory"""

        url = resource.get("url")
        datagouv_id = resource.get("datagouv_id")
        updated = resource.get("updated", datetime.now().strftime("%Y-%m-00")).split("T")[0]
        if not url:
            logger.error(f"\t\tResource {dataset_id}/{datagouv_id} has no URL, skipping.")
            return TransportDataGouvProcessor.DownloadStatus.SKIPPED

        # Create a filename based on the updated date, dataset ID and datagouv ID
        filename = f"{updated}_{dataset_id}_{datagouv_id}.zip"
        output_path = cls.output_dir / filename

        # File exists?
        if output_path.exists() and not cls.force_download:
            logger.warning(f"\t\tFile {filename} already exists, skipping.")
            return TransportDataGouvProcessor.DownloadStatus.SKIPPED

        logger.debug(f"\t\tDownloading {url} to {output_path.absolute()}")

        # Download the file
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Delete old files for this dataset_id and datagouv_id
            if delete_old_files:
                cls.delete_files(dataset_id, datagouv_id)

            # Save the content directly to file
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            cls.check_zipfile(output_path)

            logger.debug(f"\t\tSuccessfully downloaded to {output_path.absolute()}")
            logger.debug(f"\t\tFile size: {output_path.stat().st_size} bytes")

            return TransportDataGouvProcessor.DownloadStatus.DOWNLOADED

        except Exception as e:
            logger.error(f"\t\tERROR downloading {url}: {e}")
            return TransportDataGouvProcessor.DownloadStatus.ERROR


def main():
    TransportDataGouvProcessor.test_limit = 20  # Defaults to None
    TransportDataGouvProcessor.force_download = False  # Defaults to False
    TransportDataGouvProcessor.resource_validity_days_threshold = 365  # Defaults to 365

    logger.info("Running full pipeline (download)")
    TransportDataGouvProcessor.run(reload_pipeline=False)


if __name__ == "__main__":
    # Set up logger
    setup_logger(level=logging.DEBUG)
    main()
