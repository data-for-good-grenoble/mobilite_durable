import binascii
import logging
import re
import struct
import tempfile
import zipfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Pattern

import geopandas as gpd
import pandas as pd
from pydantic import ValidationError
from shapely.geometry import Point

from models.bus_stop import BusStop
from src.settings import DATA_FOLDER
from src.utils.processor_mixin import ProcessorMixin
from utils.logger import setup_logger

# Set up logger
logger = logging.getLogger(__name__)


class C2cItiProcessor(ProcessorMixin):
    input_dir = DATA_FOLDER / "C2C"
    input_file = input_dir / "Liste_iti_D4G_isere.csv"
    output_dir = input_dir
    output_file = output_dir / "Liste_iti_D4G_isere_output.csv"

    # (115215 - Moulin vieux - [655494.8027820215,  5623148.037358337])(1769219 - Pointe des Ramays - [660219.878995,  5625628.144406])
    # (39268 - Roche Rousse - Sommet N - [614572.6447715042,  5606306.160257941])(113885 - Gresse en Vercors - La Ville - [617701.946977195,  5604692.540042164])
    interest_points_pattern: Pattern = re.compile(r"\((\d+) - ([^[]+) - (\[[^\]]+\])\)")

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs) -> pd.DataFrame:
        return pd.read_csv(
            path,
            sep=",",
            header=None,
            names=[
                "name",
                "c2c_id",
                "url",
                "outing_type",
                "unknown1",
                "unknown2",
                "unknown3",
                "mountains",
                "interest_points",
                "unknown4",
            ],
        )

    @classmethod
    def pre_process(cls, content: pd.DataFrame, **kwargs):
        def clean_coordinates(coords) -> list[Decimal]:
            coords = coords.strip("[]").replace(" ", "").split(",")
            return [Decimal(x) for x in coords]

        matches = content["interest_points"].str.extractall(cls.interest_points_pattern)
        matches.columns = ["place_id", "place_name", "coordinates"]

        # Split des coordonnées
        matches[["latitude", "longitude"]] = (
            matches["coordinates"].apply(clean_coordinates).apply(pd.Series)
        )

        # Fusion
        content = content.join(matches.droplevel(1), how="left")

        return content

    @classmethod
    def save(cls, content: pd.DataFrame, path: Path):
        super().save(content, path)
        content.to_csv(path, index=False)


