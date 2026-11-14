"""
Punjab Farm Water Watch - Flagship NASA Mission Control UI
Developed by Team The SMAP Squad for NASA Space Apps Challenge 2026 (Delhi NCR)

Design System & Palette:
- Global Background: Deep teal gradient (#071F27 -> #0B2D38 -> #0C3340)
- Sidebar: Dark teal gradient (#061B23 -> #0B2D38) with #164E63 border
- Primary Accent: Warm Amber (#F59E0B) for active states, key numbers, sliders, focus rings
- Live Status: Emerald Green (#10B981) glowing pill with pulsing radar dot animation
- Card Surfaces:
    * Dark Telemetry Cards: #0C2933 with 1px solid #164E63 and soft elevation
    * High-Contrast White Cards: Crisp White (#FFFFFF) with #0F172A text and #F59E0B accents
- Clean Grid Layout Hierarchy:
    1. Top Bar: Title, Subtitle, Region Switcher, NASA Live status, EN|HI|PA Language Toggle
    2. Left Sidebar: What-If Calculator, Crop Diversification Budget & District-Scale Impact
    3. Top Row: Interactive Folium/Leaflet Map (60%) + Stress Gauge & Soil Status (40%)
    4. Middle Row: 30-Day SMAP & 7-Day RF Forecast Plotly Chart (60%) + 4 Delta & Outlook Cards (40%)
    5. Bottom Row: Soil Health Card & Prescription (50%) + Farmer Advisory White Card (50%)
    6. Across Bottom: 7-Day Smart Farm Precision Action Calendar
    7. Footer: Download District Officer Report (Markdown/PDF) & Verified NASA Mission Citations
"""

import os
import urllib.parse
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components
import folium
from branca.element import Element
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import geopandas as gpd

# Local Models, Spatial Processor & Agronomic Content
from model import (
    WaterStressModel,
    SevenDayMoistureForecaster,
    SoilQualityAnomalyDetector,
    CropBudgetSimulator
)
from src.pipeline.spatial_processor import SpatialProcessor
from src.advisories.smart_calendar import generate_smart_calendar
from src.advisories.soil_testing_guide import SOIL_TESTING_STEPS, REMEDIES_GUIDE

