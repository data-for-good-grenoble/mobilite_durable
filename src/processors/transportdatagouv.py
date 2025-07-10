"""
This module provides functionality to manage GTFS data pipeline tasks
such as downloading, loading, merging, and cleaning datasets from transport.data.gouv.fr.

Author: Laurent Sorba

Reference: https://github.com/data-for-good-grenoble/mobilite_durable/issues/4

TODO
- make it fit better the ProcessorMixin
- filter better the GTFS
- clean better the GTFS
  - delete duplicates
  - delete schedules in the past
- option to force download even if resource exists
- option to skip already downloaded resources
- too much data to process
  - optimise process: for now, loads all in memory using gtfs-kit and then write to Parquet or GTFS
  - or save in database ?
- asynchronous downloads
- progress bar: download, process
"""

import glob
import json
import logging
import zipfile
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import gtfs_kit as gk
import pandas as pd
import requests
from gtfs_kit import Feed

from src.processors.utils import ProcessorMixin
from src.settings import DATA_FOLDER
from src.utils.logger import setup_logger

# Set up logger
logger = logging.getLogger(__name__)


def sanitize_name(name) -> str:
    """
    Sanitize a given name by removing any unwanted characters and
    normalizing the format.

    Args:
        name (str): The name to be sanitized. It may contain unwanted
                    characters or formatting.

    Returns:
        str: A sanitized version of the input name, with unwanted characters
    """
    import re

    # Enlever les caractères spéciaux tout en gardant les lettres accentuées
    sanitized = re.sub(r"[^a-zA-Z0-9À-ÿ]", "", name)

    # Restreindre à un maximum de 10 caractères
    sanitized = sanitized[:10]

    return sanitized


def merge_feed_attribute(resulting_feed, feed, attribute_name):
    """
    Merge a single attribute from source feed to resulting feed if it exists and is not empty.

    Args:
        resulting_feed: The target feed to merge into
        feed: The source feed to merge from
        attribute_name: The name of the attribute to merge
    """
    if (
        hasattr(feed, attribute_name)
        and getattr(feed, attribute_name) is not None
        and not getattr(feed, attribute_name).empty
    ):
        source_data = getattr(feed, attribute_name)
        target_data = getattr(resulting_feed, attribute_name)

        merged_data = pd.concat([target_data, source_data]).drop_duplicates()
        setattr(resulting_feed, attribute_name, merged_data)
        logger.debug(f"Merged {attribute_name}: {len(source_data)} rows added")


