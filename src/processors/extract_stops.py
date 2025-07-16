import logging
import os
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import gtfs_kit as gk
import pandas as pd

from src.processors.utils import ProcessorMixin
from src.settings import DATA_FOLDER
from src.utils.logger import setup_logger

# Set up logger
logger = logging.getLogger(__name__)


class ExtractStopsProcessor(ProcessorMixin):
    """
    Processor for extracting stop information from GTFS data.

    This class is designed to process GTFS files to extract stop information, including geographic
    coordinates, agency details, and associated line information. It combines data from multiple
    agencies within GTFS feeds and produces a consolidated dataset in CSV format. Additionally, it
    supports transforming the extracted stop data into geospatial formats for further analysis.
    """

    # Define paths
    current_date = datetime.now().strftime("%Y-%m-%d")
    input_dir = DATA_FOLDER / "transportdatagouv"
    output_file = input_dir / f"{current_date}_all_stops.csv"
    output_dir = input_dir

    # Limit to x datasets for testing
    test_limit = None

    # Insert line information
    insert_line_info = True

    # Define the required columns in the desired order
    required_columns = [
        "stop_id",
        "stop_code",
        "stop_desc",
        "stop_name",
        "stop_lat",
        "stop_lon",
        "agency_id",
        "agency_name",
        "line_id",
        "line_name_short",
        "line_name_long",
        "geometry",
    ]

    @classmethod
    def load_gtfs_stops(cls, gtfs_folder):
        """
        Load stops from multiple GTFS files in a folder and combine them into a single DataFrame.

        :param gtfs_folder: Path to the folder containing GTFS files.
        :return: A DataFrame containing stops with agency name and ID.
        """
        all_stops = []
        count = 0

        # Iterate through all GTFS files in the specified folder
        for filename in os.listdir(gtfs_folder):
            if cls.test_limit and count >= cls.test_limit:
                logger.info(
                    f"Test limit reached ({cls.test_limit} datasets). Stopping process."
                )
                break

            if filename.endswith(".zip"):
                gtfs_path = os.path.join(gtfs_folder, filename)
                # Load the GTFS data
                logger.info("Loading GTFS data from " + gtfs_path)
                try:
                    gtfs_feed = gk.read_feed(Path(gtfs_path), dist_units="km")
                    logger.debug(f"\t\tRead feed {gtfs_path}.")

                    # Extract agency information
                    agencies = gtfs_feed.agency[["agency_id", "agency_name"]]
                    logger.debug(f"\t\tRead feed {gtfs_path}. Found {len(agencies)} agencies.")

                    # For each agency in the feed
                    for _, agency in agencies.iterrows():
                        agency_id = agency["agency_id"]
                        agency_name = agency["agency_name"]

                        logger.info(f"\t\tProcess agency '{agency_name}' with id: {agency_id}")
                        feed_for_agent = gtfs_feed.restrict_to_agencies({agency_id})
                        # gtf-kit fails if there is no "parent_station" in the stops

                        stops = cls.extract_stops(agency_id, agency_name, feed_for_agent)
                        stops = cls.uniformise_stops(stops)

                        all_stops.append(stops)
                        logger.info(
                            f"\t\tDone! {len(stops)} stops added from agency '{agency_name}' with id:{agency_id}."
                        )

                    count += 1
                except Exception as e:
                    logger.error(
                        f"\t\tError loading or processing GTFS file {filename}: {e.__class__.__name__}: {e}"
                    )

        # Concatenate all stops into a single DataFrame
        combined_stops = pd.concat(all_stops, ignore_index=True)
        return combined_stops

    @classmethod
    def extract_stops(cls, agency_id, agency_name, feed):
        """Extract stops"""

        # Columns to extract from the stops in the feed
        stops_columns = ["stop_id", "stop_name", "stop_lat", "stop_lon"]
        if "stop_code" in feed.stops.columns:
            stops_columns.insert(1, "stop_code")  # Insert stop_code if it exists
        if "stop_desc" in feed.stops.columns:
            stops_columns.insert(1, "stop_desc")  # Insert stop_desc if it exists

        stops = feed.stops[stops_columns].copy()
        logger.debug(f"\t\tExtract stops from agency '{agency_name}' with id: {agency_id}")

        # Add agency information to stops
        stops.loc[:, "agency_id"] = agency_id
        stops.loc[:, "agency_name"] = agency_name

        if not cls.insert_line_info:
            return stops

        # Extract trips and routes to get line information
        trips = feed.trips[["trip_id", "route_id"]]
        routes = feed.routes[["route_id", "route_short_name", "route_long_name"]]

        # Merge trips with routes to get line information
        trip_route = trips.merge(routes, on="route_id", how="left")
        logger.debug(
            f"\t\tMerge trips with routes for agency '{agency_name}' with id: {agency_id}"
        )

        # For each stop, find the associated lines (trips)
        for stop_id in stops["stop_id"]:
            # Get the trips that serve this stop
            stop_trips = feed.stop_times[feed.stop_times["stop_id"] == stop_id]

            # Check if stop_trips is not empty and contains 'trip_id'
            if not stop_trips.empty and "trip_id" in stop_trips.columns:
                # Get the trip IDs for the stop
                trip_ids = stop_trips["trip_id"].tolist()  # Convert to list

                # Find line information for the trips serving this stop
                line_info = trip_route[trip_route["trip_id"].isin(trip_ids)]

                # If there are associated lines, take the first one (or handle as needed)
                if not line_info.empty:
                    stops.loc[stops["stop_id"] == stop_id, "line_id"] = line_info[
                        "route_id"
                    ].iloc[0]
                    stops.loc[stops["stop_id"] == stop_id, "line_name_short"] = line_info[
                        "route_short_name"
                    ].iloc[0]
                    stops.loc[stops["stop_id"] == stop_id, "line_name_long"] = line_info[
                        "route_long_name"
                    ].iloc[0]

        return stops

    @classmethod
    def run(cls, reload_pipeline: bool = False) -> None:
        """Run the processor to download GTFS data"""

        stops_df = cls.load_gtfs_stops(cls.input_dir)
        # Convert to GeoDataFrame if needed
        gdf = gpd.GeoDataFrame(
            stops_df,
            geometry=gpd.points_from_xy(stops_df.stop_lat, stops_df.stop_lon),
            crs="EPSG:4326",  # WGS84
        )
        # Convert to EPSG:3857 (Web Mercator)
        gdf = gdf.to_crs(epsg=3857)

        # Set pandas options to display all columns
        pd.set_option("display.max_columns", None)  # None means no limit
        pd.set_option("display.expand_frame_repr", False)  # Prevents line breaks in the output
        print(gdf.sample(n=10))

        gdf.to_csv(cls.output_file, index=False)  # mode="a", append
        logger.info(f"Saved {len(gdf)} stops to CSV.")

    @classmethod
    def uniformise_stops(cls, df):
        # Check for missing columns and add them with default values
        for col in cls.required_columns:
            if col not in df.columns:
                df[col] = None

        # Reorder the DataFrame to match the required column order
        return df[cls.required_columns]


def main(**kwargs):
    logger.info("Running full pipeline (extract stops)")
    ExtractStopsProcessor.run(reload_pipeline=False)


if __name__ == "__main__":
    # Set up logger
    setup_logger(level=logging.DEBUG)
    ExtractStopsProcessor.test_limit = 5  # Defaults to None
    ExtractStopsProcessor.insert_line_info = False  # Defaults to True
    main()
