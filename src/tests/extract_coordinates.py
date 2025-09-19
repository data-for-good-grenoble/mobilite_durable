# Arnaud Reboud 19/06/2025
# This script loads the List_iti_D4G_isre.csv dataset and extracts the coordinates (X and Y) in EPSG:3857 and converts them to EPSG:4326 (lon, lat). It then add both coordinates to the dataset and saves the results to a CSV file. Original data are conserved.

import geopandas as gpd
import pandas as pd
from pyproj import Transformer

# load dataset
data = pd.read_csv("src/data/C2C/Liste_iti_D4G_isere.csv")

# Extract X and Y coordinates from the column
X = (
    data["(id WP - titre - [X,Y] - accessibilité (si renseigné) )"]
    .str.extract(r"(?<= - \[)([^]]+)(?=\])")[0]
    .str.strip()
    .str.split(",", expand=True)[0]
    .astype(float)
)
Y = (
    data["(id WP - titre - [X,Y] - accessibilité (si renseigné) )"]
    .str.extract(r"(?<= - \[)([^]]+)(?=\])")[0]
    .str.strip()
    .str.split(",", expand=True)[1]
    .astype(float)
)

# Transform coordinates from EPSG:3857 to EPSG:4326
# EPSG:3857 is Web Mercator, EPSG:4326 is WGS84
transformer = Transformer.from_crs(crs_from="EPSG:3857", crs_to="EPSG:4326", always_xy=True)
lon, lat = transformer.transform(X, Y)

# Add coordinates to the DataFrame
data["X"], data["Y"], data["lon"], data["lat"] = X, Y, lon, lat

# Save the DataFrame to a CSV file
data.to_csv("src/data/C2C/Liste_iti_D4G_isere_output.csv", index=False)

# create GeoDataFrame with X and Y coordinates in EPSG:3857
gdf_3857 = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(X, Y), crs="EPSG:3857")

# convert GeoDataFrame to EPSG:4326
gdf_4326 = gdf_3857.to_crs("EPSG:4326")
