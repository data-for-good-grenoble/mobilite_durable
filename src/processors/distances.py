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
    max_distance_threshold = 5_000

    # Margin for Euclidean approximation filtering (in meters)
    # Euclidean distance is shorter than geodesic, so we add margin to avoid false negatives
    euclidean_margin = 30

    # Size of the batch of distances computed by each thread
    batch_size = 10_000

    # Maximum number of threads to use to compute distances
    max_workers = 10

    # Columns to keep to identify bus stops
    bus_stop_columns = ["osm_id", "gtfs_id", "navitia_id"]

    @classmethod
    def fetch_from_api(cls, **kwargs) -> pd.DataFrame:
        """Fetch data from API, in this case compute distances between bus stops and activities.

        Variables in kwargs:
        - keep_old_distances (bool): if True, keep old distances from the existing output file and only compute new distances for new bus stop - activity pairs. If false, computed all the bus stop - activity pairs.
        - latitude_grouping_precision (float): the precision for grouping activities by latitude. Latitude values are cut to this precision to group actitvities in the same groupes at each running. Creating groups reduce memory usage.
        """
        keep_old_distances = kwargs.pop("keep_old_distances", False)
        latitude_grouping_precision = kwargs.pop("latitude_grouping_precision", 0.1)
        return cls._fetch_from_api(keep_old_distances, latitude_grouping_precision)

    @classmethod
    def _fetch_from_api(
        cls,
        keep_old_distances: bool,
        latitude_grouping_precision: float,
    ) -> pd.DataFrame:
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
        area_activity_gdf = cls._get_area_activities(
            area_gdf, latitude_grouping_precision
        ).rename(columns={"geometry": "activity_geometry"})
        logger.info(
            f"Number of activities in the {len(cls.area_codes)} areas: {len(area_activity_gdf)}"
        )

        # Compute cross product of bus stops and activities for a group of actitivities
        for activity_latitude_index in area_activity_gdf["latitude_index"].unique():
            logger.info(f"Processing activity latitude index {activity_latitude_index}...")
            activity_subset_gdf = area_activity_gdf[
                area_activity_gdf["latitude_index"] == activity_latitude_index
            ]
            cross_df = area_bus_stops_gdf.reset_index(drop=True).merge(
                activity_subset_gdf.reset_index(drop=True),
                how="cross",
            )
            logger.info(
                f"Number of bus stop - activity pairs to compute distances for: {len(cross_df)}"
            )

            # Merge with old distances to avoid recomputing them
            part_path = cls._get_distance_part_path(activity_latitude_index)
            if keep_old_distances and part_path is not None and part_path.exists():
                logger.info(f"Loading old distances from {part_path} to avoid recomputation...")
                old_distances_df = cls.fetch_from_file(part_path)
                if "computed" not in old_distances_df.columns:
                    old_distances_df["computed"] = ~pd.isna(old_distances_df["distance_m"])
                cross_df = cross_df.merge(
                    old_distances_df,
                    on=cls.bus_stop_columns + ["Id wp"],
                    how="left",
                    suffixes=("", "_old"),
                )
                cross_df["computed"] = cross_df["computed"].fillna(False).astype(bool)
                logger.info(
                    f"Number of already computed distances: {cross_df['computed'].sum()}"
                )
                logger.info(f"Number of distances to compute: {(~cross_df['computed']).sum()}")
            else:
                cross_df["computed"] = False

            # Calculate distances using the API
            with concurrent.futures.ThreadPoolExecutor(max_workers=cls.max_workers) as executor:
                non_computed_indices = list(cross_df.index[~cross_df["computed"]])

                for batch_id in tqdm(
                    range(0, len(non_computed_indices), cls.batch_size),
                    total=(len(non_computed_indices) + cls.batch_size - 1) // cls.batch_size,
                    desc="Submitting distance computations",
                ):
                    batch_indices = non_computed_indices[batch_id : batch_id + cls.batch_size]
                    futures = {
                        executor.submit(
                            cls._compute_distance_and_manage_errors, cross_df.loc[i]
                        ): i
                        for i in batch_indices
                    }
                    for future in concurrent.futures.as_completed(futures):
                        i = futures[future]
                        (
                            cross_df.at[i, "distance_m"],
                            cross_df.at[i, "computed"],
                        ) = future.result()
            cls.save(
                cross_df.loc[:, cls.bus_stop_columns + ["Id wp", "distance_m", "computed"]],
                part_path,
            )
            logger.info(
                f"Saved distances for activity latitude index {activity_latitude_index} to {part_path}"
            )

        # Merge the different parts and keep only computed distances
        distance_parts = []
        for activity_latitude_index in area_activity_gdf["latitude_index"].unique():
            part_path = cls._get_distance_part_path(activity_latitude_index)
            if part_path.exists():
                distance_df = cls.fetch_from_file(part_path)
                distance_parts.append(distance_df[distance_df["computed"]])
        return pd.concat(distance_parts, ignore_index=True)

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        return pd.read_parquet(path)

    @classmethod
    def save(cls, content: pd.DataFrame, path: Path, **kwargs) -> None:
        content.to_parquet(path)

    @classmethod
    def _get_area_activities(
        cls, area_gdf: gpd.GeoDataFrame, latitude_grouping_precision: float
    ) -> gpd.GeoDataFrame:
        activity_gdf = gpd.read_parquet(DATA_FOLDER / "C2C/depart_topos_stops_isere.parquet")
        activity_gdf = activity_gdf.rename(
            columns={
                "navitia_id": "Id wp",
                "name": "Name wp",
                "nombre_de_depart_de_topo": "nbr_topo",
            }
        )
        logger.info(f"Number of activities before filtering by area: {len(activity_gdf)}")
        valid_ids = gpd.sjoin(
            activity_gdf.to_crs(EPSG_WGS84),
            area_gdf[area_gdf["code"].isin(cls.area_codes)].to_crs(EPSG_WGS84),
        )["Id wp"].drop_duplicates()
        area_activity_gdf = activity_gdf[activity_gdf["Id wp"].isin(valid_ids)]
        logger.info(f"Number of activities after filtering by area: {len(area_activity_gdf)}")
        area_activity_gdf["latitude_index"] = (
            activity_gdf["geometry"].y / latitude_grouping_precision
        ).astype(int)
        return area_activity_gdf

    @classmethod
    def _get_bus_stops(cls, area_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        bus_stop_columns = cls.bus_stop_columns + ["geometry"]
        # TODO Add parameter to choose the geographic scope of OSM bus stops
        osm_stops_gdf = AURAOSMBusStopsProcessor.fetch(reload_pipeline=False)[bus_stop_columns]
        if osm_stops_gdf is None or osm_stops_gdf.empty:
            err_msg = "No OSM bus stops found, please process AURA OSM bus stops first."
            raise ValueError(err_msg)
        logger.info(f"Number of OSM bus stops before filtering by area: {len(osm_stops_gdf)}")
        valid_osm_ids = gpd.sjoin(
            osm_stops_gdf,
            area_gdf[area_gdf["code"].isin(cls.area_codes)].to_crs(EPSG_WGS84),
        )["osm_id"].drop_duplicates()
        osm_stops_gdf = osm_stops_gdf[osm_stops_gdf["osm_id"].isin(valid_osm_ids)]
        logger.info(f"Number of OSM bus stops after filtering by area: {len(osm_stops_gdf)}")
        c2c_stops_gdf = C2CBusStopsProcessor.fetch(reload_pipeline=False)[bus_stop_columns]
        logger.info(f"Number of C2C bus stops before filtering by area: {len(c2c_stops_gdf)}")
        if c2c_stops_gdf is None or c2c_stops_gdf.empty:
            err_msg = "No C2C bus stops found, please process C2C bus stops first."
            raise ValueError(err_msg)
        valid_navitia_ids = gpd.sjoin(
            c2c_stops_gdf.to_crs(EPSG_WGS84),
            area_gdf[area_gdf["code"].isin(cls.area_codes)].to_crs(EPSG_WGS84),
        )["navitia_id"].drop_duplicates()
        c2c_stops_gdf = c2c_stops_gdf[c2c_stops_gdf["navitia_id"].isin(valid_navitia_ids)]
        logger.info(f"Number of C2C bus stops after filtering by area: {len(c2c_stops_gdf)}")
        tdg_stop_list = []
        for area_code in cls.area_codes:
            tdg_file = DATA_FOLDER / f"transportdatagouv/stops_{area_code}.parquet"
            if not tdg_file.exists():
                err_msg = f"No TransportDataGouv bus stops found for area code {area_code}, please process it first."
                raise ValueError(err_msg)
            tdg_stop_list.append(gpd.read_parquet(tdg_file))
        tdg_stops_gdf = pd.concat(tdg_stop_list, ignore_index=True)
        logger.info(f"Number of TDG bus stops after filtering by area: {len(tdg_stops_gdf)}")
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
    def _get_distance_part_path(cls, activity_latitude_index: int) -> Path:
        return (
            cls.output_dir
            / f"bus_stops_to_activities_distances_latitude_index_{activity_latitude_index}.parquet"
        )

    @classmethod
    def _compute_distance_and_manage_errors(cls, row: pd.Series) -> tuple[float, bool]:
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
    logger.info("Computing distances from bus stops to activities...")
    DistancesProcessor.run(reload_pipeline=True, fetch_api_kwargs={"keep_old_distances": True})


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)
    main()
