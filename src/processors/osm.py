"""
This module provides functionality to getting OpenStreetMap data using the Overpass API.

Author: Nicolas Grosjean
"""

import json
import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pydantic import ValidationError
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from src.api.overpass import OverpassAPI
from src.models.bus_line import BusLine
from src.models.bus_stop import BusStop
from src.settings import DATA_FOLDER, EPSG_WGS84
from src.utils.logger import setup_logger
from src.utils.processor_mixin import ProcessorMixin

# Set up logger
logger = logging.getLogger(__name__)


class AbstractOSMProcessor(ProcessorMixin):
    # Define paths
    input_dir = DATA_FOLDER / "OSM"
    output_dir = input_dir

    # API declaration and technical limitations
    api_class: type[OverpassAPI] = OverpassAPI
    api_timeout = 600  # seconds

    # Geographical delimitation
    area = "Isère"

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs) -> dict | pd.DataFrame:
        fetch_geometry = kwargs.pop("fetch_geometry", False)
        if fetch_geometry:
            logger.info("Fetching data with geometry suffix from file")
            path = path.with_name(f"{path.stem}_with_geometry{path.suffix}")
        if path.suffix in [".json", ".geojson"]:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif path.suffix == ".parquet":
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    @classmethod
    def save(cls, content, path: Path, **kwargs) -> None:
        save_geometry = kwargs.pop("save_geometry", False)
        if save_geometry:
            logger.info("Saving data with geometry suffix to file")
            path = path.with_name(f"{path.stem}_with_geometry{path.suffix}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in [".json", ".geojson"]:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        elif path.suffix == ".parquet":
            content.to_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")


class OSMBusStopsProcessor(AbstractOSMProcessor):
    input_file = AbstractOSMProcessor.input_dir / "raw_bus_stops_isere.geojson"
    output_file = AbstractOSMProcessor.output_dir / "bus_stops_isere.parquet"

    @classmethod
    def fetch_from_api(cls, **kwargs) -> dict | None:
        query = f"""
        [out:json][timeout:{cls.api_timeout}];
        area["name"="{cls.area}"]["boundary"="administrative"]->.searchArea;
        node["highway"="bus_stop"](area.searchArea);
        out geom;
        """
        return cls.api_class.query_overpass(query, cls.api_timeout)

    @classmethod
    def pre_process(cls, content: dict, **kwargs) -> gpd.GeoDataFrame:
        # Create a dict mapping stop OSM IDs to the list of line OSM IDs containing them
        logger.info("Fetching bus lines to map stops to lines")
        lines_df: pd.DataFrame = OSMBusLinesProcessor.fetch(reload_pipeline=False)
        osm_stop_to_line_ids = {}
        for _, row in lines_df.iterrows():
            line_osm_id = row["osm_id"]
            for stop_osm_id in row["stops_osm_ids"]:
                if stop_osm_id not in osm_stop_to_line_ids:
                    osm_stop_to_line_ids[stop_osm_id] = []
                osm_stop_to_line_ids[stop_osm_id].append(line_osm_id)
        logger.info("Mapping stops to lines completed")

        stops = []
        for element in content.get("elements", []):
            id = element.get("id")
            tags = element.get("tags", {})
            if "disused" in tags or "disused:public_transport" in tags or "abandoned" in tags:
                logger.debug(f"Skipping disused or abandoned bus stop with id {id}")
                continue
            stop = {
                "gtfs_id": tags.pop("gtfs_id", None),
                "navitia_id": None,
                "osm_id": id,
                "name": tags.pop("name", ""),
                "description": tags.pop("description", None),
                "line_gtfs_ids": [],
                "line_osm_ids": osm_stop_to_line_ids.get(id, []),
                "network": tags.pop("network", None),
                "network_gtfs_id": None,
                "geometry": Point(element["lon"], element["lat"]),
                "other": tags,
            }
            try:
                BusStop(**stop)
            except ValidationError as e:
                logger.error(f"Validation error for bus stop with id {id}: {e}")
                continue
            stops.append(stop)
        if len(stops) == 0:
            logger.warning("No valid bus stops found in the data.")
            gdf = gpd.GeoDataFrame(
                columns=[
                    "gtfs_id",
                    "navitia_id",
                    "osm_id",
                    "name",
                    "description",
                    "line_gtfs_ids",
                    "line_osm_ids",
                    "network",
                    "network_gtfs_id",
                    "geometry",
                    "other",
                ],
                geometry="geometry",
            )
        else:
            gdf = gpd.GeoDataFrame(stops, geometry="geometry")
        gdf.set_crs(EPSG_WGS84, inplace=True)
        return gdf

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs) -> dict | gpd.GeoDataFrame:
        if path.suffix == ".parquet":
            return gpd.read_parquet(path)
        else:
            return super().fetch_from_file(path, **kwargs)


