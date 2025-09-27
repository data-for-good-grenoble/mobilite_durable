from typing import Any

from pydantic import BaseModel


class BusStop(BaseModel):
    gtfs_id: str | None
    navitia_id: str | None
    osm_id: int | None
    name: str
    description: str | None
    line_gtfs_ids: list[str]
    line_osm_ids: list[int]
    network: str | None
    network_gtfs_id: str | None
    geometry: Any | None
    other: dict[str, Any]
