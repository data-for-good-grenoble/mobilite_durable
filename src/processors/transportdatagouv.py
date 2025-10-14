"""
This module provides functionality to manage GTFS data pipeline tasks
such as filtering and downloading datasets from transport.data.gouv.fr.

- for now uses the ProcessorMixin to store the filtered dataset json downloaded from the API

Author: Laurent Sorba

Reference: https://github.com/data-for-good-grenoble/mobilite_durable/issues/4

"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests
from tqdm import tqdm

from src.settings import DATA_FOLDER
from src.utils.downloader_mixin import DownloaderMixin
from src.utils.logger import setup_logger
from src.utils.processor_mixin import ProcessorMixin

# Set up logger
logger = logging.getLogger(__name__)


class TransportDataGouvProcessor(ProcessorMixin, DownloaderMixin):
    """
    Processor for downloading GTFS data from transport.data.gouv.fr

    This processor:
    1. Fetches datasets from the transport.data.gouv.fr API
    2. Filters for public-transit datasets
       and checks that data is recent and has a valid GTFS format
    3. Downloads and saves the GTFS files, skips already downloaded GTFS files
       optionally force download.
    """

    # Define paths
    input_dir = DATA_FOLDER / "transportdatagouv"
    input_file = input_dir / "datasets.json"
    output_dir = input_dir
    output_file = output_dir / "filtered_datasets.json"

    # API URL
    API_URL = "https://transport.data.gouv.fr/api/datasets"

    # Reload filtered datasets
    reload_pipeline = True

    # Force download even if the GTFS already exists
    force_download = False

    # Maximum number of retries for downloads
    max_retries = 3

    # Timeout for download requests
    timeout = 60

    # Delete old files that are no more in transportdatagouv datasets
    delete_old_files = True

    # Number of days a resource is considered valid
    resource_validity_days_threshold = 90

    # Limit to x datasets for testing
    test_limit: int | None = None

    # Needed from ProcessorMixin
    api_class = True  # TODO Extract API logic into TransportDataGouvAPI class

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
    def get_dataset_recent_date(cls, dataset_id: str) -> datetime | None:
        """Query dataset details to determine the most relevant recent date.

        Prefers history[0].last_up_to_date_at, then history[0].updated_at,
        then history[0].inserted_at. Returns a timezone-aware datetime in UTC
        when possible.
        """
        if not dataset_id:
            return None

        url = f"{cls.API_URL}/{dataset_id}"
        resp = requests.get(url, timeout=cls.timeout)
        resp.raise_for_status()
        data = resp.json()
        history = data.get("history") or []
        recent_str = None
        if history:
            entry = history[0] or {}
            # Prefer last_up_to_date_at, fallback to updated_at, then inserted_at
            recent_str = (
                entry.get("last_up_to_date_at")
                or entry.get("updated_at")
                or entry.get("inserted_at")
            )
        # Parse ISO datetime (with Z)
        recent_dt = None
        if recent_str:
            try:
                # Ensure Z is parsed as UTC
                recent_dt = datetime.fromisoformat(recent_str.replace("Z", "+00:00"))
            except Exception:
                recent_dt = None

        return recent_dt

    @classmethod
    def save(cls, content, path: Path) -> None:
        """Save content to a file"""
        # super().save(content, path)

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
        - resources containing the "bus" or "coach" or "tramway" mode
        - datasets considered up-to-date according to transport.data.gouv.fr dataset history
        - resources have the available flag set to True
        - metadata end_date not in the past (if it exists)
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

            dataset_id = dataset.get("id")

            # Find valid resources
            valid_resources = []
            for resource in dataset.get("resources", []):
                # Check if resource has bus or coach or tramway mode
                modes = resource.get("modes", [])
                has_desired_mode = not modes or any(
                    mode in modes for mode in ["bus", "coach", "tramway", "cable_car"]
                )

                if not has_desired_mode:
                    logger.info(
                        f"Not a desired mode in GTFS: {dataset.get('id', 'unknown')}. Skipping."
                    )
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
                if (
                    "metadata" in resource
                    and "end_date" in resource["metadata"]
                    and resource["metadata"]["end_date"]
                ):
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

                # Check dataset recency from dataset API
                try:
                    recent_dt = cls.get_dataset_recent_date(dataset_id)
                except Exception as e:
                    logger.error(
                        f"Failed to fetch dataset history for {dataset_id}: {e}. Skipping dataset."
                    )
                    continue
                if recent_dt and recent_dt < valid_days_threshold:
                    logger.warning(
                        f"Dataset {dataset_id} considered outdated (history date {recent_dt}). Skipping."
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
    def parse_datasets(cls, datasets):
        """Parse datasets to extract URLs from its resources"""
        if cls.test_limit is None:
            total = len(datasets)
            logger.warning("Test limit is not set, processing all datasets")
        else:
            total = min(cls.test_limit, len(datasets))

        # For each dataset
        for dataset_index, dataset in tqdm(
            enumerate(datasets),
            total=total,
            desc="Processing datasets",
        ):
            # Limit to test_limit datasets for testing
            if cls.test_limit and dataset_index >= cls.test_limit:
                logger.debug(
                    f"Test limit reached ({cls.test_limit} datasets). Stopping process."
                )
                break

            dataset_id = dataset.get("id", "unknown")

            # For each resource in the dataset, add url & destination file to the list
            for resource in dataset.get("resources", []):
                url, download_path = cls.extract_url_from_resource(dataset_id, resource)
                cls.urls.append(url)
                cls.destinations.append(download_path)

    @classmethod
    def extract_url_from_resource(cls, dataset_id, resource) -> tuple[str, Path]:
        """Extract URL of the GTFS file from resource and create the output path"""

        url = resource.get("url")
        datagouv_id = resource.get("datagouv_id")
        updated = resource.get("updated", datetime.now().strftime("%Y-%m-00")).split("T")[0]
        if not url:
            raise Exception(f"Resource {dataset_id}/{datagouv_id} has no URL")

        # Create a filename based on the updated date, dataset ID and datagouv ID
        filename = f"{updated}_{dataset_id}_{datagouv_id}.zip"
        if cls.output_dir is None:
            raise ValueError("Output directory is not defined. Please set `output_dir`.")
        output_path = cls.output_dir / filename

        logger.debug(f"Adding {url} to download to {output_path.absolute()}")
        return url, output_path

    @classmethod
    def run_all(cls, reload_pipeline: bool = False) -> None:
        """
        Run the processor to filter datasets/resources
        and run the downloader to download the GTFS data
        """
        if cls.output_file is None:
            raise ValueError("Output file is not defined. Please set `output_file`.")
        if cls.output_dir is None:
            raise ValueError("Output directory is not defined. Please set `output_dir`.")

        if cls.output_file and (reload_pipeline or not cls.output_file.exists()):
            # Preprocess and filter datasets
            cls.fetch(reload_pipeline=reload_pipeline)

        # Use filtered_datasets.json to download the GTFS files
        if cls.output_file.exists():
            with open(cls.output_file, "r") as f:
                filtered_datasets = json.load(f)
                cls.parse_datasets(filtered_datasets)
                logger.info(
                    f"Processed finished. Found {sum(len(d.get('resources', [])) for d in filtered_datasets)} GTFS files from {len(filtered_datasets)} datasets"
                )

                # Download the GTFS files and display status
                if cls.test_limit and cls.test_limit > 0:
                    cls.urls = cls.urls[: cls.test_limit]
                    cls.destinations = cls.destinations[: cls.test_limit]

                status_counts = cls.download_files(
                    cls.force_download, cls.max_retries, cls.timeout
                )
                for status, files in status_counts.items():
                    logger.info(f"Files {status}: {len(files)} - {files}")
                logger.info("Downloaded all requested GTFS files")

                # Delete old ZIP files that are not in the destinations
                if cls.delete_old_files:
                    zip_files_in_dir = filter(
                        lambda f: f.suffix == ".zip", cls.output_dir.iterdir()
                    )
                    files_to_delete = list(
                        filter(lambda f: f not in cls.destinations, zip_files_in_dir)
                    )
                    logger.info(f"{len(files_to_delete)} old files to delete")
                    for file in files_to_delete:
                        try:
                            file.unlink()
                            logger.info(f"Deleted old file: {file}")
                        except Exception as e:
                            logger.error(f"Failed to delete {file}: {e}")

                else:
                    logger.warning(
                        "Fail to delete old files because no destinations were found."
                    )
        else:
            logger.warning(f"Output file {cls.output_file} does not exist. No processing done.")


def main(**kwargs):
    logger.info("Running the full pipeline")
    TransportDataGouvProcessor.run_all(
        reload_pipeline=TransportDataGouvProcessor.reload_pipeline
    )


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)

    # TransportDataGouvProcessor.test_limit = 1 # Defaults to None
    TransportDataGouvProcessor.force_download = False  # Defaults to False
    TransportDataGouvProcessor.resource_validity_days_threshold = 90  # Defaults to 90

    main()
