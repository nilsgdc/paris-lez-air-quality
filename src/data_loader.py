import pandas as pd
import geopandas as gpd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "raw" / "airparif"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
ZFE_DIR = Path(__file__).parent.parent / "data" / "raw" / "zfe_perimetres"
IRIS_IDF_PATH = PROCESSED_DIR / "iris_idf" / "iris_idf.shp"


def load_airparif(year: int) -> pd.DataFrame:
    """
    Load Airparif NO2 data for a given year.
    Returns a DataFrame with stations as columns and a datetime index.

    Airparif file structure (6 header rows):
        row 0 : long identifiers  (e.g. PA01H:NO2)
        row 1 : full station names
        row 2 : short codes       (e.g. PA01H)  ← used as header
        row 3 : pollutant name    ("dioxyde d azote" as written in source file)
        row 4 : symbol            (NO2)
        row 5 : unit              (microg/m3)
        row 6+: hourly data
    """
    filepath = DATA_DIR / f"{year}_NO2.csv"

    df = pd.read_csv(
        filepath,
        sep=",",
        skiprows=[0, 1, 3, 4, 5],  # keeps row 2 (short codes) as header
        header=0,
        index_col=0,
        parse_dates=True,
    )

    df.index.name = "datetime"

    return df


def load_stations_metadata() -> gpd.GeoDataFrame:
    """
    Load Airparif station coordinates as a GeoDataFrame.
    Coordinates retrieved via OpenStreetMap Nominatim geocoding API.
    Source queries documented in the geocoding_query column.
    """
    filepath = DATA_DIR / "stations_metadata.csv"
    stations = pd.read_csv(filepath)
    return gpd.GeoDataFrame(
        stations,
        geometry=gpd.points_from_xy(stations["longitude"], stations["latitude"]),
        crs="EPSG:4326",
    )


def load_zfe_perimeter() -> gpd.GeoDataFrame:
    """
    Load the Paris LEZ (ZFE) perimeter as a GeoDataFrame.
    """
    filepath = ZFE_DIR / "zone-a-faibles-emissions.geojson"
    return gpd.read_file(filepath).to_crs("EPSG:4326")


def load_processed_airparif() -> pd.DataFrame:
    """
    Load the cleaned Airparif NO2 dataset from data/processed/.
    """
    filepath = PROCESSED_DIR / "airparif_clean.csv"
    return pd.read_csv(filepath, index_col=0, parse_dates=True)


def load_processed_meteo() -> pd.DataFrame:
    """
    Load the cleaned weather dataset from data/processed/.
    """
    filepath = PROCESSED_DIR / "meteo_clean.csv"
    return pd.read_csv(filepath, index_col=0, parse_dates=True)


def load_processed_insee() -> pd.DataFrame:
    """
    Load the cleaned INSEE IRIS income dataset from data/processed/.
    """
    filepath = PROCESSED_DIR / "insee_iris_clean.csv"
    return pd.read_csv(filepath, dtype={"IRIS": str})


def load_iris_contours() -> gpd.GeoDataFrame:
    """
    Load IRIS geographic contours, pre-filtered to inner Île-de-France.

    Source: IGN CONTOURS-IRIS 3.0 (edition 2024-01-01), filtered to
    departments 75, 92, 93, 94 (Paris + petite couronne) — 2,752 IRIS
    instead of the 48,569 national IRIS. Filtering is done once
    upstream so the repo ships a ~2.6 MB shapefile instead of 123 MB,
    and no longer depends on the IGN download server.

    Reprojected from Lambert 93 (EPSG:2154) to WGS84 (EPSG:4326).
    """
    return gpd.read_file(IRIS_IDF_PATH).to_crs("EPSG:4326")