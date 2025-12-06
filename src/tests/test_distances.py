import pandas as pd
import pytest
from pytest_mock import MockerFixture

from processors.distances import DistancesProcessor


@pytest.fixture
def mock_get_bus_stops(mocker: MockerFixture):
    res = pd.DataFrame(
        [(0, None, None, None)], columns=["osm_id", "gtfs_id", "navitia_id", "geometry"]
    )
    mocker.patch.object(DistancesProcessor, "_get_bus_stops", return_value=res)


@pytest.fixture
def mock_get_area_activities(mocker: MockerFixture):
    res = pd.DataFrame([(0, None)], columns=["Id wp", "geometry"])
    mocker.patch.object(DistancesProcessor, "_get_area_activities", return_value=res)


@pytest.fixture
def mock_compute_distance(mocker: MockerFixture):
    mocker.patch.object(DistancesProcessor, "_compute_distance", return_value=42.0)


class TestFetchFromAPI:
    def test_fetch_from_api(
        self,
        mock_get_bus_stops: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
    ):
        result = DistancesProcessor.fetch_from_api()
        expected = pd.DataFrame(
            [(0, None, None, 0, 42.0)],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m"],
        )
        pd.testing.assert_frame_equal(result, expected)
