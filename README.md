# Air Quality & Low Emission Zone — Paris NO₂ Impact Analysis

A causal inference study measuring the effect of the Paris Low Emission Zone (ZFE-m)
on NO₂ concentrations, with a socio-economic equity dimension.

---

## Business question

> Did the Paris LEZ Crit'Air 3 ban (June 2021) lead to a measurable reduction in NO₂
> concentrations at traffic-adjacent monitoring stations, and does this effect differ
> by neighbourhood median income?

---

## Key findings

| Metric | Value |
|--------|-------|
| LEZ causal effect (DiD) | **−1.22 µg/m³** (p < 0.001) |
| General post-2021 trend | −3.49 µg/m³ across all stations |
| Income interaction (did × income_std) | +0.049 (p = 0.121, not significant) |
| R² — base model | 0.150 |
| R² — model with income | 0.192 |
| Panel observations | 1,518,446 (hourly, 2019–2023) |

The LEZ is associated with an additional NO₂ reduction of **1.22 µg/m³** inside the zone,
after controlling for wind speed, precipitation, and temperature.
The income interaction is not statistically significant — the LEZ effect does not
measurably vary with neighbourhood income at this sample size.

---

## Methodology

- **Design:** Difference-in-differences (DiD) with 13 treatment stations (inside LEZ)
  and 23 control stations (outside LEZ)
- **Treatment date:** June 2021 (Crit'Air 3 ban enforcement)
- **Regression:** OLS with HAC-robust standard errors (maxlags=24) to correct for
  autocorrelation in hourly time series data
- **Controls:** wind speed, precipitation, temperature (Open-Meteo API, hourly)
- **Income variable:** INSEE IRIS 2021 median disposable income, standardised (z-score),
  matched to each station via nearest-IRIS spatial join (EPSG:2154)
- **Station coordinates:** OpenStreetMap Nominatim geocoding API

---

## Project structure

```
├── notebooks/
│   ├── 01_exploration.ipynb    # Data discovery: Airparif, ZFE, INSEE, weather
│   ├── 02_cleaning.ipynb       # NaN treatment, interpolation, processed exports
│   └── 03_analysis.ipynb       # Spatial classification, temporal trends, DiD, income
├── src/
│   └── data_loader.py          # Centralised loading functions for all datasets
├── data/
│   ├── raw/                    # Source files (gitignored)
│   └── processed/              # Cleaned exports: airparif_clean, meteo_clean, insee_iris_clean
├── outputs/                    # Generated figures (gitignored)
├── requirements.txt
└── README.md
```

---

## Data sources

| Dataset | Source | Coverage |
|---------|--------|----------|
| NO₂ hourly measurements | [Airparif](https://www.airparif.fr/) | 36 stations, 2019–2023 |
| LEZ perimeter | [data.gouv.fr](https://www.data.gouv.fr/) | Paris ZFE-m GeoJSON |
| IRIS median income | [INSEE](https://www.insee.fr/) | Île-de-France, 2021 |
| Weather controls | [Open-Meteo API](https://open-meteo.com/) | Paris, hourly, 2019–2023 |
| IRIS geographic contours | [IGN](https://geoservices.ign.fr/) | France, 2024 edition |

---

## How to run

```bash
# 1. Create and activate virtual environment
python -m venv zfe-env
source zfe-env/bin/activate      # Windows: zfe-env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place raw data in data/raw/ (see Data sources above)

# 4. Run notebooks in order
jupyter notebook
```

Notebooks are self-contained and load data via `src/data_loader.py`.
Run them in order: `01` → `02` → `03`.

---

## Limitations

1. **Low station count (n=36):** limits statistical power for interaction effects
2. **Single weather point:** one Open-Meteo location for all stations; outer stations may differ
3. **No station fixed effects:** unobserved station-level characteristics may bias estimates
4. **IRIS income proxy:** neighbourhood income ≠ income of drivers on nearby roads
5. **Station geocoding:** coordinates retrieved via Nominatim; precision affects spatial joins

---

## Stack

Python · pandas · geopandas · statsmodels · matplotlib · seaborn · Jupyter
