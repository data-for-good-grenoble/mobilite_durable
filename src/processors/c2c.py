import re
from decimal import Decimal
from typing import Pattern

import pandas as pd

from src.settings import DATA_FOLDER
from src.utils.processor_mixin import ProcessorMixin


class C2cItiProcessor(ProcessorMixin):
    input_dir = DATA_FOLDER / "C2C"
    input_file = input_dir / "Liste_iti_D4G_isere.csv"
    output_dir = input_dir
    output_file = output_dir / "Liste_iti_D4G_isere_output.csv"

    # (115215 - Moulin vieux - [655494.8027820215,  5623148.037358337])(1769219 - Pointe des Ramays - [660219.878995,  5625628.144406])
    # (39268 - Roche Rousse - Sommet N - [614572.6447715042,  5606306.160257941])(113885 - Gresse en Vercors - La Ville - [617701.946977195,  5604692.540042164])
    interest_points_pattern: Pattern = re.compile(r"\((\d+) - ([^[]+) - (\[[^\]]+\])\)")

    @classmethod
    def fetch_from_file(cls, path, **kwargs):
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
    def pre_process(cls, content, **kwargs):
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
    def save(cls, content, path):
        super().save(content, path)
        content.to_csv(path, index=False)
