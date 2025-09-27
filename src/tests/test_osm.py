from typing import Any

import geopandas as gpd
import pandas as pd
import pytest
from pytest_mock import MockerFixture
from shapely.geometry import Point

from src.processors.osm import OSMBusLinesProcessor, OSMBusStopsProcessor


@pytest.fixture
def fetch_bus_lines_mocker(mocker: MockerFixture):
    mocker.patch.object(
        OSMBusLinesProcessor,
        "fetch",
        return_value=pd.DataFrame(
            [
                {
                    "osm_id": 1,
                    "stops_osm_ids": [101, 102],
                },
                {
                    "osm_id": 2,
                    "stops_osm_ids": [101, 103],
                },
                {
                    "osm_id": 3,
                    "stops_osm_ids": [101, 104],
                },
            ]
        ),
    )
    return mocker


class TestOSMBusLinesProcessorPreProcess:
    """Test de pre_process method of OSMBusLinesProcessor.

    Author: Nicolas Grosjean
    """

    def test_pre_process_ko_bad_type(self, caplog: pytest.LogCaptureFixture):
        input_content = {
            "elements": [
                {
                    "type": "relation",
                    "id": "string_instead_of_int",
                    "tags": {
                        "name": "Test Bus Line",
                        "from": "Test Stop A",
                        "to": "Test Stop B",
                        "network": "Test Network",
                        "operator": "Test Operator",
                        "colour": "#FF0000",
                        "text_colour": "#FFFFFF",
                    },
                    "members": [
                        {"role": "stop", "ref": 101},
                        {"role": "stop", "ref": 102},
                    ],
                }
            ]
        }
        expected = pd.DataFrame([])
        expected_log_message = (
            "Validation error for bus line with id string_instead_of_int: 1 validation error for BusLine\n"
            "osm_id\n"
            "  Input should be a valid integer, unable to parse string as an integer"
            " [type=int_parsing, input_value='string_instead_of_int', input_type=str]\n"
            "    For further information visit https://errors.pydantic.dev/2.11/v/int_parsing"
        )
        result = OSMBusLinesProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)
        assert caplog.records[-1].message == expected_log_message

    def test_pre_process_no_elements(self):
        input_content = {"elements": []}
        expected = pd.DataFrame([])
        result = OSMBusLinesProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)

    def test_pre_process_no_relation(self):
        input_content = {
            "elements": [
                {"type": "node", "id": 1, "tags": {"name": "Not a relation"}},
                {"type": "way", "id": 2, "tags": {"name": "Also not a relation"}},
            ]
        }
        expected = pd.DataFrame([])
        result = OSMBusLinesProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)

    def test_pre_process_ok_one_element(self):
        input_content = {
            "elements": [
                {
                    "type": "relation",
                    "id": 1,
                    "tags": {
                        "name": "Test Bus Line",
                        "from": "Test Stop A",
                        "to": "Test Stop B",
                        "network": "Test Network",
                        "operator": "Test Operator",
                        "colour": "#FF0000",
                        "text_colour": "#FFFFFF",
                        "bus": "school",
                        "public_transport:version": "2",
                    },
                    "members": [
                        {"role": "stop", "ref": 101},
                        {"role": "stop", "ref": 102},
                    ],
                }
            ]
        }
        expected = pd.DataFrame(
            [
                {
                    "gtfs_id": None,
                    "osm_id": 1,
                    "name": "Test Bus Line",
                    "from_location": "Test Stop A",
                    "to": "Test Stop B",
                    "network": "Test Network",
                    "network_gtfs_id": None,
                    "network_wikidata": None,
                    "operator": "Test Operator",
                    "colour": "#FF0000",
                    "text_colour": "#FFFFFF",
                    "stop_gtfs_ids": [],
                    "stops_osm_ids": [101, 102],
                    "school": True,
                    "geometry": None,
                    "other": {"public_transport:version": "2"},
                }
            ]
        )
        result = OSMBusLinesProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)

    def test_pre_process_ok_multiple_elements(self):
        input_content = {
            "elements": [
                {
                    "type": "relation",
                    "id": 1,
                    "tags": {
                        "name": "Test Bus Line 1",
                        "from": "Test Stop A",
                        "to": "Test Stop B",
                        "network": "Test Network",
                        "operator": "Test Operator",
                        "colour": "#FF0000",
                        "text_colour": "#FFFFFF",
                        "public_transport:version": "2",
                        "ref": "327",
                        "name:fr": "BlaBlaCar: Madrid, Gare Routière Sud → Lyon, Perrache",
                    },
                    "members": [
                        {"role": "stop", "ref": 101},
                        {"role": "stop", "ref": 102},
                    ],
                },
                {
                    "type": "relation",
                    "id": 2,
                    "tags": {
                        "name": "Test Bus Line 2",
                        "from": "Test Stop C",
                        "to": "Test Stop D",
                        "network": "Test Network",
                        "operator": "Test Operator 2",
                        "colour": "#00FF00",
                        "text_colour": "#000000",
                        "bus": "school",
                    },
                    "members": [
                        {"role": "stop", "ref": 201},
                        {"role": "stop", "ref": 202},
                    ],
                },
                {
                    "type": "relation",
                    "id": 3,
                    "tags": {
                        "name": "Disused Bus Line",
                        "from": "Old Stop A",
                        "to": "Old Stop B",
                        "network": "Old Network",
                        "operator": "Old Operator",
                        "colour": "#0000FF",
                        "text_colour": "#FFFF00",
                        "disused": "yes",
                    },
                },
            ]
        }
        expected = pd.DataFrame(
            [
                {
                    "gtfs_id": None,
                    "osm_id": 1,
                    "name": "Test Bus Line 1",
                    "from_location": "Test Stop A",
                    "to": "Test Stop B",
                    "network": "Test Network",
                    "network_gtfs_id": None,
                    "network_wikidata": None,
                    "operator": "Test Operator",
                    "colour": "#FF0000",
                    "text_colour": "#FFFFFF",
                    "stop_gtfs_ids": [],
                    "stops_osm_ids": [101, 102],
                    "school": False,
                    "geometry": None,
                    "other": {
                        "public_transport:version": "2",
                        "ref": "327",
                        "name:fr": "BlaBlaCar: Madrid, Gare Routière Sud → Lyon, Perrache",
                    },
                },
                {
                    "gtfs_id": None,
                    "osm_id": 2,
                    "name": "Test Bus Line 2",
                    "from_location": "Test Stop C",
                    "to": "Test Stop D",
                    "network": "Test Network",
                    "network_gtfs_id": None,
                    "network_wikidata": None,
                    "operator": "Test Operator 2",
                    "colour": "#00FF00",
                    "text_colour": "#000000",
                    "stop_gtfs_ids": [],
                    "stops_osm_ids": [201, 202],
                    "school": True,
                    "geometry": None,
                    "other": {},
                },
            ]
        )
        result = OSMBusLinesProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)