class OSMBusLinesProcessor(AbstractOSMProcessor):
    input_file = AbstractOSMProcessor.input_dir / "raw_bus_lines_isere.json"
    output_file = AbstractOSMProcessor.output_dir / "bus_lines_isere.parquet"

    @classmethod
    def fetch_from_api(cls, **kwargs) -> dict | None:
        fetch_geometry = kwargs.pop("fetch_geometry", False)
        if fetch_geometry:
            logger.info("Fetching bus lines with geometry from Overpass API")
            query = f"""
            [out:json][timeout:{cls.api_timeout}];
            area["name"="{cls.area}"]["boundary"="administrative"]->.searchArea;
            relation["type"="route"]["route"="bus"](area.searchArea)->.busRoutes;
            .busRoutes out body;
            (way(r.busRoutes); node(w););
            out skel qt;
            """
        else:
            logger.info("Fetching bus lines without geometry from Overpass API")
            query = f"""
            [out:json][timeout:{cls.api_timeout}];
            area["name"="{cls.area}"]["boundary"="administrative"]->.searchArea;
            relation["type"="route"]["route"="bus"](area.searchArea);
            out;
            """
        return cls.api_class.query_overpass(query, cls.api_timeout)

    @classmethod
    def pre_process(cls, content: dict, **kwargs) -> pd.DataFrame | gpd.GeoDataFrame:
        rows = []

        # Create the ways geometry
        nodes: dict[int, tuple[float, float]] = {
            element["id"]: (element["lon"], element["lat"])
            for element in content["elements"]
            if element["type"] == "node" and "lat" in element and "lon" in element
        }
        ways: dict[int, LineString | Polygon] = dict()
        for element in content["elements"]:
            if element["type"] == "way":
                if "nodes" not in element:
                    continue
                id = element["id"]
                coords = [nodes[node_id] for node_id in element["nodes"]]
                if coords[0] == coords[-1]:
                    geom = Polygon(coords)
                else:
                    geom = LineString(coords)
                ways[id] = geom

        # Create the bus lines (relations)
        for element in content["elements"]:
            if element["type"] == "relation":
                id = element["id"]
                tags = element["tags"]
                if "disused" in tags or "disused:type" in tags or "abandoned" in tags:
                    logger.debug(f"Skipping disused or abandoned bus line with id {id}")
                    continue
                relation = {
                    "gtfs_id": element["tags"].pop("gtfs_id", None),
                    "osm_id": id,
                    "name": tags.pop("name", ""),
                    "from_location": tags.pop("from", None),
                    "to": tags.pop("to", None),
                    "network": tags.pop("network", None),
                    "network_gtfs_id": None,
                    "network_wikidata": tags.pop("network:wikidata", None),
                    "operator": tags.pop("operator", None),
                    "colour": tags.pop("colour", None),
                    "text_colour": tags.pop("text_colour", None),
                    "stop_gtfs_ids": [],
                    "stops_osm_ids": list(
                        member["ref"]
                        for member in element["members"]
                        if member["role"] == "stop"
                    ),
                    "school": tags.pop("bus", None) == "school",
                    "geometry": unary_union(
                        list(
                            ways[member["ref"]]
                            for member in element["members"]
                            if member["role"] == ""
                            and member["type"] == "way"
                            and member["ref"] in ways
                        )
                    )
                    if ways
                    else None,
                    "other": tags,
                }
                try:
                    BusLine(**relation)
                except ValidationError as e:
                    logger.error(f"Validation error for bus line with id {id}: {e}")
                    continue
                rows.append(relation)
        if ways:
            gdf = gpd.GeoDataFrame(rows, geometry="geometry")
            gdf.set_crs(EPSG_WGS84, inplace=True)
            return gdf
        else:
            return pd.DataFrame(rows)

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs) -> dict | pd.DataFrame | gpd.GeoDataFrame:
        fetch_geometry = kwargs.pop("fetch_geometry", False)
        if fetch_geometry and path.suffix == ".parquet":
            logger.info("Fetching data with geometry suffix from file")
            path = path.with_name(f"{path.stem}_with_geometry{path.suffix}")
            return gpd.read_parquet(path)
        else:
            return super().fetch_from_file(path, **kwargs)


def main(**kwargs):
    reload_pipeline = True
    # Process lines without geometry first to get the mapping of stops to lines when processing stops
    logger.info("Processing OSM bus lines without geometry")
    OSMBusLinesProcessor.run(reload_pipeline)
    logger.info("Processing OSM bus stops")
    OSMBusStopsProcessor.run(reload_pipeline)
    logger.info("Processing OSM bus lines with geometry")
    OSMBusLinesProcessor.run(
        reload_pipeline,
        fetch_api_kwargs={"fetch_geometry": True},
        fetch_input_kwargs={"fetch_geometry": True},
        fetch_output_kwargs={"fetch_geometry": True},
        save_kwargs={"save_geometry": True},
    )


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)
    main()