class TransportDataGouvProcessor(ProcessorMixin):
    """
    Processor for downloading, loading, merging, and cleaning GTFS data from transport.data.gouv.fr

    This processor:
    1. Fetches datasets from the transport.data.gouv.fr API
    2. Filters for public-transit datasets with bus mode
    3. Checks that data is less than a year old
    4. Downloads and saves the GTFS files
    5. Loads all GTFS files from the data/transportdatagouv folder
    6. Merges the GTFS data with appropriate prefixes
    7. Cleans the merged data using gtfs-kit
    8. Saves the cleaned and merged GTFS data as a zip file or in parquet format
    """

    # Define paths
    input_dir = DATA_FOLDER / "transportdatagouv"
    input_file = input_dir / "datasets.json"
    output_dir = input_dir

    # API URL
    API_URL = "https://transport.data.gouv.fr/api/datasets"

    class SaveMethod(Enum):
        PARQUET = 0
        GTFS = 1

    save_method = SaveMethod.GTFS

    # Limit to x datasets for testing (download and process)
    test_limit = None

    @classmethod
    def fetch_from_api(cls, **kwargs):
        """Fetch datasets from transport.data.gouv.fr API"""
        response = requests.get(cls.API_URL)
        response.raise_for_status()
        datasets = response.json()

        # Save the raw API response
        if cls.input_file:
            cls.save_datasets_list(datasets, cls.input_file)

        return datasets

    @classmethod
    def fetch_from_file(cls, path, **kwargs):
        """Load datasets from a JSON file"""
        with open(path, "r") as f:
            return json.load(f)

    @classmethod
    def save_datasets_list(cls, content, path: Path) -> None:
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
        - metadata end_date not in the past (if it exists)

        TODO:
        - some resources can contain both bus and another mode, for now download if at least one bus resource is available
        """
        filtered_datasets = []
        # Create a timezone-aware datetime for one year ago
        one_year_ago = datetime.now().replace(
            tzinfo=datetime.now().astimezone().tzinfo
        ) - timedelta(days=365)
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

                # Check if resource is recent (less than a year old)
                if "updated" in resource:
                    updated_date = datetime.fromisoformat(
                        resource["updated"].replace("Z", "+00:00")
                    )
                    if updated_date < one_year_ago:
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
        download_count = 0
        error_count = 0

        # Ensure the output directory exists
        cls.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting downloads to {cls.output_dir.absolute()}")
        logger.info(f"Output directory exists: {cls.output_dir.exists()}")

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

            for i, resource in enumerate(dataset.get("resources", [])):
                url = resource.get("url")
                if not url:
                    logger.info(f"  Resource {i} has no URL, skipping")
                    continue

                # Create a filename based on the date, dataset ID and resource index
                date_prefix = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_prefix}_{dataset_id}_{i}.zip"
                output_path = cls.output_dir / filename

                logger.info(f"  Downloading {url} to {output_path.absolute()}")

                # Download the file
                try:
                    response = requests.get(url, stream=True)
                    response.raise_for_status()

                    # Save the content directly to file
                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Verify the file was created
                    if not output_path.exists():
                        raise Exception(f"File was not created at {output_path.absolute()}")

                    download_count += 1
                    logger.info(f"  Successfully downloaded to {output_path.absolute()}")
                    logger.info(f"  File size: {output_path.stat().st_size} bytes")

                    # Validate that it's a valid ZIP file
                    try:
                        with zipfile.ZipFile(output_path) as zf:
                            file_list = zf.namelist()
                            logger.info(f"  ZIP file contains {len(file_list)} files")
                    except zipfile.BadZipFile:
                        logger.warning(
                            f"  Downloaded file is not a valid ZIP file: {output_path}"
                        )

                except Exception as e:
                    error_count += 1
                    logger.error(f"  ERROR downloading {url}: {e}")

        logger.info(
            f"Download summary: {download_count} files downloaded, {error_count} errors"
        )

    @classmethod
    def fetch(cls, reload_pipeline: bool = False) -> list:
        """
        Override the fetch method to correctly call our fetch_from_api method.
        """
        # Try to load from output file first if it exists and we're not reloading
        if not reload_pipeline and cls.output_dir:
            output_json = cls.output_dir / "filtered_datasets.json"
            if output_json.exists():
                with open(output_json, "r") as f:
                    return json.load(f)

        # Try to load from input file if it exists and we're not reloading
        if not reload_pipeline and cls.input_file and cls.input_file.exists():
            content = cls.fetch_from_file(cls.input_file)
            return content

        # Otherwise fetch from API
        return cls.fetch_from_api()

    @classmethod
    def load_gtfs_files(cls) -> Feed:
        """
        Load all GTFS files from the src/data/transportdatagouv folder

        Returns:
            List of dictionaries containing:
                - feed: The GTFS feed object
                - file_path: The path to the GTFS file
                - dataset_id: The ID of the dataset
        """
        # Find all GTFS zip files in the output directory
        gtfs_files = glob.glob(str(cls.output_dir / "*.zip"))
        logger.info(f"Found {len(gtfs_files)} GTFS files in {cls.output_dir}")

        gtfs_attributes = [
            "stops",
            "trips",
            "routes",
            "stop_times",
            "shapes",
            "agency",
            "calendar",
            "calendar_dates",
            "fare_attributes",
            "fare_rules",
            "frequencies",
            "transfers",
            "feed_info",
            "attributions",
        ]

        resulting_feed = Feed(dist_units="km")
        success_count = 0
        error_count = 0

        for file_path in gtfs_files:
            if cls.test_limit and success_count + error_count >= cls.test_limit:
                logger.info(f"Test limit reached ({cls.test_limit} datasets). Stop loading.")
                break

            file_path = Path(file_path)
            file_name = file_path.name

            # Extract dataset_id from filename (format: date_dataset-id_index.zip)
            try:
                # Parse the filename to extract dataset_id
                parts = file_name.split("_")
                if len(parts) >= 2:
                    dataset_id = parts[1]
                else:
                    dataset_id = "unknown"

                logger.info(f"Loading GTFS file: {file_name} (Dataset ID: {dataset_id})")

                # Load the GTFS feed
                try:
                    feed = gk.read_feed(file_path, dist_units="km")

                    # Basic validation of the feed
                    if hasattr(feed, "stops") and len(feed.stops) > 0:
                        logger.info(
                            f"Successfully loaded {file_name} with {len(feed.stops)} stops and {len(feed.routes) if hasattr(feed, 'routes') else 0} routes"
                        )

                        # Get agency name if available, otherwise use dataset_id
                        agency_name = dataset_id
                        if hasattr(feed, "agency") and not feed.agency.empty:
                            # Use the first agency name as prefix
                            agency_name = (
                                sanitize_name(
                                    feed.agency.iloc[0].get("agency_name", dataset_id)
                                )
                                + "_"
                            )

                        feed = cls.clean_gtfs_feed(feed)
                        # feed = feed.aggregate_stops(stop_id_prefix=agency_name)
                        # feed = feed.aggregate_routes(route_id_prefix=agency_name)

                        for attribute in gtfs_attributes:
                            merge_feed_attribute(resulting_feed, feed, attribute)

                        success_count = success_count + 1
                    else:
                        logger.warning(f"Skipping {file_name}: Feed has no stops")

                except Exception as e:
                    logger.error(f"Error loading GTFS file {file_name}. Error: {e}")
                    error_count = error_count + 1

            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}")
                error_count = error_count + 1

        logger.info(
            f"Successfully loaded {success_count} GTFS feeds. {error_count} errors encountered."
        )
        return resulting_feed

    @classmethod
    def clean_gtfs_feed(cls, feed: gk.Feed) -> Feed | None:
        """
        Clean a GTFS feed using gtfs-kit

        Args:
            feed: GTFS feed to clean

        Returns:
            Cleaned GTFS feed
        """
        if feed is None:
            logger.warning("No feed to clean")
            return None

        logger.info("Cleaning GTFS feed")

        try:
            nb_stops = feed.stops
            nb_routes = feed.routes
            nb_trips = feed.trips
            nb_stop_times = feed.stop_times
            # clean ids / times / route_short_names / zombies
            # feed = feed.clean()
            # feed = feed.drop_zombies()
            feed = feed.drop_invalid_columns()
            # TODO
            # Delete schedules in the past
            logger.debug(
                f"Cleaned stops. Remaining stops: {len(feed.stops)} over {len(nb_stops)}"
            )
            logger.debug(
                f"Cleaned routes. Remaining routes: {len(feed.routes)} over {len(nb_routes)}"
            )
            logger.debug(
                f"Cleaned trips. Remaining trips: {len(feed.trips)} over {len(nb_trips)}"
            )
            logger.debug(
                f"Cleaned nb_stop_times. Remaining nb_stop_times: {len(feed.stop_times)} over {len(nb_stop_times)}"
            )

            # Assess Quality
            quality = gk.assess_quality(feed)
            assessment = quality[quality["indicator"] == "assessment"]

            logger.debug(f"Feed quality: {assessment.get('value')}")

            return feed

        except Exception as e:
            logger.error(f"Error cleaning GTFS feed: {e}")
            return feed

    @classmethod
    def save_gtfs_feed_parquet(cls, feed: gk.Feed, output_path: Path) -> None:
        """
        Save a GTFS feed to a parquet file

        Args:
            feed: GTFS feed to save
            output_path: Path to save the feed to
        """
        logger.info(f"Saving GTFS feed to {output_path}")

        try:
            # Iterate through each attribute of the feed that is a DataFrame
            for table_name, df in feed.__dict__.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    try:
                        parquet_path = (
                            output_path.parent / f"{output_path.stem}_{table_name}.parquet"
                        )
                        df.to_parquet(parquet_path)
                        logger.info(
                            f"Successfully saved {table_name} as dataframe to {parquet_path}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error saving geo dataframe to {output_path.with_suffix('.parquet')}: {e}"
                        )

        except Exception as e:
            logger.error(f"Error saving GTFS feed to {output_path}: {e}")

    @classmethod
    def save_gtfs_feed_gtfs(cls, feed: gk.Feed, output_path: Path) -> None:
        """
        Save a GTFS feed to a zip file in the GTFS format

        Args:
            feed: GTFS feed to save
            output_path: Path to save the feed to
        """
        logger.info(f"Saving GTFS feed to {output_path}")

        try:
            # Save the feed to a zip file
            with zipfile.ZipFile(output_path, "w") as zip_file:
                for table_name, df in feed.__dict__.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # Convert DataFrame to CSV and add to zip
                        csv_data = df.to_csv(index=False)
                        zip_file.writestr(f"{table_name}.txt", csv_data)

            logger.info(f"Successfully saved GTFS feed to {output_path}")

        except Exception as e:
            logger.error(f"Error saving GTFS feed to {output_path}: {e}")

    @classmethod
    def save(cls, feed: gk.Feed, output_path: Path) -> None:
        super().save(gk.Feed, output_path)
        logger.info(f"Saving GTFS feed to {output_path} to {cls.save_method} format")

        if feed is None:
            logger.warning("No feed to save")
            return None

        if cls.save_method == cls.SaveMethod.PARQUET:
            cls.save_gtfs_feed_parquet(feed, output_path)
            return None
        elif cls.save_method == cls.SaveMethod.GTFS:
            cls.save_gtfs_feed_gtfs(feed, output_path)
            return None
        else:
            logger.error("Invalid save method")
            return None

    @classmethod
    def run(cls, reload_pipeline: bool = False) -> None:
        """Run the processor to download GTFS data"""
        # Create output directory if it doesn't exist
        cls.output_dir.mkdir(parents=True, exist_ok=True)

        # Fetch datasets
        datasets = cls.fetch(reload_pipeline=reload_pipeline)

        # Filter datasets
        filtered_datasets = cls.pre_process(datasets)

        # Save filtered datasets for future use
        filtered_json = cls.output_dir / "filtered_datasets.json"
        with open(filtered_json, "w") as f:
            json.dump(filtered_datasets, f, indent=2)

        # Download GTFS files
        cls.download_gtfs_files(filtered_datasets)

        logger.info(
            f"Downloaded {sum(len(d.get('resources', [])) for d in filtered_datasets)} GTFS files from {len(filtered_datasets)} datasets"
        )

        # Load GTFS files
        cls.process_gtfs_files()

    @classmethod
    def process_gtfs_files(cls) -> None:
        """
        Process GTFS files without downloading new data.
        This method:
        1. Loads all GTFS files from the data/transportdatagouv folder
        2. Merges the GTFS data with appropriate prefixes
        3. Cleans the merged data using gtfs-kit
        4. Saves the cleaned and merged GTFS data as a zip file
        5. Saves the stops as a geo dataframe in parquet format
        """
        # Create output directory if it doesn't exist
        cls.output_dir.mkdir(parents=True, exist_ok=True)

        # Load GTFS files
        loaded_feeds = cls.load_gtfs_files()

        if loaded_feeds:
            # Clean merged GTFS feed
            cleaned_feed = cls.clean_gtfs_feed(loaded_feeds)

            # Save cleaned GTFS feed
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_prefix}_merged_cleaned_gtfs.zip"
            output_path = cls.output_dir / filename
            cls.save(cleaned_feed, output_path)

            logger.info("GTFS processing complete")
        else:
            logger.warning("No GTFS files found to process")


def main(**kwargs):
    TransportDataGouvProcessor.save_method = TransportDataGouvProcessor.SaveMethod.GTFS
    TransportDataGouvProcessor.test_limit = 5

    # Choose which operation to run
    if "operation" in kwargs and kwargs["operation"] == "process":
        # Only process existing GTFS files
        logger.info("Running GTFS processing only")
        TransportDataGouvProcessor.process_gtfs_files()
    else:
        # Run the full pipeline
        logger.info("Running full pipeline (download and process)")
        TransportDataGouvProcessor.run(reload_pipeline=True)


if __name__ == "__main__":
    # Set up logger
    setup_logger()
    main(operation="process")
