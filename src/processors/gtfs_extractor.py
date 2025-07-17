"""
Module for GTFS data extraction and processing.

This module provides classes for extracting and processing GTFS (General Transit
Feed Specification) data, including stops, lines, and export functionality.

Author: Laurent Sorba

References:
    https://github.com/data-for-good-grenoble/mobilite_durable/issues/8
    https://github.com/data-for-good-grenoble/mobilite_durable/issues/9

Classes:
    GTFSExtractor: Base class for GTFS data extraction
    GTFSStopsExtractor: Extracts stop information from GTFS feeds
    GTFSLinesExtractor: Extracts line information from GTFS feeds
    GTFExporter: Exports processed GTFS data to various formats: CSV or GeoJSON

Example:
    # Extract stops from a folder containing multiple GTFS files
    stops_df = extract_gtfs_stops(str(input_dir), str(output_file_stops_csv), "csv", with_lines=True)
    stops_df = extract_gtfs_stops(str(input_dir), str(output_file_stops_geojson), "geojson", with_lines=True)

    # Extract lines from a folder containing multiple GTFS files
    lines_df = extract_gtfs_lines(str(input_dir), str(output_file_lines_csv), "csv")
    lines_df = extract_gtfs_lines(str(input_dir), str(output_file_lines_geojson), "geojson")
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import gtfs_kit as gk
import pandas as pd
from pyproj import Transformer
from shapely import Point
from shapely.geometry import LineString, MultiLineString

from src.settings import DATA_FOLDER
from src.utils.logger import setup_logger

# Set up logger
logger = logging.getLogger(__name__)


class GTFSExtractor:
    """Base class for GTFS data extraction with common utilities"""

    def __init__(self, insert_line_info: bool = True):
        self.insert_line_info = insert_line_info

    @staticmethod
    def prepare_feed(feed):
        """Prepare GTFS feed by adding missing optional columns"""
        # Handle missing columns in stops
        if "parent_station" not in feed.stops.columns:
            feed.stops["parent_station"] = None
        if "stop_code" not in feed.stops.columns:
            feed.stops["stop_code"] = None
        if "stop_desc" not in feed.stops.columns:
            feed.stops["stop_desc"] = None

        # Handle missing columns in routes
        if "agency_id" not in feed.routes.columns:
            feed.routes["agency_id"] = None
        if "route_color" not in feed.routes.columns:
            feed.routes["route_color"] = None
        if "route_text_color" not in feed.routes.columns:
            feed.routes["route_text_color"] = None

        return feed

    @staticmethod
    def get_agencies(feed) -> List[Dict]:
        """Get list of agencies from feed"""
        if feed.agency is not None and not feed.agency.empty:
            return feed.agency[["agency_id", "agency_name"]].to_dict("records")
        else:
            return [{"agency_id": "default", "agency_name": "Default Agency"}]

    @staticmethod
    def get_dynamic_columns(
        df: pd.DataFrame, required_cols: List[str], optional_cols: List[str]
    ) -> List[str]:
        """Get columns list based on what's available in the DataFrame"""
        columns = required_cols.copy()
        for col in optional_cols:
            if col in df.columns:
                columns.append(col)
        return columns

    @staticmethod
    def create_unique_id(agency_id: str, item_id: str) -> str:
        """Create unique identifier combining agency and item ID"""
        return f"{agency_id}_{item_id}"

    @staticmethod
    def get_trip_route_mapping(feed) -> pd.DataFrame:
        """Get mapping between trips and routes with line information"""
        trips = feed.trips[["trip_id", "route_id"]]
        routes = feed.routes[["route_id", "route_short_name", "route_long_name"]]
        return trips.merge(routes, on="route_id", how="left")

    @staticmethod
    def safe_list_to_string(lst: Union[List, str, None]) -> str:
        """Safely convert list to comma-separated string"""
        if isinstance(lst, list):
            return ",".join(str(item) for item in lst)
        elif lst is None:
            return ""
        else:
            return str(lst)

    @staticmethod
    def transform_to_web_mercator(lon: float, lat: float) -> tuple:
        """Transform WGS84 coordinates to Web Mercator (EPSG:3857)"""
        try:
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
            x, y = transformer.transform(lon, lat)
            return x, y
        except Exception as e:
            logger.warning(f"Error transforming coordinates: {e}")
            raise ValueError("Invalid coordinates") from e

    @staticmethod
    def safe_concat_dataframes(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """Safely concatenate DataFrames, handling empty ones"""
        non_empty_dfs = [df for df in dataframes if not df.empty]
        if non_empty_dfs:
            return pd.concat(non_empty_dfs, ignore_index=True)
        else:
            return pd.DataFrame()

    @staticmethod
    def find_gtfs_files(folder_path: str) -> List[str]:
        """Find all GTFS files in a folder (zip files or folders containing GTFS files)"""
        gtfs_files = []
        folder_path = Path(folder_path)

        if not folder_path.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return gtfs_files

        # Look for zip files
        zip_files = list(folder_path.glob("*.zip"))
        gtfs_files.extend([str(f) for f in zip_files])

        # Look for folders containing gtfs files (check for stops.txt or routes.txt)
        for item in folder_path.iterdir():
            if item.is_dir():
                if (item / "stops.txt").exists() or (item / "routes.txt").exists():
                    gtfs_files.append(str(item))

        logger.info(f"Found {len(gtfs_files)} GTFS files/folders in {folder_path}")
        return gtfs_files

    @staticmethod
    def clean_stops_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean stops dataframe by removing duplicates and invalid data"""
        if df.empty:
            return df

        logger.info(f"Cleaning stops dataframe with {len(df)} rows")

        # Remove rows with missing essential data
        df_clean = df.dropna(subset=["stop_id", "stop_name", "stop_lat", "stop_lon"])

        # Remove duplicates based on stop_unique_id
        df_clean = df_clean.drop_duplicates(subset=["stop_unique_id"])

        # Remove stops with invalid coordinates
        df_clean = df_clean[
            (df_clean["stop_lat"] >= -90)
            & (df_clean["stop_lat"] <= 90)
            & (df_clean["stop_lon"] >= -180)
            & (df_clean["stop_lon"] <= 180)
        ]

        # Check for missing columns and add them with default values
        for col in GTFSStopsExtractor.stops_cols:
            if col not in df_clean.columns:
                df_clean[col] = None
        df_clean = df_clean[GTFSStopsExtractor.stops_cols]

        logger.info(f"Cleaned stops dataframe: {len(df_clean)} rows remaining")
        return df_clean

    @staticmethod
    def clean_lines_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean lines dataframe by removing duplicates and invalid data"""
        if df.empty:
            return df

        logger.info(f"Cleaning lines dataframe with {len(df)} rows")

        # Remove rows with missing essential data
        df_clean = df.dropna(subset=["route_id", "route_short_name"])

        # Remove duplicates based on line_unique_id
        df_clean = df_clean.drop_duplicates(subset=["line_unique_id"])

        # Remove lines with no geometry or stops
        df_clean = df_clean[(df_clean["geometry"].notna()) & (df_clean["stop_count"] > 0)]

        # Check for missing columns and add them with default values
        for col in GTFSLinesExtractor.lines_cols:
            if col not in df_clean.columns:
                df_clean[col] = None
        df_clean = df_clean[GTFSLinesExtractor.lines_cols]

        logger.info(f"Cleaned lines dataframe: {len(df_clean)} rows remaining")
        return df_clean


class GTFSStopsExtractor(GTFSExtractor):
    """Extractor for GTFS stops with line information"""

    stops_cols = [
        "stop_unique_id",
        "agency_id",
        "agency_name",
        "stop_id",
        "stop_name",
        "stop_code",
        "stop_desc",
        "stop_lat",
        "stop_lon",
        "geometry",
    ]

    def extract_stops(self, agency_id: str, agency_name: str, feed) -> pd.DataFrame:
        """Extract stops for a specific agency with optional line information"""

        # Prepare feed
        feed = self.prepare_feed(feed)

        # Filter feed for specific agency
        try:
            feed_for_agency = feed.restrict_to_agencies({agency_id})
        except Exception as e:
            logger.warning(f"Could not filter feed for agency {agency_id}: {e}")
            feed_for_agency = feed

        # Get dynamic columns for stops
        required_cols = ["stop_id", "stop_name", "stop_lat", "stop_lon"]
        optional_cols = ["stop_code", "stop_desc"]
        stops_columns = self.get_dynamic_columns(
            feed_for_agency.stops, required_cols, optional_cols
        )

        # Extract stops
        stops = feed_for_agency.stops[stops_columns].copy()
        logger.debug(
            f"Extracted {len(stops)} stops from agency '{agency_name}' with id: {agency_id}"
        )

        # Add agency information
        stops.loc[:, "agency_id"] = agency_id
        stops.loc[:, "agency_name"] = agency_name
        stops.loc[:, "stop_unique_id"] = stops["stop_id"].apply(
            lambda x: self.create_unique_id(agency_id, x)
        )

        # Add geometry column (Point in EPSG:3857 - Web Mercator)
        stops.loc[:, "geometry"] = stops.apply(
            lambda row: Point(self.transform_to_web_mercator(row["stop_lon"], row["stop_lat"]))
            if pd.notna(row["stop_lat"]) and pd.notna(row["stop_lon"])
            else None,
            axis=1,
        )

        if not self.insert_line_info:
            return stops

        # Add line information
        stops = self._add_line_info_to_stops(stops, feed_for_agency)

        return stops

    def _add_line_info_to_stops(self, stops: pd.DataFrame, feed) -> pd.DataFrame:
        """Add line information to stops"""

        # Get trip-route mapping
        trip_route = self.get_trip_route_mapping(feed)

        # Get stop_times and merge with trip_route
        stop_times = feed.stop_times[["stop_id", "trip_id"]]
        stop_lines = stop_times.merge(trip_route, on="trip_id", how="left")

        # Remove duplicates to get unique stop-route combinations
        stop_lines = stop_lines.drop_duplicates(subset=["stop_id", "route_id"])

        # Group by stop_id and create line information list
        lines_per_stop = (
            stop_lines.groupby("stop_id")
            .apply(
                lambda x: [
                    {
                        "line_id": row["route_id"],
                        "line_name_short": row["route_short_name"],
                        "line_name_long": row["route_long_name"],
                    }
                    for _, row in x.iterrows()
                ],
                include_groups=False,
            )
            .reset_index()
        )

        lines_per_stop.columns = ["stop_id", "stop_lines"]

        # Merge with stops
        stops = stops.merge(lines_per_stop, on="stop_id", how="left")

        # Fill NaN with empty lists
        stops["stop_lines"] = stops["stop_lines"].apply(
            lambda x: x if isinstance(x, list) else []
        )

        return stops

    @classmethod
    def extract_from_file(cls, gtfs_path: str, with_lines: bool = True) -> pd.DataFrame:
        """Extract all stops from a single GTFS file"""
        extractor = cls(insert_line_info=with_lines)

        try:
            feed = gk.read_feed(gtfs_path, dist_units="km")
            feed = gk.clean(feed)
        except Exception as e:
            logger.error(f"Error reading GTFS file {gtfs_path}: {e}")
            return pd.DataFrame()

        agencies = extractor.get_agencies(feed)
        all_stops = []

        for agency in agencies:
            stops = extractor.extract_stops(agency["agency_id"], agency["agency_name"], feed)
            all_stops.append(stops)

        result = extractor.safe_concat_dataframes(all_stops)
        return extractor.clean_stops_dataframe(result)

    @classmethod
    def extract_from_folder(cls, folder_path: str, with_lines: bool = True) -> pd.DataFrame:
        """Extract all stops from all GTFS files in a folder"""
        gtfs_files = cls.find_gtfs_files(folder_path)

        all_stops = []
        for gtfs_file in gtfs_files:
            logger.info(f"Processing GTFS file: {gtfs_file}")
            stops = cls.extract_from_file(gtfs_file, with_lines)
            if not stops.empty:
                all_stops.append(stops)

        if all_stops:
            result = cls.safe_concat_dataframes(all_stops)
            return cls.clean_stops_dataframe(result)
        else:
            return pd.DataFrame()


class GTFSLinesExtractor(GTFSExtractor):
    """Extractor for GTFS lines with geometry and stop information"""

    lines_cols = [
        "line_unique_id",
        "agency_id",
        "agency_name",
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_type",
        "route_color",
        "route_text_color",
        "geometry",
        "stop_ids",
        "stop_count",
    ]

    def extract_lines(self, agency_id: str, agency_name: str, feed) -> pd.DataFrame:
        """Extract lines for a specific agency with coordinates and stop information"""

        # Prepare feed
        feed = self.prepare_feed(feed)

        # Filter feed for specific agency
        try:
            feed_for_agency = feed.restrict_to_agencies({agency_id})
        except Exception as e:
            logger.warning(f"Could not filter feed for agency {agency_id}: {e}")
            feed_for_agency = feed

        # Get dynamic columns for routes
        required_cols = ["route_id", "route_short_name", "route_long_name", "route_type"]
        optional_cols = ["route_color", "route_text_color"]
        routes_columns = self.get_dynamic_columns(
            feed_for_agency.routes, required_cols, optional_cols
        )

        # Extract routes
        routes = feed_for_agency.routes[routes_columns].copy()
        logger.debug(
            f"Extracted {len(routes)} routes from agency '{agency_name}' with id: {agency_id}"
        )

        # Add agency information
        routes.loc[:, "agency_id"] = agency_id
        routes.loc[:, "agency_name"] = agency_name
        routes.loc[:, "line_unique_id"] = routes["route_id"].apply(
            lambda x: self.create_unique_id(agency_id, x)
        )

        # Process each route to get geometry and stops
        lines_data = []

        for _, route in routes.iterrows():
            line_data = self._process_route_geometry(route, feed_for_agency)
            if line_data:
                lines_data.append(line_data)

        lines_df = pd.DataFrame(lines_data)
        logger.debug(f"Processed {len(lines_df)} lines from agency '{agency_name}'")

        return lines_df

    def _process_route_geometry(self, route: pd.Series, feed) -> Optional[Dict]:
        """Process a single route to extract geometry and stop information"""
        route_id = route["route_id"]

        # Get trips for this route
        route_trips = feed.trips[feed.trips["route_id"] == route_id]
        if route_trips.empty:
            return None

        # Get stop_times for these trips
        trip_ids = route_trips["trip_id"].tolist()
        route_stop_times = feed.stop_times[feed.stop_times["trip_id"].isin(trip_ids)].copy()

        if route_stop_times.empty:
            return None

        # Sort by trip_id and stop_sequence
        route_stop_times = route_stop_times.sort_values(["trip_id", "stop_sequence"])

        # Get stop information
        stop_ids = route_stop_times["stop_id"].unique().tolist()
        route_stops = feed.stops[feed.stops["stop_id"].isin(stop_ids)].copy()

        # Merge to get coordinates
        route_stop_times = route_stop_times.merge(
            route_stops[["stop_id", "stop_lat", "stop_lon", "stop_name"]],
            on="stop_id",
            how="left",
        )

        # Create geometry
        geometry = self._create_route_geometry(route_stop_times, trip_ids)

        # Prepare line data
        line_data = {
            "line_unique_id": route["line_unique_id"],
            "route_id": route_id,
            "route_short_name": route["route_short_name"],
            "route_long_name": route["route_long_name"],
            "route_type": route["route_type"],
            "agency_id": route["agency_id"],
            "agency_name": route["agency_name"],
            "geometry": geometry,
            "stop_ids": stop_ids,
            "stop_count": len(stop_ids),
        }

        # Add optional fields
        for col in ["route_color", "route_text_color"]:
            if col in route.index and pd.notna(route[col]):
                line_data[col] = route[col]

        return line_data

    def _create_route_geometry(
        self, route_stop_times: pd.DataFrame, trip_ids: List[str]
    ) -> Optional[Union[LineString, MultiLineString]]:
        """Create geometry for a route from trip stop times"""
        trip_geometries = []

        for trip_id in trip_ids:
            trip_stops = route_stop_times[route_stop_times["trip_id"] == trip_id].sort_values(
                "stop_sequence"
            )

            if len(trip_stops) >= 2:
                coordinates = [
                    self.transform_to_web_mercator(row["stop_lon"], row["stop_lat"])
                    for _, row in trip_stops.iterrows()
                    if pd.notna(row["stop_lat"]) and pd.notna(row["stop_lon"])
                ]

                if len(coordinates) >= 2:
                    trip_geometries.append(LineString(coordinates))

        # Create geometry
        if trip_geometries:
            if len(trip_geometries) == 1:
                return trip_geometries[0]
            else:
                return MultiLineString(trip_geometries)

        return None

    @classmethod
    def extract_from_file(cls, gtfs_path: str) -> pd.DataFrame:
        """Extract all lines from a single GTFS file"""
        extractor = cls()

        try:
            feed = gk.read_feed(gtfs_path, dist_units="km")
            feed = gk.clean(feed)
        except Exception as e:
            logger.error(f"Error reading GTFS file {gtfs_path}: {e}")
            return pd.DataFrame()

        agencies = extractor.get_agencies(feed)
        all_lines = []

        for agency in agencies:
            lines = extractor.extract_lines(agency["agency_id"], agency["agency_name"], feed)
            all_lines.append(lines)

        result = extractor.safe_concat_dataframes(all_lines)
        return extractor.clean_lines_dataframe(result)

    @classmethod
    def extract_from_folder(cls, folder_path: str) -> pd.DataFrame:
        """Extract all lines from all GTFS files in a folder"""
        gtfs_files = cls.find_gtfs_files(folder_path)

        all_lines = []
        for gtfs_file in gtfs_files:
            logger.info(f"Processing GTFS file: {gtfs_file}")
            lines = cls.extract_from_file(gtfs_file)
            if not lines.empty:
                all_lines.append(lines)

        if all_lines:
            result = cls.safe_concat_dataframes(all_lines)
            return cls.clean_lines_dataframe(result)
        else:
            return pd.DataFrame()


class GTFSExporter:
    """Utility class for exporting GTFS data to various formats"""

    @staticmethod
    def to_csv(df: pd.DataFrame, output_path: str, geometry_col: str = "geometry"):
        """Export DataFrame to CSV with proper handling of geometry and lists"""
        csv_export = df.copy()

        # Handle geometry column
        if geometry_col in csv_export.columns:
            csv_export[f"{geometry_col}_wkt"] = csv_export[geometry_col].apply(
                lambda geom: geom.wkt if geom is not None else None
            )
            csv_export = csv_export.drop(geometry_col, axis=1)

        # Handle list columns
        for col in csv_export.columns:
            if csv_export[col].dtype == "object":
                csv_export[col] = csv_export[col].apply(GTFSExtractor.safe_list_to_string)

        csv_export.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"Data saved to {output_path}")

        return csv_export

    @staticmethod
    def to_geojson(
        df: pd.DataFrame,
        output_path: str,
        geometry_col: str = "geometry",
        crs: str = "EPSG:3857",
    ):
        """Export DataFrame to GeoJSON"""
        try:
            import geopandas as gpd

            # Filter rows with geometry
            df_with_geometry = df[df[geometry_col].notna()].copy()

            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(df_with_geometry, geometry=geometry_col, crs=crs)

            # Handle list columns for GeoJSON
            for col in gdf.columns:
                if col != geometry_col and gdf[col].dtype == "object":
                    gdf[col] = gdf[col].apply(GTFSExtractor.safe_list_to_string)

            gdf.to_file(output_path, driver="GeoJSON")
            logger.info(f"Data saved to {output_path}")

        except ImportError:
            logger.error("geopandas not installed, cannot save to GeoJSON")


