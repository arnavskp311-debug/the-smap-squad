---
name: interactive-dashboard-builder
description: Builds responsive, accessible, and high-performance interactive dashboards using Streamlit, Leaflet/Folium, Plotly, and React. Covers information hierarchy, state management, pin-drop spatial queries, multi-language localization (i18n), and real-time scenario simulation.
license: Apache-2.0
allowed-tools: Read Write Edit Bash Glob Grep
metadata:
  version: "1.0"
  skill-author: Antigravity UI & Data Visualization Team
---

# Interactive Dashboard Builder

Guidelines and patterns for building interactive, user-friendly scientific dashboards designed for farmers, researchers, and decision makers.

## Visual Hierarchy & Layout Guidelines

1. **Top Tier — KPI Cards**:
   - Current Water Stress Index (0–100) with color badge (Green: 0–30, Yellow: 31–60, Red: 61–100).
   - Soil Quality / Salinity Flag status (Normal vs Anomaly Alert).
   - 7-Day Rainfall & Soil Moisture Forecast overview.
2. **Core Tier — Interactive Map & Spatial Exploration**:
   - Leaflet / Mapbox map centered on the target region (e.g. Punjab, India: Bathinda, Ludhiana, Patiala).
   - District choropleths or gridded heatmaps of soil moisture / vegetation indices.
   - Click-to-query (pin-drop) event handling: clicking anywhere retrieves the coordinates and calculates the localized field score.
3. **Analytics Tier — Temporal Trends & Diagnostics**:
   - 30-Day historical slider comparing SMAP rootzone moisture against GPM rainfall and Landsat NDVI.
   - 7-Day machine learning forecast band (Random Forest / TimesFM quantile interval).
4. **Action & Advisory Drawer**:
   - Language toggle: English, Hindi (हिन्दी), Punjabi (ਪੰਜਾਬੀ).
   - Targeted agronomic advice (e.g. Direct Seeded Rice / DSR adoption, 3-day irrigation delay, mulching, gypsum application for sodic/alkaline soil).
   - Transparent data provenance badges ("Source: NASA SMAP, GPM IMERG, Landsat 8/9, NASA POWER").

## Streamlit + Folium/Leaflet Architecture

```python
import streamlit as st
from streamlit_folium import st_folium
import folium

def render_map(center_lat, center_lon, zoom=8):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    # Add district GeoJSON overlays and markers
    map_data = st_folium(m, height=450, width=700)
    # Extract clicked coordinates
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        return lat, lon
    return center_lat, center_lon
```

## Performance & Caching Rules
- Use `@st.cache_data` for raster I/O, heavy mathematical calculations, and API queries.
- Keep UI reactive: separate heavy ingestion from interactive filtering.
- Provide graceful offline/fallback modes with synthetic or pre-cached granules if network access is restricted.