class TestOSMBusStopsProcessorPreProcess:
    """Test de pre_process method of OSMBusStopsProcessor.

    Author: Nicolas Grosjean
    """

    def test_pre_process_ko_bad_type(
        self, caplog: pytest.LogCaptureFixture, fetch_bus_lines_mocker: MockerFixture
    ):
        input_content = {
            "elements": [
                {
                    "type": "node",
                    "id": "string_instead_of_int",
                    "lon": "2.3522",
                    "lat": "48.8566",
                    "tags": {
                        "gtfs_id": "STOP123",
                        "name": "Test Stop A",
                        "description": "Test description",
                    },
                }
            ]
        }
        expected = gpd.GeoDataFrame(
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
        expected_log_message = (
            "Validation error for bus stop with id string_instead_of_int: 1 validation error for BusStop\n"
            "osm_id\n"
            "  Input should be a valid integer, unable to parse string as an integer"
            " [type=int_parsing, input_value='string_instead_of_int', input_type=str]\n"
            "    For further information visit https://errors.pydantic.dev/2.11/v/int_parsing"
        )
        latest_expected_log_message = "No valid bus stops found in the data."
        result = OSMBusStopsProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)
        assert caplog.records[-1].message == latest_expected_log_message
        assert caplog.records[-2].message == expected_log_message

    def test_pre_process_no_elements(self, fetch_bus_lines_mocker: MockerFixture):
        input_content: dict[str, Any] = {"elements": []}
        expected = gpd.GeoDataFrame(
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
        result = OSMBusStopsProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)

    def test_pre_process_ok_one_element(self, fetch_bus_lines_mocker: MockerFixture):
        input_content = {
            "elements": [
                {
                    "type": "node",
                    "id": 1,
                    "lon": "2.35222",
                    "lat": "48.85658",
                    "tags": {
                        "gtfs_id": "STOP123",
                        "name": "Test Stop A",
                        "description": "Test description",
                    },
                }
            ]
        }
        expected = gpd.GeoDataFrame(
            [
                {
                    "gtfs_id": "STOP123",
                    "navitia_id": None,
                    "osm_id": 1,
                    "name": "Test Stop A",
                    "description": "Test description",
                    "line_gtfs_ids": [],
                    "line_osm_ids": [],
                    "network": None,
                    "network_gtfs_id": None,
                    "geometry": Point(2.35222, 48.85658),
                    "other": {},
                }
            ],
            geometry="geometry",
        )
        result = OSMBusStopsProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)

    def test_pre_process_ok_multiple_elements(self, fetch_bus_lines_mocker: MockerFixture):
        input_content = {
            "elements": [
                {
                    "type": "node",
                    "id": 101,
                    "lon": "2.3522",
                    "lat": "48.8566",
                    "tags": {
                        "gtfs_id": "STOP123",
                        "name": "Test Stop A",
                        "description": "Test description A",
                    },
                },
                {
                    "type": "node",
                    "id": 2,
                    "lon": "2.295",
                    "lat": "48.8738",
                    "tags": {
                        "name": "Test Stop B",
                        "description": "Test description B",
                        "disused": "yes",
                    },
                },
                {
                    "type": "node",
                    "id": 104,
                    "lon": "2.3333",
                    "lat": "48.8600",
                    "tags": {
                        "gtfs_id": "STOP456",
                        "name": "Test Stop C",
                        # No description
                    },
                },
            ]
        }
        expected = gpd.GeoDataFrame(
            [
                {
                    "gtfs_id": "STOP123",
                    "navitia_id": None,
                    "osm_id": 101,
                    "name": "Test Stop A",
                    "description": "Test description A",
                    "line_gtfs_ids": [],
                    "line_osm_ids": [1, 2, 3],
                    "network": None,
                    "network_gtfs_id": None,
                    "geometry": Point(2.3522, 48.8566),
                    "other": {},
                },
                {
                    "gtfs_id": "STOP456",
                    "navitia_id": None,
                    "osm_id": 104,
                    "name": "Test Stop C",
                    "description": None,
                    "line_gtfs_ids": [],
                    "line_osm_ids": [3],
                    "network": None,
                    "network_gtfs_id": None,
                    "geometry": Point(2.3333, 48.8600),
                    "other": {},
                },
            ],
            geometry="geometry",
        )
        result = OSMBusStopsProcessor.pre_process(input_content)
        pd.testing.assert_frame_equal(result, expected)
