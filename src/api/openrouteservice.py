import requests


class OpenRouteServiceAPI:
    API_URL = "http://localhost:8080/ors/v2"

    @classmethod
    def compute_distance(
        cls, start_coords: tuple[float, float], end_coords: tuple[float, float]
    ) -> float:
        """
        Compute the walking distance between two coordinates using the openrouteservice API.

        Parameters:
        start_coords (tuple): A tuple containing the latitude and longitude of the start point (lat, lon).
        end_coords (tuple): A tuple containing the latitude and longitude of the end point (lat, lon).

        Returns:
        float: The walking distance in meters.
        """

        base_url = cls.API_URL + "/directions/foot-hiking"
        params = {
            "start": f"{start_coords[1]},{start_coords[0]}",
            "end": f"{end_coords[1]},{end_coords[0]}",
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        distance = data["features"][0]["properties"]["segments"][0]["distance"]

        return distance
