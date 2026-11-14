---
name: data-engineering-data-pipeline
description: Builds resilient, reproducible scientific data pipelines for geospatial and time-series data. Covers NASA Earthdata API ingestion (earthaccess), multidimensional raster processing (xarray, rasterio, rioxarray), spatial subsetting/masking with geopandas, feature engineering, and robust caching.
license: Apache-2.0
allowed-tools: Read Write Edit Bash Glob Grep
metadata:
  version: "1.0"
  skill-author: Antigravity Science & Data Team
---

# Data Engineering & Data Pipeline

Build modular, auditable, and resilient data processing pipelines for earth observation and environmental data.

## Core Principles

1. **Idempotence & Caching**: Every pipeline stage must be re-runnable without side effects. Cache intermediate API responses and clipped rasters locally (`data/raw`, `data/processed`).
2. **Strict CRS & Spatial Alignment**: Coordinate reference systems must match before any spatial join, zonal statistic, or raster mask. Reproject vector masks (`EPSG:4326` to local projected UTM `EPSG:32643`) before computing planar statistics.
3. **Chunking & Memory Safety**: Use chunked processing via `xarray`/`rioxarray`/`dask` to avoid Out-Of-Memory (OOM) failures when ingesting regional rasters.
4. **Data Contract & Lineage**: Every processed dataset must track its provenance (source satellite, granules, dates, processing parameters, and missing cell imputation strategy).

## Standard Earth Observation Pipeline Architecture

```text
[NASA Earthdata APIs / Providers]
       │
       ▼ (Step 1: Ingest)
[earthaccess / requests / power API] ──► raw cache (HDF5 / GeoTIFF / NetCDF)
       │
       ▼ (Step 2: Spatial Clip & Reproject)
[rioxarray / rasterio / geopandas] ──► processed district slices (UTM 43N)
       │
       ▼ (Step 3: Feature Engineering & Alignment)
[xarray / polars / numpy] ──► daily multi-band tabular matrix
       │
       ▼ (Step 4: Scoring & Diagnostic Engine)
[Water Stress Score (0-100) + SMAP-vs-NDVI Anomaly Detection]
```

## Recommended Implementation Standards

### Ingestion (`earthaccess` / NASA APIs)
```python
import earthaccess

def ingest_granules(short_name, bounding_box, temporal_range):
    # Authenticate via NASA Earthdata Login credentials or session token
    auth = earthaccess.login(strategy="environment") # or "interactive"
    results = earthaccess.search_data(
        short_name=short_name,
        bounding_box=bounding_box,
        temporal=temporal_range,
        count=100
    )
    # Download files to dedicated raw cache directory
    files = earthaccess.download(results, "./data/raw/")
    return files
```

### Raster Processing & District Masking (`rioxarray` & `geopandas`)
```python
import geopandas as gpd
import rioxarray
from shapely.geometry import mapping

def mask_to_district(raster_path, shapefile_path, district_name):
    gdf = gpd.read_file(shapefile_path)
    district_geom = gdf[gdf['district'] == district_name].geometry
    
    with rioxarray.open_rasterio(raster_path) as rds:
        # Match CRS
        if rds.rio.crs != gdf.crs:
            rds = rds.rio.reproject(gdf.crs)
        clipped = rds.rio.clip(district_geom.apply(mapping), gdf.crs, drop=True)
        return clipped
```