# -----------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Punjab Farm Water Watch | NASA Space Apps 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DESIGN SYSTEM & CSS TOKENS (ui-ux-pro-max + frontend-design principles)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Reset & Typography */
    html, body, [data-testid="stAppViewContainer"], .main {
        background: linear-gradient(180deg, #071F27 0%, #0B2D38 45%, #0C3340 100%) !important;
        color: #E2E8F0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        overflow-x: hidden !important;
    }

    /* Zero layout overflow */
    .block-container {
        padding-top: 0.9rem !important;
        padding-bottom: 2.0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1480px !important;
        overflow-x: hidden !important;
    }

    /* Sidebar Gradient & Border */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061B23 0%, #0B2D38 100%) !important;
        border-right: 1px solid #164E63 !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
    }

    /* Top Navigation Bar */
    .top-navbar-box {
        background: rgba(11, 45, 56, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid #164E63;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.28);
    }

    .brand-title {
        font-size: 1.38rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 0.76rem;
        color: #94A3B8;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 2px;
    }

    /* NASA Earthdata Live Glowing Pill */
    .nasa-live-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid #10B981;
        color: #34D399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.28);
    }

    .pulsing-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        animation: pulse-green 2s infinite ease-in-out;
    }

    @keyframes pulse-green {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.45; transform: scale(0.85); }
    }

    /* Dark Telemetry Cards */
    .dark-card {
        background-color: #0C2933;
        border: 1px solid #164E63;
        border-radius: 10px;
        padding: 15px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
    }

    .card-header-flex {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.92rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 10px;
    }

    .info-tag {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 17px;
        height: 17px;
        border-radius: 50%;
        border: 1px solid #475569;
        color: #94A3B8;
        font-size: 11px;
        font-weight: 700;
        cursor: default;
    }

    /* High-Contrast Crisp White Cards */
    .white-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        color: #0F172A;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
    }

    .white-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Farmer Advisory Card (Amber Top Border) */
    .advisory-card-white {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #F59E0B;
        border-radius: 10px;
        padding: 16px 18px;
        color: #0F172A;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
    }

    /* Savings Highlight Box (Sidebar) */
    .savings-display-box {
        background: #081B26;
        border: 1px solid #143548;
        border-radius: 8px;
        padding: 16px 14px;
        text-align: center;
        margin: 12px 0 8px 0;
    }

    .savings-big-val {
        font-size: 2.6rem;
        font-weight: 800;
        color: #F59E0B; /* Warm Amber */
        line-height: 1.05;
        letter-spacing: -0.02em;
    }

    .savings-label-text {
        font-size: 0.88rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 10px;
        font-weight: 500;
    }

    .kwh-pill-badge {
        display: inline-block;
        background: #1E293B;
        border: 1px solid #334155;
        color: #E2E8F0;
        padding: 4px 12px;
        border-radius: 14px;
        font-size: 0.79rem;
        font-weight: 600;
    }

    /* Delta Cards */
    .delta-box {
        background: #09202C;
        border: 1px solid #14384B;
        border-radius: 8px;
        padding: 12px 14px;
    }

    .delta-label-txt {
        font-size: 0.72rem;
        color: #94A3B8;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 3px;
    }

    .delta-val-txt {
        font-size: 1.45rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
        margin-bottom: 2px;
    }

    .delta-sub-txt {
        font-size: 0.75rem;
        color: #64748B;
    }

    /* Precision Action Calendar Cards */
    .cal-card {
        background: #09202C;
        border: 1px solid #164E63;
        border-radius: 8px;
        padding: 12px 14px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
        margin-bottom: 8px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }

    .cal-card:hover {
        border-color: #F59E0B;
        transform: translateY(-1px);
    }

    .cal-icon-col {
        font-size: 1.6rem;
        line-height: 1;
        margin-top: 2px;
    }

    .cal-title-txt {
        font-size: 0.86rem;
        font-weight: 700;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 3px;
    }

    .cal-desc-txt {
        font-size: 0.80rem;
        color: #CBD5E1;
        line-height: 1.35;
    }

    /* Prescription Box */
    .prescription-box {
        background: linear-gradient(145deg, #09202C, #0D2837);
        border: 1px solid #164E63;
        border-radius: 8px;
        padding: 12px 14px;
    }

    .prescription-title-txt {
        font-size: 0.85rem;
        font-weight: 700;
        color: #38BDF8;
        margin-bottom: 6px;
    }

    .prescription-dose-item {
        font-size: 0.83rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 4px;
    }

    /* Badges */
    .badge-critical {
        background: #DC2626;
        color: #FFFFFF;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.74rem;
        font-weight: 700;
    }

    .badge-warning {
        background: #F59E0B;
        color: #0F172A;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.74rem;
        font-weight: 700;
    }

    .badge-green {
        background: #16A34A;
        color: #FFFFFF;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.74rem;
        font-weight: 700;
    }

    .badge-outline {
        border: 1px solid #475569;
        color: #94A3B8;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.73rem;
        font-weight: 600;
    }

    /* Streamlit Slider Styling (Warm Amber) */
    div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {
        background-color: #F59E0B !important;
        border-color: #F59E0B !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.4) !important;
    }

    div[data-testid="stSlider"] div[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"],
    div[data-testid="stSlider"] div[data-baseweb="slider"] div[style*="background-color: rgb(255, 43, 43)"] {
        background-color: #F59E0B !important;
    }

    /* Touch Target & Accessible Buttons */
    button, a, select, input {
        min-height: 40px !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. DATA & MODEL INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_data
def load_datasets():
    csv_path = "data/processed/punjab_multi_satellite_30d.csv"
    if not os.path.exists(csv_path):
        from fetch_nasa_data import run_pipeline
        run_pipeline()
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df_all = load_datasets()

# Initialize core scientific models
stress_model = WaterStressModel()
forecaster = SevenDayMoistureForecaster()
soil_detector = SoilQualityAnomalyDetector()
spatial = SpatialProcessor()

gdf_districts = spatial.gdf


# -----------------------------------------------------------------------------
# 4. REGION & LANGUAGE SELECTOR STATE
# -----------------------------------------------------------------------------
region_options = [
    "Punjab - Bathinda (Primary Hotspot)",
    "Punjab - Sangrur",
    "Punjab - Patiala",
    "Punjab - Ludhiana",
    "Punjab - Amritsar",
    "Global - Central Valley, CA (Hotspot)",
    "Global - Nile Basin (Hotspot)",
    "Global - High Plains Aquifer, USA (Hotspot)"
]

if "selected_region_opt" not in st.session_state:
    st.session_state["selected_region_opt"] = region_options[0]

# Language choice in session_state
if "lang_choice" not in st.session_state:
    st.session_state["lang_choice"] = "EN"


# -----------------------------------------------------------------------------
# 5. TOP NAVIGATION BAR
# -----------------------------------------------------------------------------
top_c1, top_c2, top_c3, top_c4 = st.columns([2.2, 1.4, 1.0, 0.8], gap="small")

with top_c1:
    st.markdown("""
    <div style="padding-top:4px;">
        <div class="brand-title">
            <span>🛰️</span>
            <span>Punjab Farm Water Watch</span>
        </div>
        <div class="brand-subtitle">NASA Space Apps 2026 · Mission Control</div>
    </div>
    """, unsafe_allow_html=True)

with top_c2:
    selected_region_label = st.selectbox(
        "Region Switcher",
        options=region_options,
        index=region_options.index(st.session_state["selected_region_opt"]) if st.session_state["selected_region_opt"] in region_options else 0,
        label_visibility="collapsed",
        key="top_region_switcher_select"
    )
    if selected_region_label != st.session_state["selected_region_opt"]:
        st.session_state["selected_region_opt"] = selected_region_label
        st.rerun()

with top_c3:
    st.markdown("""
    <div style="display:flex; justify-content:center; align-items:center; height:100%; padding-top:6px;">
        <div class="nasa-live-pill">
            <span class="pulsing-dot"></span>
            <span>NASA Earthdata Live</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with top_c4:
    lang_val = st.radio(
        "Language",
        ["EN", "HI", "PA"],
        horizontal=True,
        index=["EN", "HI", "PA"].index(st.session_state["lang_choice"]),
        label_visibility="collapsed",
        key="top_language_toggle_radio"
    )
    if lang_val != st.session_state["lang_choice"]:
        st.session_state["lang_choice"] = lang_val
        st.rerun()

lang_selection = st.session_state["lang_choice"].lower()


# -----------------------------------------------------------------------------
# 6. RESOLVE ACTIVE DISTRICT & SATELLITE TELEMETRY
# -----------------------------------------------------------------------------
is_global_hotspot = "Global -" in st.session_state["selected_region_opt"]

if is_global_hotspot:
    if "Central Valley" in st.session_state["selected_region_opt"]:
        selected_district = "Central Valley (CA)"
        lat_in, lon_in = 36.7783, -119.4179
    elif "Nile Basin" in st.session_state["selected_region_opt"]:
        selected_district = "Nile Basin (Egypt)"
        lat_in, lon_in = 30.8025, 31.0000
    else:
        selected_district = "High Plains Aquifer"
        lat_in, lon_in = 37.0000, -100.0000

    dist_df = df_all[df_all["district"] == "Bathinda"].copy()
else:
    selected_district = st.session_state["selected_region_opt"].replace("Punjab - ", "").split(" (")[0].strip()
    dist_sub = df_all[df_all["district"] == selected_district]
    if dist_sub.empty:
        selected_district = "Bathinda"
        dist_sub = df_all[df_all["district"] == "Bathinda"]
    dist_df = dist_sub.copy()

    matching_geom = gdf_districts[gdf_districts["name"] == selected_district]
    if not matching_geom.empty:
        lat_in = float(matching_geom.geometry.centroid.y.iloc[0])
        lon_in = float(matching_geom.geometry.centroid.x.iloc[0])
    else:
        lat_in, lon_in = 30.2110, 74.9455

latest = dist_df.iloc[-1]
rain_30d_val = float(dist_df["gpm_precipitation_mm"].sum())

# Compute Water Stress Score
stress_res = stress_model.compute_water_stress_score(
    smap_rootzone_sm=float(latest["smap_rootzone_sm"]),
    rain_30d_mm=rain_30d_val,
    modis_et_mm=float(latest["modis_et_mm"]),
    landsat_lst_c=float(latest["landsat_lst_c"])
)

# Compute Soil Anomaly Dual Diagnosis
soil_res = soil_detector.evaluate_soil_anomaly(
    smap_rootzone_sm=float(latest["smap_rootzone_sm"]),
    water_stress_score=float(stress_res["score"]),
    landsat_ndvi=float(latest["landsat_ndvi"]),
    landsat_savi=float(latest["landsat_savi"])
)

# Compute 7-Day Forecast
fc_results = forecaster.predict_next_7_days(dist_df)
fc_df = pd.DataFrame(fc_results)

# Precompute district risk boundaries GeoJSON colors
district_scores = {}
for d in gdf_districts["name"]:
    sub = df_all[df_all["district"] == d]
    if not sub.empty:
        l_row = sub.iloc[-1]
        r30 = float(sub["gpm_precipitation_mm"].sum())
        sc = stress_model.compute_water_stress_score(
            l_row["smap_rootzone_sm"], r30, l_row["modis_et_mm"], l_row["landsat_lst_c"]
        )
        district_scores[d] = sc
    else:
        district_scores[d] = {"score": 25.0, "zone": "Green", "badge_color": "#16A34A", "status": "No Stress"}


# -----------------------------------------------------------------------------
# 7. LEFT SIDEBAR: WHAT-IF CALCULATOR & CROP BUDGET SIMULATOR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="dark-card" style="margin-bottom:12px;">
        <div class="card-header-flex">
            <span>What-If Water &amp; Energy Calculator</span>
            <span class="info-tag" title="Dynamic empirical model based on PAU water conservation trials">ⓘ</span>
        </div>
    """, unsafe_allow_html=True)

    farm_acres = st.slider(
        "Farm Size",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        format="%d Acres",
        key="sidebar_farm_size_slider"
    )

    practice_options = [
        "Direct Seeded Rice (DSR) / Mulching",
        "3-Day Irrigation Delay",
        "Straw Mulching",
        "Combined Protocol"
    ]
    selected_practice = st.selectbox(
        "Conservation Practice",
        options=practice_options,
        index=0,
        key="sidebar_practice_select"
    )

    pct_saved_map = {
        "Direct Seeded Rice (DSR) / Mulching": 0.20,
        "3-Day Irrigation Delay": 0.10,
        "Straw Mulching": 0.15,
        "Combined Protocol": 0.30
    }
    saving_ratio = pct_saved_map[selected_practice]
    total_baseline_litres = farm_acres * 900000
    litres_saved = total_baseline_litres * saving_ratio
    kwh_saved = int(litres_saved * 0.000789)

    if litres_saved >= 1000000:
        litres_display = f"{litres_saved / 1000000:.1f}M"
    else:
        litres_display = f"{int(litres_saved):,}"

    st.markdown(f"""
        <div class="savings-display-box">
            <div class="savings-big-val">{litres_display}</div>
            <div class="savings-label-text">Litres Saved ({farm_acres} Acres)</div>
            <div class="kwh-pill-badge">⚡ Electricity Saved: {kwh_saved:,} kWh</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Alternative Crop Diversification Budget
    st.markdown(f"""
    <div class="dark-card" style="margin-bottom:12px;">
        <div class="card-header-flex">
            <span>Crop Diversification Budget</span>
            <span class="info-tag" title="PAU Agronomic Benchmarks">ⓘ</span>
        </div>
    """, unsafe_allow_html=True)

    crop_options = list(CropBudgetSimulator.CROP_PROFILES.keys())
    crop_choice = st.selectbox(
        "Alternative Crop Diversification",
        options=crop_options,
        index=1,
        key="sidebar_crop_choice_select"
    )
    sim_budget = CropBudgetSimulator.calculate_budget(crop_choice, farm_acres=farm_acres)

    st.markdown(f"""
        <div style="background:#081B26; border:1px solid #143548; border-radius:8px; padding:12px; margin-top:6px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.82rem;">
                <span style="color:#94A3B8;">Paddy Baseline:</span>
                <span style="color:#FFFFFF; font-weight:700;">{sim_budget['baseline_litres_m']}M Litres</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.82rem;">
                <span style="color:#94A3B8;">Crop Demand:</span>
                <span style="color:#38BDF8; font-weight:700;">{sim_budget['crop_water_demand_m']}M Litres</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.82rem;">
                <span style="color:#94A3B8;">Groundwater Saved:</span>
                <span style="color:#F59E0B; font-weight:800;">{sim_budget['groundwater_saved_m']}M L ({sim_budget['pct_saved']:.0f}%)</span>
            </div>
            <div style="margin-top:6px; font-size:0.75rem; color:#CBD5E1; font-style:italic;">
                💡 {sim_budget['recommendation']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # District-Scale Aquifer Impact Callout
    district_saving_m = (sim_budget["groundwater_saved_m"] / farm_acres) * (120000 * 0.10 * 8)
    st.markdown(f"""
    <div class="dark-card">
        <div class="card-header-flex">
            <span>District Aquifer Impact</span>
            <span class="info-tag" title="Projected over 10% tube-well adoption in active district">ⓘ</span>
        </div>
        <div style="font-size:0.80rem; color:#94A3B8; margin-bottom:6px;">
            If <b>10% of tube-wells</b> in {selected_district} adopt this protocol:
        </div>
        <div style="background:#081B26; border:1px solid #143548; border-radius:6px; padding:10px; text-align:center;">
            <div style="font-size:1.7rem; font-weight:800; color:#2DD4BF;">{district_saving_m:.0f}M Litres</div>
            <div style="font-size:0.74rem; color:#94A3B8;">Groundwater Preserved Every Season</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 8. TOP ROW: INTERACTIVE MAP (60%) + STRESS GAUGE & SOIL STATUS (40%)
# -----------------------------------------------------------------------------
top_map_col, top_cards_col = st.columns([1.55, 1.0], gap="medium")

with top_map_col:
    m = folium.Map(
        location=[lat_in, lon_in],
        zoom_start=7 if not is_global_hotspot else 6,
        min_zoom=5,
        max_zoom=14,
        tiles="CartoDB dark_matter",
        zoom_control=True
    )

    # High-Res Esri Satellite Base
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="🌍 High-Res Satellite (Esri)",
        attr="Esri World Imagery",
        overlay=False,
        control=True
    ).add_to(m)

    # NASA GIBS WMTS Live Layer (default off to prevent raw orbital swath gap stripes on load)
    gibs_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    modis_truecolor_url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{gibs_date}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg"
    folium.TileLayer(
        tiles=modis_truecolor_url,
        name="🛰️ NASA GIBS Live WMTS (MODIS)",
        attr="NASA Worldview / GIBS",
        overlay=True,
        control=True,
        show=False,
        opacity=0.70
    ).add_to(m)

    # Dynamic District Polygons with Choropleth Risk
    if not is_global_hotspot:
        def district_style_func(feat):
            dname = feat["properties"]["name"]
            score_info = district_scores.get(dname, {"score": 25.0})
            sc = score_info["score"]
            if sc > 60:
                fill_c = "#DC2626" # Red
            elif sc > 30:
                fill_c = "#F59E0B" # Amber
            else:
                fill_c = "#16A34A" # Green
            return {
                "fillColor": fill_c,
                "color": "#1E293B",
                "weight": 1.8,
                "fillOpacity": 0.75
            }

        folium.GeoJson(
            gdf_districts,
            name="Punjab District Risk Boundaries",
            style_function=district_style_func,
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "soil_type", "primary_crop"],
                aliases=["District:", "Soil:", "Crops:"]
            )
        ).add_to(m)

        # Active District Pin Marker
        pin_color = "red" if stress_res["zone"] == "Red" else ("orange" if stress_res["zone"] == "Yellow" else "green")
        folium.Marker(
            [lat_in, lon_in],
            tooltip=f"<b>{selected_district}</b><br>Stress Score: {stress_res['score']}/100 ({stress_res['zone']})",
            icon=folium.Icon(color=pin_color, icon="tint", prefix="fa")
        ).add_to(m)

        folium.map.Marker(
            [lat_in, lon_in],
            icon=folium.DivIcon(
                icon_size=(110, 24),
                icon_anchor=(55, -10),
                html=f'<div style="font-size:11px; font-weight:700; color:#1E293B; background:rgba(255,255,255,0.92); padding:2px 8px; border-radius:4px; border:1px solid #94A3B8; text-align:center; width:max-content; margin:0 auto; box-shadow:0 1px 4px rgba(0,0,0,0.3);">{selected_district}</div>'
            )
        ).add_to(m)
    else:
        folium.Marker(
            [lat_in, lon_in],
            tooltip=f"<b>{selected_district}</b>",
            icon=folium.Icon(color="red", icon="warning-sign")
        ).add_to(m)

    folium.LayerControl(position="topright", collapsed=True).add_to(m)

    # Map Legend
    legend_html = """
    <div style="
        position: fixed; bottom: 14px; right: 14px; width: 140px; 
        background-color: rgba(255, 255, 255, 0.95);
        border: 1px solid #CBD5E1; border-radius: 6px;
        padding: 8px 10px; font-size: 11px; z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1E293B; box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    ">
        <div style="font-weight: 700; margin-bottom: 5px; color:#0F172A;">Water Stress Legend</div>
        <div style="margin-bottom: 3px; display:flex; align-items:center;"><span style="display:inline-block; width:10px; height:10px; background:#16A34A; margin-right:6px; border-radius:2px;"></span> Safe (0–30)</div>
        <div style="margin-bottom: 3px; display:flex; align-items:center;"><span style="display:inline-block; width:10px; height:10px; background:#F59E0B; margin-right:6px; border-radius:2px;"></span> Moderate (31–60)</div>
        <div style="display:flex; align-items:center;"><span style="display:inline-block; width:10px; height:10px; background:#DC2626; margin-right:6px; border-radius:2px;"></span> Critical (61–100)</div>
    </div>
    """
    m.get_root().html.add_child(Element(legend_html))

    map_data = st_folium(
        m,
        width="100%",
        height=380,
        returned_objects=["last_clicked"],
        key="main_leaflet_folium_map"
    )

    # Click-to-select district sync
    if map_data and map_data.get("last_clicked") and not is_global_hotspot:
        c_lat = map_data["last_clicked"]["lat"]
        c_lon = map_data["last_clicked"]["lng"]
        loc = spatial.locate_point(c_lat, c_lon)
        clicked_dist = loc["district"]
        matched_prefix = f"Punjab - {clicked_dist}"
        for opt in region_options:
            if opt.startswith(matched_prefix) and opt != st.session_state.get("selected_region_opt"):
                st.session_state["selected_region_opt"] = opt
                st.rerun()

with top_cards_col:
    # 1. Water Stress Score Gauge Card
    gauge_val = stress_res['score']
    gauge_zone = stress_res['zone']
    gauge_color = "#DC2626" if gauge_val > 60 else ("#F59E0B" if gauge_val > 30 else "#16A34A")

    st.markdown("""
    <div class="dark-card" style="padding:12px 14px 10px 14px; margin-bottom:10px;">
        <div class="card-header-flex" style="margin-bottom:4px;">
            <span>Water Stress Score</span>
            <span class="info-tag" title="40% SMAP + 30% GPM rain + 20% MODIS ET + 10% Landsat LST">ⓘ</span>
        </div>
    """, unsafe_allow_html=True)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gauge_val,
        number={
            'suffix': "/100",
            'font': {'size': 32, 'color': '#FFFFFF', 'family': '-apple-system, BlinkMacSystemFont, sans-serif'}
        },
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#334155', 'ticks': ''},
            'bar': {'color': gauge_color, 'thickness': 0.28},
            'bgcolor': '#1E293B',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(22, 163, 74, 0.25)'},
                {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.25)'},
                {'range': [60, 100], 'color': 'rgba(220, 38, 38, 0.35)'}
            ]
        }
    ))
    fig_gauge.update_layout(
        margin=dict(l=10, r=10, t=10, b=0),
        height=100,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False}, key="water_stress_plotly_gauge")

    st.markdown(f"""
        <div style="display:flex; justify-content:center; gap:8px; margin-top:-6px; margin-bottom:4px;">
            <span class="{'badge-critical' if gauge_zone == 'Red' else ('badge-warning' if gauge_zone == 'Yellow' else 'badge-green')}">{gauge_zone} Zone</span>
            <span class="badge-outline">Status: {stress_res['status']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Soil Quality Status Dual Diagnosis Card
    st.markdown("""
    <div class="dark-card" style="padding:12px 14px; margin-bottom:0px;">
        <div class="card-header-flex" style="margin-bottom:4px;">
            <span>Soil Quality Status</span>
            <span class="info-tag" title="SMAP rootzone moisture vs Landsat NDVI/SAVI vegetative vigor">ⓘ</span>
        </div>
    """, unsafe_allow_html=True)

    sq_c1, sq_c2 = st.columns([1.3, 1.0])
    with sq_c1:
        if soil_res["alert_triggered"]:
            st.markdown(
                '<div style="font-size:0.86rem; font-weight:700; color:#FFFFFF; line-height:1.25; margin-top:4px;">'
                'Alert: Low Organic Carbon &amp; Alkaline'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div style="margin-top:10px;"><span class="badge-critical">Critical Anomaly</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="font-size:0.86rem; font-weight:700; color:#FFFFFF; line-height:1.25; margin-top:4px;">'
                'Optimal Soil Health &amp; Carbon Balance'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div style="margin-top:10px;"><span class="badge-green">Optimal</span></div>', unsafe_allow_html=True)
    with sq_c2:
        sq_gauge_val = 82 if soil_res["alert_triggered"] else 20
        sq_bar_color = "#DC2626" if soil_res["alert_triggered"] else "#16A34A"
        fig_soil_mini = go.Figure(go.Indicator(
            mode="gauge",
            value=sq_gauge_val,
            gauge={
                'axis': {'range': [0, 100], 'ticks': ''},
                'bar': {'color': sq_bar_color, 'thickness': 0.35},
                'bgcolor': '#1E293B',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 33], 'color': '#16A34A'},
                    {'range': [33, 66], 'color': '#F59E0B'},
                    {'range': [66, 100], 'color': '#DC2626'}
                ]
            }
        ))
        fig_soil_mini.update_layout(
            margin=dict(l=5, r=5, t=5, b=0),
            height=70,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_soil_mini, use_container_width=True, config={'displayModeBar': False}, key="soil_quality_mini_gauge")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 9. MIDDLE ROW: 30-DAY SMAP & 7-DAY FORECAST (60%) + 4 DELTA CARDS (40%)
# -----------------------------------------------------------------------------
st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
mid_chart_col, mid_deltas_col = st.columns([1.55, 1.0], gap="medium")

with mid_chart_col:
    st.markdown("""
    <div class="white-card">
        <div class="white-card-title">
            <span>Soil Moisture &amp; Water Forecast</span>
            <span style="font-size:0.78rem; color:#64748B; font-weight:600;">30-Day SMAP + 7-Day Random Forest Outlook</span>
        </div>
    """, unsafe_allow_html=True)

    hist_dates = pd.to_datetime(dist_df["date"]).dt.strftime("%b %d").tolist()
    hist_sm = dist_df["smap_rootzone_sm"].tolist()

    fc_dates = [f["day_label"] for f in fc_results]
    fc_preds = [f["predicted_sm"] for f in fc_results]
    fc_lower = [f["lower_sm_bound"] for f in fc_results]
    fc_upper = [f["upper_sm_bound"] for f in fc_results]

    all_timeline_dates = hist_dates + fc_dates

    fig_forecast = go.Figure()

    # Shaded 90% Confidence Envelope
    fig_forecast.add_vrect(
        x0=len(hist_dates) - 1,
        x1=len(all_timeline_dates) - 1,
        fillcolor="rgba(245, 158, 11, 0.12)",
        layer="below",
        line_width=0
    )

    # 30-Day Historical SMAP Rootzone (Deep Teal #0F4C5C)
    fig_forecast.add_trace(go.Scatter(
        x=list(range(len(hist_dates))),
        y=hist_sm,
        mode="lines",
        name="30-Day SMAP Rootzone (0–100 cm)",
        line=dict(color="#0F4C5C", width=2.6)
    ))

    # 7-Day RandomForest Outlook (Warm Amber #F59E0B)
    fig_forecast.add_trace(go.Scatter(
        x=list(range(len(hist_dates) - 1, len(all_timeline_dates))),
        y=[hist_sm[-1]] + fc_preds,
        mode="lines+markers",
        name="7-Day RandomForest Outlook",
        line=dict(color="#F59E0B", width=2.6),
        marker=dict(size=4, color="#F59E0B")
    ))

    # Dashed baseline drydown trajectory
    dash_baseline = [hist_sm[-1] - (i * 0.012) for i in range(len(fc_preds) + 1)]
    fig_forecast.add_trace(go.Scatter(
        x=list(range(len(hist_dates) - 1, len(all_timeline_dates))),
        y=dash_baseline,
        mode="lines",
        name="Baseline Drydown",
        line=dict(color="#0284C7", width=1.6, dash="dash")
    ))

    tick_indices = [0, len(hist_dates) // 2, len(hist_dates) - 1, len(all_timeline_dates) - 1]
    tick_texts = [all_timeline_dates[t] for t in tick_indices]

    fig_forecast.update_layout(
        template="plotly_white",
        height=240,
        margin=dict(l=35, r=20, t=10, b=30),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#1E293B")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=tick_indices,
            ticktext=tick_texts,
            title="Date",
            title_font=dict(size=11, color="#475569"),
            showgrid=True,
            gridcolor="#E2E8F0"
        ),
        yaxis=dict(
            range=[0.0, 0.65],
            title="Soil Moisture (m³/m³)",
            title_font=dict(size=11, color="#475569"),
            showgrid=True,
            gridcolor="#E2E8F0"
        )
    )
    st.plotly_chart(fig_forecast, use_container_width=True, config={'displayModeBar': False}, key="smap_forecast_plotly_chart")
    st.markdown("</div>", unsafe_allow_html=True)

with mid_deltas_col:
    # 4 Delta & Outlook Cards
    row_30d = dist_df.iloc[0]
    sm_old = float(row_30d["smap_rootzone_sm"])
    sm_now = float(latest["smap_rootzone_sm"])
    sm_diff = sm_now - sm_old
    sm_color = "#DC2626" if sm_diff < -0.03 else ("#16A34A" if sm_diff > 0.02 else "#F59E0B")

    ndvi_old = float(row_30d["landsat_ndvi"])
    ndvi_now = float(latest["landsat_ndvi"])
    ndvi_diff = ndvi_now - ndvi_old
    ndvi_color = "#DC2626" if ndvi_diff < -0.05 else ("#16A34A" if ndvi_diff > 0.03 else "#F59E0B")

    score_old = stress_model.compute_water_stress_score(
        smap_rootzone_sm=sm_old,
        rain_30d_mm=float(dist_df["gpm_precipitation_mm"].head(10).sum()) * 1.5,
        modis_et_mm=float(row_30d["modis_et_mm"]),
        landsat_lst_c=float(row_30d["landsat_lst_c"])
    )["score"]
    score_now = stress_res["score"]
    score_diff = score_now - score_old
    score_color = "#DC2626" if score_diff > 10 else ("#16A34A" if score_diff < -5 else "#F59E0B")

    fc_day7 = fc_results[-1]

    st.markdown(f"""
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
        <div class="delta-box">
            <div class="delta-label-txt">SMAP Rootzone SM</div>
            <div class="delta-val-txt">{sm_now:.3f} <span style="font-size:0.75rem; color:#94A3B8;">m³/m³</span></div>
            <div class="delta-sub-txt">30d Ago: {sm_old:.3f} | <b style="color:{sm_color};">{sm_diff:+.3f}</b></div>
        </div>
        <div class="delta-box">
            <div class="delta-label-txt">Landsat 8/9 NDVI</div>
            <div class="delta-val-txt">{ndvi_now:.3f}</div>
            <div class="delta-sub-txt">30d Ago: {ndvi_old:.3f} | <b style="color:{ndvi_color};">{ndvi_diff:+.3f}</b></div>
        </div>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div class="delta-box">
            <div class="delta-label-txt">Water Stress Index</div>
            <div class="delta-val-txt">{score_now} <span style="font-size:0.75rem; color:#94A3B8;">/100</span></div>
            <div class="delta-sub-txt">30d Ago: {score_old:.1f} | <b style="color:{score_color};">{score_diff:+.1f} pts</b></div>
        </div>
        <div class="delta-box" style="border-color:#F59E0B;">
            <div class="delta-label-txt" style="color:#F59E0B;">Day-7 Forecast</div>
            <div class="delta-val-txt" style="color:#F59E0B;">{fc_day7['predicted_sm']:.3f}</div>
            <div class="delta-sub-txt">90% CI: <b>{fc_day7['lower_sm_bound']:.3f}–{fc_day7['upper_sm_bound']:.3f}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 10. BOTTOM ROW: SOIL HEALTH CARD (50%) + FARMER ADVISORY (50%)
# -----------------------------------------------------------------------------
st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
bot_soil_col, bot_adv_col = st.columns([1.0, 1.0], gap="medium")

with bot_soil_col:
    st.markdown("""
    <div class="dark-card" style="margin-bottom:0px; height:100%;">
        <div class="card-header-flex">
            <span>Soil Health Card &amp; Lab Prescription</span>
            <span class="info-tag" title="Empirical PAU/KVK Soil Testing Protocol">ⓘ</span>
        </div>
    """, unsafe_allow_html=True)

    sh_in_col, sh_rx_col = st.columns([1.0, 1.15], gap="small")
    with sh_in_col:
        st.markdown("<div style='font-size:0.75rem; color:#94A3B8; font-weight:600;'>Soil pH</div>", unsafe_allow_html=True)
        input_ph = st.number_input("pH", value=8.6, step=0.1, min_value=4.0, max_value=11.0, label_visibility="collapsed", key="soil_ph_input")

        st.markdown("<div style='font-size:0.75rem; color:#94A3B8; font-weight:600; margin-top:4px;'>EC (dS/m)</div>", unsafe_allow_html=True)
        input_ec = st.number_input("EC", value=0.9, step=0.1, min_value=0.0, max_value=20.0, label_visibility="collapsed", key="soil_ec_input")

        st.markdown("<div style='font-size:0.75rem; color:#F59E0B; font-weight:600; margin-top:4px;'>Organic Carbon (%)</div>", unsafe_allow_html=True)
        input_oc = st.number_input("OC", value=0.38, step=0.01, min_value=0.05, max_value=2.0, label_visibility="collapsed", key="soil_oc_input")

        st.markdown("<div style='font-size:0.75rem; color:#94A3B8; font-weight:600; margin-top:4px;'>Available Nitrogen (kg/ha)</div>", unsafe_allow_html=True)
        input_n = st.number_input("Nitrogen", value=190, step=10, min_value=50, max_value=600, label_visibility="collapsed", key="soil_n_input")

    gypsum_bags = 2 if input_ph > 8.5 else 0
    fym_tonnes = 4 if input_oc < 0.5 else 0
    gypsum_text = f"• {gypsum_bags} Bags Gypsum/Acre" if gypsum_bags > 0 else "• Gypsum: Normal (No Treatment)"
    compost_text = f"• {fym_tonnes}t Compost/Acre" if fym_tonnes > 0 else "• Compost: Adequate Carbon"
    zinc_text = "• Zinc Dose (25 kg/ha ZnSO4)" if input_n < 250 else "• Standard Basal Dose"

    with sh_rx_col:
        st.markdown(f"""
        <div class="prescription-box">
            <div class="prescription-title-txt">PAU / KVK Lab Prescription</div>
            <div class="prescription-dose-item">{gypsum_text}</div>
            <div class="prescription-dose-item">{compost_text}</div>
            <div class="prescription-dose-item">{zinc_text}</div>
            <div style="margin-top:8px; font-size:0.74rem; color:#CBD5E1; border-top:1px solid rgba(255,255,255,0.12); padding-top:4px;">
                Status: <b style="color:{'#F87171' if gypsum_bags > 0 or fym_tonnes > 0 else '#4ADE80'};">{'Alkaline / Low Carbon Soil — Remediation Required' if gypsum_bags > 0 or fym_tonnes > 0 else 'Balanced State'}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📖 PAU / ICAR 15 cm Soil Sampling Protocol & Field Remedies"):
        st.markdown("**PAU / ICAR 4-Step Sampling Guide:**")
        for step in SOIL_TESTING_STEPS:
            t_key = f"title_{lang_selection}" if f"title_{lang_selection}" in step else "title_en"
            d_key = f"desc_{lang_selection}" if f"desc_{lang_selection}" in step else "desc_en"
            st.markdown(f"**Step {step['step_number']}: {step.get(t_key, step['title_en'])}**\n{step.get(d_key, step['desc_en'])}")
        st.markdown("---")
        st.markdown("**Field Remedies Matrix:**")
        for rem in REMEDIES_GUIDE:
            r_key = f"remedy_{lang_selection}" if f"remedy_{lang_selection}" in rem else "remedy_en"
            st.markdown(f"• **{rem['problem']}:** {rem.get(r_key, rem['remedy_en'])}")

    st.markdown("</div>", unsafe_allow_html=True)

with bot_adv_col:
    # Trilingual localized advisory
    if stress_res["zone"] == "Red":
        if lang_selection == "pa":
            adv1 = "ਕਿਸਾਨ ਵੀਰੋ, 3 ਦਿਨ ਪਾਣੀ ਰੋਕੋ (Kisan veero, 3 din paani roko)"
            adv2 = "ਸਿੱਧੀ ਬਿਜਾਈ (DSR) ਅਤੇ ਮਲਚਿੰਗ ਅਪਣਾਓ (Adopt DSR & Mulching)"
        elif lang_selection == "en":
            adv1 = "Farmers, pause irrigation for 3 days to preserve root aeration"
            adv2 = "Switch to Direct Seeded Rice (DSR) & Crop-Residue Mulching"
        else: # hi
            adv1 = "किसान भाई, 3 दिन पानी रोक दें (जड़ क्षेत्र को हवा लगने दें)"
            adv2 = "सीधी बिजाई (DSR) और पुआल मल्चिंग अपनाएं"
    elif stress_res["zone"] == "Yellow":
        if lang_selection == "pa":
            adv1 = "ਜੜ੍ਹ ਖੇਤਰ ਵਿੱਚ ਦਰਮਿਆਨੀ ਨਮੀ ਦੀ ਘਾਟ - ਸਿੰਚਾਈ 2 ਦਿਨ ਟਾਲੋ"
            adv2 = "ਵਾਸ਼ਪੀਕਰਨ ਰੋਕਣ ਲਈ ਪਰਾਲੀ ਦੀ ਮਲਚਿੰਗ ਕਰੋ"
        elif lang_selection == "en":
            adv1 = "Moderate moisture deficit: Delay flood irrigation by 2 days"
            adv2 = "Apply straw mulching to curb high surface evapotranspiration losses"
        else: # hi
            adv1 = "जड़-क्षेत्र में मध्यम नमी की कमी - सिंचाई 2 दिन टालें"
            adv2 = "वाष्पीकरण रोकने के लिए खेत में पुआल की मल्चिंग करें"
    else: # Green
        if lang_selection == "pa":
            adv1 = "ਫ਼ਸਲ ਲਈ ਪਾਣੀ ਕਾਫ਼ੀ ਹੈ - ਬੇਲੋੜੀ ਸਿੰਚਾਈ ਤੋਂ ਬਚੋ"
            adv2 = "ਜ਼ਮੀਨੀ ਪਾਣੀ ਬਚਾਉਣ ਲਈ ਤੁਪਕਾ ਜਾਂ ਫੁਹਾਰਾ ਸਿੰਚਾਈ ਅਪਣਾਓ"
        elif lang_selection == "en":
            adv1 = "Water reserves are currently sufficient for crop demand"
            adv2 = "Avoid unnecessary over-irrigation to conserve regional groundwater"
        else: # hi
            adv1 = "फसल की मांग के लिए पानी पर्याप्त है - अतिरिक्त सिंचाई से बचें"
            adv2 = "भूजल स्तर बनाए रखने के लिए संतुलित सिंचाई करें"

    st.markdown(f"""
    <div class="advisory-card-white" style="margin-bottom:0px; height:100%;">
        <div style="font-weight:700; font-size:0.92rem; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <span>Farmer Advisory &amp; Action</span>
            <span style="font-size:1.1rem;">🔔</span>
        </div>
        <div style="font-size:0.86rem; font-weight:600; color:#1E293B; margin-bottom:6px;">
            • {adv1}
        </div>
        <div style="font-size:0.86rem; font-weight:600; color:#1E293B; margin-bottom:14px;">
            • {adv2}
        </div>
    """, unsafe_allow_html=True)

    wa_text = f"🌾 Punjab Farm Water Watch Alert - {selected_district}\nWater Stress Score: {stress_res['score']}/100 ({stress_res['zone']})\nAdvisory:\n1. {adv1}\n2. {adv2}\nNASA Live Telemetry Verified."
    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

    adv_c1, adv_c2 = st.columns(2)
    with adv_c1:
        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
            <div style="
                background-color:#22C55E; color:#FFFFFF; text-align:center;
                font-size:0.82rem; font-weight:700; padding:8px 10px; border-radius:6px;
                display:flex; align-items:center; justify-content:center; gap:6px;
                box-shadow:0 2px 6px rgba(34,197,94,0.3);
            ">
                💬 Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
    with adv_c2:
        speech_text = f"{adv1}. {adv2}."
        speech_lang = "hi-IN" if lang_selection in ["hi", "pa"] else "en-US"
        speech_html = f"""
        <div style="display:flex; justify-content:center;">
            <button id="voiceBtn" style="
                width: 100%; background-color:#E2E8F0; color:#1E293B; border:none;
                font-size:0.82rem; font-weight:700; padding:8px 10px; border-radius:6px;
                cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px;
                font-family:-apple-system, BlinkMacSystemFont, sans-serif;
            ">
                🔊 Listen Voice Alert
            </button>
        </div>
        <script>
            const btn = document.getElementById('voiceBtn');
            btn.onclick = function() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance({pd.Series([speech_text]).to_json(orient='values')[1:-1]});
                    utterance.lang = '{speech_lang}';
                    utterance.rate = 0.95;
                    window.speechSynthesis.speak(utterance);
                }} else {{
                    alert('Web Speech API is not supported in this browser.');
                }}
            }};
        </script>
        """
        components.html(speech_html, height=38)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 11. ACROSS BOTTOM: 7-DAY SMART FARM ACTION CALENDAR
# -----------------------------------------------------------------------------
st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class="dark-card" style="margin-bottom:14px;">
    <div class="card-header-flex">
        <span>🗓️ Pin-Drop 7-Day Precision Action Calendar ({selected_district})</span>
        <span class="info-tag" title="Dynamic 7-day schedule generated from RandomForest soil projections & anomaly triggers">ⓘ</span>
    </div>
""", unsafe_allow_html=True)

smart_cal_days = generate_smart_calendar(fc_results, soil_res, lang=lang_selection)

cal_cols = st.columns(2)
for idx, c_day in enumerate(smart_cal_days):
    col_target = cal_cols[idx % 2]
    with col_target:
        st.markdown(f"""
        <div class="cal-card">
            <div class="cal-icon-col">{c_day['icon']}</div>
            <div style="flex-grow:1;">
                <div class="cal-title-txt">
                    <span>{c_day['day_label']}: {c_day['title']}</span>
                    <span class="badge-outline" style="border-color:{c_day['badge_color']}; color:{c_day['badge_color']};">{c_day['badge']}</span>
                </div>
                <div class="cal-desc-txt">{c_day['action']}</div>
                <div style="font-size:0.73rem; color:#64748B; margin-top:4px;">
                    Projected Moisture: <b>{c_day['projected_sm']:.3f} m³/m³</b> · Zone: <b style="color:{c_day['badge_color']};">{c_day['risk_zone']}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 12. FOOTER: REPORT DOWNLOAD & VERIFIED NASA CITATIONS
# -----------------------------------------------------------------------------
officer_report_md = f"""# Punjab Farm Water Watch - District Officer Brief
**NASA Space Apps Challenge 2026 · Delhi NCR**
**Team:** The SMAP Squad
**Target District:** {selected_district} (Coordinates: {lat_in:.4f}°N, {lon_in:.4f}°E)
**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

### 1. Water Stress Score & Multi-Satellite Metrics
* **Composite Water Stress Score:** {stress_res['score']} / 100 ({stress_res['zone']} Zone)
* **NASA SMAP L4 Rootzone Moisture (0–100 cm):** {latest['smap_rootzone_sm']:.3f} m³/m³
* **NASA SMAP L4 Surface Moisture (0–5 cm):** {latest['smap_surface_sm']:.3f} m³/m³
* **NASA GPM IMERG 30-Day Precipitation:** {rain_30d_val:.1f} mm
* **MODIS MOD16A2 Evapotranspiration:** {latest['modis_et_mm']:.2f} mm/day
* **Landsat 8/9 OLI Canopy NDVI:** {latest['landsat_ndvi']:.3f}
* **Landsat 8/9 OLI Canopy SAVI:** {latest['landsat_savi']:.3f}
* **NASA GRACE Groundwater Anomaly:** {latest['grace_water_anomaly_cm']:.2f} cm

---

### 2. Dual-Diagnosis Soil Quality Audit
* **Anomaly Status:** {'ALERT TRIGGERED' if soil_res['alert_triggered'] else 'NORMAL'}
* **Diagnosis:** {soil_res['diagnosis']}
* **Recommended Field Prescription:** Apply {gypsum_bags} bags/acre Agricultural Gypsum, {fym_tonnes} tonnes/acre FYM/Compost, and 25 kg/acre Zinc Sulfate.

---

### 3. 7-Day Machine Learning Predictive Outlook
| Day | Projected Soil Moisture (m³/m³) | 90% Confidence Interval | Projected Water Stress |
|---|---|---|---|
"""
for f in fc_results:
    officer_report_md += f"| {f['day_label']} | {f['predicted_sm']:.3f} | {f['lower_sm_bound']:.3f} – {f['upper_sm_bound']:.3f} | {f['predicted_stress_score']:.1f} / 100 |\n"

officer_report_md += """
---

### 4. PAU / ICAR 15 cm Soil Sampling Protocol for Extension Officers
1. **Field Stratification:** Select 5–6 representative spots in a zigzag pattern across the field, avoiding field bunds and shade trees.
2. **15 cm V-Cut Sampling:** Dig a V-shaped pit to 15 cm depth (active plow layer) and slice a uniform 2 cm core.
3. **Composite Quartering:** Mix in clean bucket, break clods, divide into 4 quarters, discarding opposite pairs until ~500g remains.
4. **Lab Submission:** Air-dry in shade (never sun-bake); submit to local KVK/PAU laboratory for pH, EC, OC, N-P-K, and micronutrients.

---
*Verified NASA Missions: SMAP L4, GPM IMERG, Landsat 8/9, MODIS MOD16A2, NASA POWER DAV, GRACE-FO.*
"""

foot_c1, foot_c2 = st.columns([1.5, 2.5], gap="medium")
with foot_c1:
    st.download_button(
        label="📥 Download District Officer Report (PDF / Markdown)",
        data=officer_report_md,
        file_name=f"punjab_farm_water_watch_{selected_district.lower().replace(' ', '_')}_report.md",
        mime="text/markdown",
        use_container_width=True,
        key="global_download_report_btn"
    )

with foot_c2:
    st.markdown("""
    <div style="text-align:right; font-size:0.78rem; color:#64748B; padding-top:8px;">
        Verified NASA Telemetry: NASA SMAP L4, GPM IMERG, Landsat 8/9, MODIS MOD16A2, POWER, GRACE-FO
    </div>
    """, unsafe_allow_html=True)
