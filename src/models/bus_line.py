from typing import Any

from pydantic import BaseModel


class BusLine(BaseModel):
    gtfs_id: str | None
    osm_id: int | None
    name: str
    from_location: str | None
    to: str | None
    network: str | None
    network_gtfs_id: str | None
    network_wikidata: str | None
    operator: str | None
    colour: str | None
    text_colour: str | None
    stop_gtfs_ids: list[str]
    stops_osm_ids: list[int]
    school: bool
    geometry: Any | None
    other: dict[str, Any]
