"""
This module provides functionality to getting OpenStreetMap data using the Overpass API.

Author: Nicolas Grosjean
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from pydantic import ValidationError

from src.models.bus_line import BusLine
from src.settings import DATA_FOLDER
from src.utils.logger import setup_logger
from src.utils.processor_mixin import ProcessorMixin

# Set up logger
logger = logging.getLogger(__name__)


class AbstractOSMProcessor(ProcessorMixin):
    # Define paths
    input_dir = DATA_FOLDER / "OSM"
    output_dir = input_dir

    # API declaration and technical limitations
    api_class = True  # TODO Export API into OverpassAPI class
    API_URL = "https://overpass-api.de/api/interpreter"
    api_timeout = 600  # seconds

    # Geographical delimitation
    area = "Isère"

    @classmethod
    def query_overpass(cls, query: str, timeout: int) -> dict:
        """
        Query Overpass API.

        Args:
            query: Overpass QL query
            timeout: Query timeout in seconds

        Returns:
            JSON response from the API
        """
        start = datetime.now()
        response = requests.post(
            cls.API_URL,
            data={"data": query},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout,
        )
        response.raise_for_status()
        end = datetime.now()
        elapsed = end - start
        logger.info(f"Getting overpass query results in {elapsed.seconds}s")
        return response.json()

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        if path.suffix in [".json", ".geojson"]:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif path.suffix == ".parquet":
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    @classmethod
    def save(cls, content, path: Path) -> None:
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
    output_file = AbstractOSMProcessor.output_dir / "bus_stops_isere.geojson"

    @classmethod
    def fetch_from_api(cls, **kwargs) -> dict | None:
        query = f"""
        [out:json][timeout:{cls.api_timeout}];
        area["name"="{cls.area}"]["boundary"="administrative"]->.searchArea;
        node["highway"="bus_stop"](area.searchArea);
        out geom;
        """
        return cls.query_overpass(query, cls.api_timeout)

    @classmethod
    def pre_process(cls, content, **kwargs) -> dict:
        features = []
        for element in content.get("elements", []):
            id = element.get("id")
            tags = element.get("tags", {})
            if "disused" in tags or "disused:public_transport" in tags or "abandoned" in tags:
                logger.debug(f"Skipping disused or abandoned bus stop with id {id}")
                continue
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [element["lon"], element["lat"]],
                },
                "properties": element.get("tags", {}),
                "id": id,
            }
            features.append(feature)
        return {
            "type": "FeatureCollection",
            "generator": content.get("generator", "overpass-turbo"),
            "copyright": content.get(
                "copyright",
                "The data included in this document is from www.openstreetmap.org. "
                "The data is made available under ODbL.",
            ),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "features": features,
        }


class OSMBusLinesProcessor(AbstractOSMProcessor):
    input_file = AbstractOSMProcessor.input_dir / "raw_bus_lines_isere.json"
    output_file = AbstractOSMProcessor.output_dir / "bus_lines_isere.parquet"

    @classmethod
    def fetch_from_api(cls, **kwargs) -> dict | None:
        query = f"""
        [out:json][timeout:{cls.api_timeout}];
        area["name"="{cls.area}"]["boundary"="administrative"]->.searchArea;
        relation["type"="route"]["route"="bus"](area.searchArea);
        out;
        """
        return cls.query_overpass(query, cls.api_timeout)

    @classmethod
    def pre_process(cls, content: dict, **kwargs) -> pd.DataFrame:
        rows = []
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
                    "network_osm_id": None,
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
                    "geometry": None,
                    "other": tags,
                }
                try:
                    BusLine(**relation)
                except ValidationError as e:
                    logger.error(f"Validation error for bus line with id {id}: {e}")
                    continue
                rows.append(relation)
        return pd.DataFrame(rows)


def main(**kwargs):
    reload_pipeline = True
    OSMBusStopsProcessor.run(reload_pipeline)
    OSMBusLinesProcessor.run(reload_pipeline)


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)
    main()