# Convenience functions for backward compatibility and easy usage
def extract_gtfs_stops(
    gtfs_path: str, output_path: str = None, output_format: str = "csv", with_lines: bool = True
) -> pd.DataFrame:
    """Extract stops from GTFS file or folder"""
    if os.path.isdir(gtfs_path):
        stops = GTFSStopsExtractor.extract_from_folder(gtfs_path, with_lines)
    else:
        stops = GTFSStopsExtractor.extract_from_file(gtfs_path, with_lines)

    if output_path and not stops.empty:
        if output_format.lower() == "csv":
            GTFSExporter.to_csv(stops, output_path)
        elif output_format.lower() == "geojson":
            GTFSExporter.to_geojson(stops, output_path)

    return stops


def extract_gtfs_lines(
    gtfs_path: str, output_path: str = None, output_format: str = "csv"
) -> pd.DataFrame:
    """Extract lines from GTFS file or folder"""
    if os.path.isdir(gtfs_path):
        lines = GTFSLinesExtractor.extract_from_folder(gtfs_path)
    else:
        lines = GTFSLinesExtractor.extract_from_file(gtfs_path)

    if output_path and not lines.empty:
        if output_format.lower() == "csv":
            GTFSExporter.to_csv(lines, output_path)
        elif output_format.lower() == "geojson":
            GTFSExporter.to_geojson(lines, output_path)

    return lines