class C2CBusStopsProcessor(ProcessorMixin):
    # Define paths
    input_dir = DATA_FOLDER / "C2C"
    input_file = input_dir / "UTF-8dump-c2corg-202505050900.sql.zip"
    output_dir = input_dir
    output_file = output_dir / "bus_stops_isere.parquet"

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs) -> list[dict] | gpd.GeoDataFrame:
        if path.suffix == ".parquet":
            return gpd.read_parquet(path)
        else:
            return cls._fetch_from_sql_file()

    @classmethod
    def save(cls, content: gpd.GeoDataFrame, path: Path) -> None:
        if path.suffix == ".parquet":
            content.to_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    @classmethod
    def pre_process(cls, content: list[dict] | None, **kwargs) -> gpd.GeoDataFrame | None:
        lines_by_stop_and_network: dict[
            tuple(str, str, str, str, Any), list[dict[str, str | int]]
        ] = dict()
        for stop_area in content:
            key = (
                stop_area["navitia_id"],
                stop_area["name"],
                stop_area["srid"],
                stop_area["network"],
                stop_area["geometry"],
            )
            if key not in lines_by_stop_and_network:
                lines_by_stop_and_network[key] = []
            lines_by_stop_and_network[key].append(
                {"stoparea_id": stop_area["stoparea_id"], "line": stop_area["line"]}
            )
        stops = []
        for key, value in lines_by_stop_and_network.items():
            stop = {
                "gtfs_id": None,
                "navitia_id": key[0],
                "osm_id": None,
                "name": key[1],
                "description": None,
                "line_gtfs_ids": [],
                "line_osm_ids": [],
                "network": key[3],
                "network_gtfs_id": None,
                "geometry": key[4],
                "other": {
                    "stoparea_id_and_line": value,
                    "srid": key[2],
                },
            }
            try:
                BusStop(**stop)
            except ValidationError as e:
                logger.error(f"Validation error for bus stop with id {id}: {e}")
                continue
            stops.append(stop)

        # Create GeoDataFrame
        if stops:
            gdf = gpd.GeoDataFrame(stops, geometry="geometry", crs="EPSG:3857")
            return gdf
        else:
            return gpd.GeoDataFrame([])

    @classmethod
    def _fetch_from_sql_file(cls) -> list[dict]:
        """Parse SQL dump to extract bus stop data into a DataFrame.

        Author: Laurent Sorba"""
        sql_filename_inside_zip = "dump-c2corg-202505050900.sql"
        with zipfile.ZipFile(cls.input_file, "r") as zip_ref:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Extract SQL file to temporary directory
                zip_ref.extract(sql_filename_inside_zip, tmp_dir)
                sql_file_path = Path(tmp_dir) / sql_filename_inside_zip
                stop_areas = cls._parse_sql_dump(sql_file_path)
                logger.info(f"Loaded {len(stop_areas)} bus stop areas from SQL dump")
                return stop_areas

    @classmethod
    def _parse_sql_dump(cls, sql_file: Path) -> list[dict]:
        """Parse SQL file to extract bus stop data into a DataFrame.

        Author: Laurent Sorba"""
        # Pattern to match INSERT statements
        insert_pattern = re.compile(
            r"INSERT INTO guidebook\.stopareas VALUES (.*?);", re.DOTALL
        )

        # List to store parsed stop areas
        stopareas = []

        with open(sql_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Process each INSERT statement
        for match in insert_pattern.finditer(content):
            values_str = match.group(1)

            # Split values preserving quoted strings (handling escaped quotes)
            values = []
            current = ""
            in_quote = False
            escape_next = False

            for char in values_str:
                if escape_next:
                    current += char
                    escape_next = False
                    continue

                if char == "\\":
                    escape_next = True
                    continue

                if char == "'":
                    in_quote = not in_quote
                    continue

                if char == "," and not in_quote:
                    values.append(current.strip())
                    current = ""
                    continue

                current += char

            if current.strip():
                values.append(current.strip())

            # Ensure we have enough values (at least 6)
            if len(values) < 6:
                continue

            try:
                # Extract basic fields
                stoparea_id = int(values[0].strip("("))
                navitia_id = values[1].strip("'")
                stoparea_name = values[2].strip("'")
                line = values[3].strip("'")
                operator = values[4].strip("'")
                ewkb_hex = values[5].strip("')")

                # Skip if geometry is NULL
                if ewkb_hex.upper() == "NULL":
                    continue

                # Convert hex to binary
                try:
                    ewkb_bytes = binascii.unhexlify(ewkb_hex)
                except binascii.Error:
                    continue

                # Check if we have enough data
                if len(ewkb_bytes) < 17:  # Minimum for point without SRID
                    continue

                # Read byte order (1 = little, 0 = big)
                byte_order = ewkb_bytes[0]
                is_little_endian = byte_order == 1

                # Read geometry type (4 bytes)
                geom_type_bytes = ewkb_bytes[1:5]

                # Extract geometry type (first 4 bits) and flags
                if is_little_endian:
                    geom_type = struct.unpack("<I", geom_type_bytes)[0]
                else:
                    geom_type = struct.unpack(">I", geom_type_bytes)[0]

                # Check if this is a point (type = 1) - ignore flags
                if (geom_type & 0x07) != 1:  # Use bitmask to ignore SRID flag and others
                    continue

                # Read SRID if present (bit 3 of geom_type is set)
                offset = 5
                srid = None
                if geom_type & 0x20000000:  # Check if SRID flag is set
                    if len(ewkb_bytes) < 9:
                        continue
                    if is_little_endian:
                        srid = struct.unpack("<I", ewkb_bytes[5:9])[0]
                    else:
                        srid = struct.unpack(">I", ewkb_bytes[5:9])[0]
                    offset = 9

                # Read coordinates
                if len(ewkb_bytes) < offset + 16:  # 8 bytes for x, 8 for y
                    continue

                # Extract X and Y coordinates
                if is_little_endian:
                    x = struct.unpack("<d", ewkb_bytes[offset : offset + 8])[0]
                    y = struct.unpack("<d", ewkb_bytes[offset + 8 : offset + 16])[0]
                else:
                    x = struct.unpack(">d", ewkb_bytes[offset : offset + 8])[0]
                    y = struct.unpack(">d", ewkb_bytes[offset + 8 : offset + 16])[0]

                # Add to list
                stop = {
                    "navitia_id": navitia_id,
                    "name": stoparea_name,
                    "network": operator,
                    "geometry": Point(x, y),
                    "stoparea_id": stoparea_id,
                    "line": line,
                    "srid": srid,
                }
                stopareas.append(stop)

            except Exception:
                # Skip problematic rows
                logger.warning(f"Skipping problematic stoparea entry: {values_str}")
        return stopareas


def main(**kwargs):
    reload_pipeline = False  # TODO: Put True when no more buggued
    logger.info("Processing C2C bus stops")
    C2CBusStopsProcessor.run(reload_pipeline)


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)
    main()
