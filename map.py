# Import libraries
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Function to translate geometries
def translate_geometries(df, x, y, scale, rotate):
    df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
    center = df.dissolve().centroid.iloc[0]
    df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
    df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)
    return df

# Function to adjust state positions
def adjust_maps(df):
    # Retrieve the individual state objects
    df_main_land = df[~df.STATEFP.isin(["02", "15", "72"])]
    df_alaska = df[df.STATEFP == "02"]
    df_hawaii = df[df.STATEFP == "15"]
    df_puerto_rico = df[df.STATEFP == "72"]

    # Reposition the state objects
    df_alaska = translate_geometries(df_alaska, 1300000, -4900000, 0.5, 32)
    df_hawaii = translate_geometries(df_hawaii, 5400000, -1500000, 1, 24)
    df_puerto_rico = translate_geometries(df_puerto_rico, -1000000, 250000, 4, -14)

    # Combine the states together to form the dataset
    return pd.concat([df_main_land, df_alaska, df_hawaii, df_puerto_rico])

# Function to load the map
def load_map():
    # Load map shapefile
    map_shape = gpd.read_file("shape/cb_2018_us_state_500k.shp")
    map_shape = map_shape[~map_shape.STATEFP.isin(["69", "60", "66", "78"])]
    map_shape = map_shape.to_crs("ESRI:102003")

    # Apply transformations
    return adjust_maps(map_shape)

# Function to create map markers
def create_markers(marker_data, crs):
    """
    Converts a list of marker data dictionaries into a GeoDataFrame.

    Args:
        marker_data (list): List of dictionaries with lat/lng coordinates.
        crs (str): Coordinate Reference System to transform the markers.

    Returns:
        gpd.GeoDataFrame: Transformed GeoDataFrame with markers.
    """

    # Ensure marker_data is a list of dictionaries
    if not isinstance(marker_data, list) or not all(isinstance(m, dict) for m in marker_data):
        raise ValueError("marker_data must be a list of dictionaries with 'lat' and 'lng' keys.")

    # Convert marker data to GeoDataFrame
    marker_df = pd.DataFrame(marker_data)

    # Check if the DataFrame is empty
    if marker_df.empty:
        raise ValueError("No marker data provided.")

    # Ensure lat/lng columns exist
    if "lat" not in marker_df.columns or "lng" not in marker_df.columns:
        raise ValueError("Missing required lat/lng fields in marker data.")

    # Create GeoDataFrame with original CRS
    gdf_markers = gpd.GeoDataFrame(
        marker_df,
        geometry=[Point(xy) for xy in zip(marker_df["lng"], marker_df["lat"])],
        crs="EPSG:4326"
    )

    # Convert markers to the target CRS
    return gdf_markers.to_crs(crs)