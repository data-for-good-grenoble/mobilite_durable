"""
This module provides functionality to computing distances using the OpenRouteService API.

Author: Nicolas Grosjean
"""

import concurrent.futures
import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import Geod
from tqdm import tqdm

from src.api.openrouteservice import OpenRouteServiceAPI
from src.processors.c2c import C2CBusStopsProcessor
from src.processors.osm import OSMBusStopsProcessor
from src.settings import DATA_FOLDER, EPSG_WGS84
from src.utils.logger import setup_logger
from src.utils.processor_mixin import ProcessorMixin

# Set up logger
logger = logging.getLogger(__name__)


class DistancesProcessor(ProcessorMixin):
    # Define paths
    input_dir = DATA_FOLDER / "distances"
    output_dir = input_dir
    output_file = output_dir / "bus_stops_to_activities_distances.parquet"

    # API declaration
    api_class: type[OpenRouteServiceAPI] = OpenRouteServiceAPI

    # Activity delimitation
    area_code = "38"

    # Threshold to not compute distance between too far points (in meters)
    max_distance_threshold = 5000

    # Columns to keep to identify bus stops
    bus_stop_columns = ["osm_id", "gtfs_id", "navitia_id"]

    # Geod object for distance calculations
    geod = Geod(ellps="WGS84")

    @classmethod
    def fetch_from_api(cls, **kwargs) -> pd.DataFrame:
        # Get bus stops and activities in the area
        area_bus_stops_gdf = cls._get_bus_stops().rename(
            columns={"geometry": "bus_stop_geometry"}
        )
        area_activity_gdf = cls._get_area_activities().rename(
            columns={"geometry": "activity_geometry"}
        )

        # Compute cross product of bus stops and activities
        cross_df = area_bus_stops_gdf.reset_index(drop=True).merge(
            area_activity_gdf.reset_index(drop=True),
            how="cross",
        )

        # Calculate distances using the API
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for batch_id in tqdm(
                range(0, len(cross_df), 1000),
                total=(len(cross_df) + 999) // 1000,
                desc="Submitting distance computations",
            ):
                batch_df = cross_df.iloc[batch_id : batch_id + 1000]
                futures = {
                    executor.submit(cls._compute_distance, batch_df.iloc[i]): batch_id + i
                    for i in range(len(batch_df))
                }
                for future in concurrent.futures.as_completed(futures):
                    i = futures[future]
                    cross_df.at[i, "distance_m"] = future.result()
        return cross_df[cls.bus_stop_columns + ["Id wp", "distance_m"]]

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        return pd.read_parquet(path)

    @classmethod
    def save(cls, content: pd.DataFrame, path: Path, **kwargs) -> None:
        content.to_parquet(path)

    @classmethod
    def _get_area_activities(cls) -> gpd.GeoDataFrame:
        area_gdf = gpd.read_file(
            DATA_FOLDER / "transportdatagouv/contour-des-departements.geojson"
        )
        activity_gdf = gpd.read_parquet(DATA_FOLDER / "C2C/depart_topos_stops_isere.parquet")
        activity_gdf.rename(
            columns={
                "navitia_id": "Id wp",
                "name": "Name wp",
                "nombre_de_depart_de_topo": "nbr_topo",
            },
            inplace=True,
        )
        area_activity_df = (
            gpd.sjoin(
                activity_gdf.to_crs(EPSG_WGS84),
                area_gdf[area_gdf["code"] == cls.area_code].to_crs(EPSG_WGS84),
            )
            .loc[:, ["Id wp"]]
            .drop_duplicates()
            .merge(activity_gdf, on="Id wp", how="inner")
        )
        area_activity_gdf = gpd.GeoDataFrame(area_activity_df, geometry="geometry").set_crs(
            EPSG_WGS84
        )
        return area_activity_gdf

    @classmethod
    def _get_bus_stops(cls) -> gpd.GeoDataFrame:
        bus_stop_columns = cls.bus_stop_columns + ["geometry"]
        # TODO Remove set_crs when new data were computed
        osm_stops_gdf = OSMBusStopsProcessor.fetch(reload_pipeline=False).set_crs(EPSG_WGS84)[
            bus_stop_columns
        ]
        c2c_stops_gdf = C2CBusStopsProcessor.fetch(reload_pipeline=False)[bus_stop_columns]
        tdg_stops_gdf = gpd.read_parquet(DATA_FOLDER / "transportdatagouv/stops_38.parquet")
        tdg_stops_gdf.columns = [
            "network_gtfs_id",
            "network",
            "gtfs_id",
            "name",
            "stop_code",
            "description",
            "line_gtfs_ids",
            "geometry",
        ]
        tdg_stops_gdf["osm_id"] = None
        tdg_stops_gdf["navitia_id"] = None
        tdg_stops_gdf = tdg_stops_gdf[bus_stop_columns]
        return pd.concat(
            (osm_stops_gdf, tdg_stops_gdf.to_crs(EPSG_WGS84), c2c_stops_gdf.to_crs(EPSG_WGS84))
        )

    @classmethod
    def _compute_distance(cls, row: pd.Series) -> float | None:
        _, _, straight_distance = cls.geod.inv(
            row["bus_stop_geometry"].x,
            row["bus_stop_geometry"].y,
            row["activity_geometry"].x,
            row["activity_geometry"].y,
        )
        if straight_distance > cls.max_distance_threshold:
            return None
        start_coords = (
            row["bus_stop_geometry"].y,
            row["bus_stop_geometry"].x,
        )
        end_coords = (
            row["activity_geometry"].y,
            row["activity_geometry"].x,
        )
        try:
            distance = cls.api_class.compute_distance(start_coords, end_coords)
            return distance
        except Exception as e:
            logger.error(f"Error computing distance for row {row.name}: {e}")
            return None


def main(**kwargs):
    reload_pipeline = True
    logger.info("Computing distances from bus stops to activities...")
    DistancesProcessor.run(reload_pipeline)


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)
    main()
