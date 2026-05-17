import pandas as pd
import numpy as np

# Stations excluded due to >20% missing data over the study period (2019-2023)
# Decision documented in 01_exploration.ipynb, Section 1
EXCLUDED_STATIONS = ["PA04C", "DEF", "BASCH", "PA01H", "SOULT"]

# INSEE department codes for Paris and inner suburbs
INNER_IDF_DEPTS = ["75", "92", "93", "94"]


def remove_invalid_stations(
    df: pd.DataFrame,
    excluded: list = EXCLUDED_STATIONS,
) -> pd.DataFrame:
    """Drop stations excluded due to excessive missing data (>20% NaN over study period)."""
    return df.drop(columns=excluded, errors="ignore")


def replace_negative_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace negative NO2 readings with NaN.
    Negative concentrations are physically impossible and indicate sensor errors.
    """
    return df.where(df >= 0, other=np.nan)


def interpolate_short_gaps(
    df: pd.DataFrame,
    max_gap_hours: int = 3,
) -> pd.DataFrame:
    """
    Interpolate NaN sequences of at most max_gap_hours consecutive hours.

    Rationale: NO2 varies slowly over short periods, so gaps <= 3h are
    plausibly caused by sensor glitches and can be interpolated linearly.
    Longer gaps (station outages) are left as NaN to avoid introducing noise.
    """
    return df.interpolate(method="time", limit=max_gap_hours)


def clean_airparif(
    dfs: dict,
    excluded: list = EXCLUDED_STATIONS,
    max_gap_hours: int = 3,
) -> pd.DataFrame:
    """
    Full Airparif NO2 cleaning pipeline.

    Steps:
        1. Exclude stations with >20% missing data over the study period
        2. Replace negative values with NaN (physically impossible readings)
        3. Concatenate all years into a single DataFrame
        4. Interpolate short gaps (<= max_gap_hours consecutive NaN)

    Parameters
    ----------
    dfs : dict
        Dictionary {year: DataFrame} as returned by data_loader.load_airparif().
    excluded : list
        Station codes to drop before any other processing.
    max_gap_hours : int
        Maximum consecutive NaN hours to interpolate. Default = 3.

    Returns
    -------
    pd.DataFrame
        Cleaned panel indexed by datetime, one column per station.
    """
    cleaned = {
        year: df.pipe(remove_invalid_stations, excluded=excluded)
                .pipe(replace_negative_values)
        for year, df in dfs.items()
    }
    return pd.concat(cleaned.values()).pipe(interpolate_short_gaps, max_gap_hours=max_gap_hours)


def clean_insee(
    df: pd.DataFrame,
    depts: list = INNER_IDF_DEPTS,
) -> pd.DataFrame:
    """
    INSEE IRIS median income cleaning pipeline.

    Steps:
        1. Filter to Paris and inner suburbs (depts 75, 92, 93, 94)
        2. Keep only IRIS code and median disposable income (DISP_MED21)
        3. Replace INSEE special codes ('ns' = non-significant, 'nd' = not available) with NaN
        4. Convert French decimal separator (comma) to dot and cast to float

    Parameters
    ----------
    df : pd.DataFrame
        Raw INSEE IRIS file as loaded from CSV.
    depts : list
        Department codes to retain. Default = inner Île-de-France.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with columns ['IRIS', 'DISP_MED21'].
    """
    df = df[df["IRIS"].str[:2].isin(depts)].copy()
    df = df[["IRIS", "DISP_MED21"]].copy()
    df["DISP_MED21"] = (
        df["DISP_MED21"]
        .replace({"ns": np.nan, "nd": np.nan})
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    return df