def main(**kwargs):
    logger.info("Running stop and line extractors...")

    # Define paths
    current_date = datetime.now().strftime("%Y-%m-%d")
    input_dir = DATA_FOLDER / "transportdatagouv"
    output_file_stops_csv = input_dir / f"{current_date}_all_stops.csv"
    output_file_lines_csv = input_dir / f"{current_date}_all_lines.csv"
    output_file_stops_geojson = input_dir / f"{current_date}_all_stops.geojson"
    output_file_lines_geojson = input_dir / f"{current_date}_all_lines.geojson"

    # Extract stops from a folder containing multiple GTFS files
    stops_df = extract_gtfs_stops(
        str(input_dir), str(output_file_stops_csv), "csv", with_lines=True
    )
    # stops_df = extract_gtfs_stops(str(input_dir), str(output_file_stops_geojson), "geojson", with_lines=True)

    # Extract lines from a folder containing multiple GTFS files
    lines_df = extract_gtfs_lines(str(input_dir), str(output_file_lines_csv), "csv")
    # lines_df = extract_gtfs_lines(str(input_dir), str(output_file_lines_geojson), "geojson")

    # Using class methods directly
    # stops_df = GTFSStopsExtractor.extract_from_folder(str(input_dir))
    # lines_df = GTFSLinesExtractor.extract_from_folder(str(input_dir))


if __name__ == "__main__":
    # Set up logger
    setup_logger(level=logging.DEBUG)
    main()
    pass
