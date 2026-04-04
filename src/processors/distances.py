"""
This module provides functionality to computing distances using the OpenRouteService API.

Author: Nicolas Grosjean
"""

import concurrent.futures
import logging
from math import cos, radians
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from tqdm import tqdm

from src.api.openrouteservice import OpenRouteServiceAPI
from src.processors.c2c import C2CBusStopsProcessor
from src.processors.osm import AURAOSMBusStopsProcessor
from src.settings import DATA_FOLDER, EPSG_WGS84
from src.utils.logger import setup_logger
from src.utils.processor_mixin import ProcessorMixin

# Set up logger
logger = logging.getLogger(__name__)


class TooFarError(Exception):
    """Custom exception to indicate that two points are too far to be interesting to compute distance."""

    pass


class DistancesProcessor(ProcessorMixin):
    # Define paths
    input_dir = DATA_FOLDER / "distances"
    output_dir = input_dir
    output_file = output_dir / "bus_stops_to_activities_distances.parquet"

    # API declaration
    api_class: type[OpenRouteServiceAPI] = OpenRouteServiceAPI

    # Data delimitation
    area_codes = ["38", "73", "74"]  # Isère, Savoie, Haute-Savoie

    # Threshold to not compute distance between too far points (in meters)
    max_distance_threshold = 5000

    # Margin for Euclidean approximation filtering (in meters)
    # Euclidean distance is shorter than geodesic, so we add margin to avoid false negatives
    euclidean_margin = 30

    # Size of the batch of distances computed by each thread
    batch_size = 10000

    # Maximum number of threads to use to compute distances
    max_workers = 10

    # Columns to keep to identify bus stops
    bus_stop_columns = ["osm_id", "gtfs_id", "navitia_id"]

    @classmethod
    def fetch_from_api(cls, **kwargs) -> pd.DataFrame:
        keep_old_distances = kwargs.pop("keep_old_distances", False)

        # Load department limits to filter data in the area of interest
        area_gdf = gpd.read_file(
            DATA_FOLDER / "transportdatagouv/contour-des-departements.geojson"
        )

        # Get bus stops and activities in the area
        area_bus_stops_gdf = cls._get_bus_stops(area_gdf).rename(
            columns={"geometry": "bus_stop_geometry"}
        )
        logger.info(
            f"Number of bus stops in the {len(cls.area_codes)} areas: {len(area_bus_stops_gdf)}"
        )
        area_activity_gdf = cls._get_area_activities(area_gdf).rename(
            columns={"geometry": "activity_geometry"}
        )
        logger.info(
            f"Number of activities in the {len(cls.area_codes)} areas: {len(area_activity_gdf)}"
        )

        # Compute cross product of bus stops and activities
        cross_df = area_bus_stops_gdf.reset_index(drop=True).merge(
            area_activity_gdf.reset_index(drop=True),
            how="cross",
        )
        logger.info(
            f"Number of bus stop - activity pairs to compute distances for: {len(cross_df)}"
        )

        # Merge with old distances to avoid recomputing them
        if keep_old_distances and cls.output_file is not None and cls.output_file.exists():
            logger.info(
                f"Loading old distances from {cls.output_file} to avoid recomputation..."
            )
            old_distances_df = cls.fetch_from_file(cls.output_file)
            if "computed" not in old_distances_df.columns:
                old_distances_df["computed"] = ~pd.isna(old_distances_df["distance_m"])
            cross_df = cross_df.merge(
                old_distances_df,
                on=cls.bus_stop_columns + ["Id wp"],
                how="left",
                suffixes=("", "_old"),
            )
            cross_df["computed"] = cross_df["computed"].fillna(False).astype(bool)
            logger.info(f"Number of already computed distances: {cross_df['computed'].sum()}")
            logger.info(f"Number of distances to compute: {(~cross_df['computed']).sum()}")
        else:
            cross_df["computed"] = False

        # Calculate distances using the API
        with concurrent.futures.ThreadPoolExecutor(max_workers=cls.max_workers) as executor:
            for batch_id in tqdm(
                range(0, len(cross_df), cls.batch_size),
                total=(len(cross_df) + cls.batch_size - 1) // cls.batch_size,
                desc="Submitting distance computations",
            ):
                batch_df = cross_df.iloc[batch_id : batch_id + cls.batch_size]
                futures = {
                    executor.submit(
                        cls._compute_distance_if_not_already_computed, batch_df.iloc[i]
                    ): batch_id + i
                    for i in range(len(batch_df))
                }
                for future in concurrent.futures.as_completed(futures):
                    i = futures[future]
                    cross_df.at[i, "distance_m"], cross_df.at[i, "computed"] = future.result()
        return cross_df.loc[:, cls.bus_stop_columns + ["Id wp", "distance_m", "computed"]]

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        return pd.read_parquet(path)

    @classmethod
    def save(cls, content: pd.DataFrame, path: Path, **kwargs) -> None:
        content.to_parquet(path)

    @classmethod
    def _get_area_activities(cls, area_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        activity_gdf = gpd.read_parquet(DATA_FOLDER / "C2C/depart_topos_stops_isere.parquet")
        activity_gdf = activity_gdf.rename(
            columns={
                "navitia_id": "Id wp",
                "name": "Name wp",
                "nombre_de_depart_de_topo": "nbr_topo",
            }
        )
        area_activity_df = (
            gpd.sjoin(
                activity_gdf.to_crs(EPSG_WGS84),
                area_gdf[area_gdf["code"].isin(cls.area_codes)].to_crs(EPSG_WGS84),
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
    def _get_bus_stops(cls, area_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        bus_stop_columns = cls.bus_stop_columns + ["geometry"]
        osm_stops_gdf = AURAOSMBusStopsProcessor.fetch(reload_pipeline=False)[bus_stop_columns]
        if osm_stops_gdf is None or osm_stops_gdf.empty:
            err_msg = "No OSM bus stops found, please process AURA OSM bus stops first."
            raise ValueError(err_msg)
        osm_stops_gdf = (
            gpd.sjoin(
                osm_stops_gdf,
                area_gdf[area_gdf["code"].isin(cls.area_codes)].to_crs(EPSG_WGS84),
            )
            .loc[:, ["osm_id"]]
            .drop_duplicates()
            .merge(osm_stops_gdf, on="osm_id", how="inner")
        )
        c2c_stops_gdf = C2CBusStopsProcessor.fetch(reload_pipeline=False)[bus_stop_columns]
        if c2c_stops_gdf is None or c2c_stops_gdf.empty:
            err_msg = "No C2C bus stops found, please process C2C bus stops first."
            raise ValueError(err_msg)
        tdg_stop_list = []
        for area_code in cls.area_codes:
            tdg_file = DATA_FOLDER / f"transportdatagouv/stops_{area_code}.parquet"
            if not tdg_file.exists():
                err_msg = f"No TransportDataGouv bus stops found for area code {area_code}, please process it first."
                raise ValueError(err_msg)
            tdg_stop_list.append(gpd.read_parquet(tdg_file))
        tdg_stops_gdf = pd.concat(tdg_stop_list, ignore_index=True)
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
    def _compute_distance_if_not_already_computed(cls, row: pd.Series) -> tuple[float, bool]:
        if row["computed"]:
            return row["distance_m"], True
        try:
            return cls._compute_distance(row), True
        except TooFarError:
            return np.nan, True
        except Exception as e:
            logger.error(f"Error computing distance for row {row.name}: {e}")
            return np.nan, False

    @classmethod
    def _compute_distance(cls, row: pd.Series) -> float:
        # Use fast Euclidean approximation with margin to filter distant points
        straight_distance = cls._square_euclidean_distance(
            row["bus_stop_geometry"].x,
            row["bus_stop_geometry"].y,
            row["activity_geometry"].x,
            row["activity_geometry"].y,
        )
        if straight_distance > (cls.max_distance_threshold + cls.euclidean_margin) ** 2:
            raise TooFarError()
        start_coords = (
            row["bus_stop_geometry"].x,
            row["bus_stop_geometry"].y,
        )
        end_coords = (
            row["activity_geometry"].x,
            row["activity_geometry"].y,
        )
        return cls.api_class.compute_distance(start_coords, end_coords)

    @classmethod
    def _square_euclidean_distance(
        cls, lon1: float, lat1: float, lon2: float, lat2: float
    ) -> float:
        """Calculate approximate distance using Euclidean formula.

        Fast approximation for geographic distances. Accurate enough for small distances (<10km).
        """
        dlat = (lat2 - lat1) * 111320  # meters per degree latitude
        dlon = (lon2 - lon1) * 111320 * cos(radians(lat1))  # meters per degree longitude
        return dlat**2 + dlon**2


def main(**kwargs):
    reload_pipeline = True
    logger.info("Computing distances from bus stops to activities...")
    DistancesProcessor.run(reload_pipeline, fetch_api_kwargs={"keep_old_distances": True})


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)
    main()
