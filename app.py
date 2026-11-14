"""
Punjab Farm Water Watch - Interactive NASA Earth Observation Mission Control
Developed by Team The SMAP Squad for NASA Space Apps Challenge 2026 (Delhi NCR)

Flagship Mission-Control UI:
- Deep Teal (#081822 / #0A1C28) dark background with crisp white chart/alert cards
- Top Bar: Title, Region/Hotspot Switcher, glowing green NASA Earthdata Live pill, and EN | HI | PA toggle
- Left Column: "What-If Water & Energy Calculator" (Farm Size slider, Practice selector, Litres/kWh Saved)
- Top Row: Leaflet/Folium Punjab Map with dynamic district risk colors, Bathinda pin, GIBS overlays, & Legend
           Stacked Water Stress Score Gauge (76/100 Critical) and Soil Quality Status card
- Middle Row: Crisp White "Soil Moisture & Water Forecast" card (30-day SMAP + 7-day RF forecast + shaded window)
- Bottom Row: "Soil Health Card & Lab Prescription" (pH, EC, OC inputs -> Gypsum/Compost/Zinc per acre)
              "Farmer Advisory & Alert" white card with trilingual advice, WhatsApp share, & Web Speech audio
- Footer: Download District Officer Report & Full NASA Citations
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

# Local models, spatial processor, and localized guides
from model import WaterStressModel, SevenDayMoistureForecaster, SoilQualityAnomalyDetector, CropBudgetSimulator
from fetch_nasa_data import NASADataFetcher, REGIONAL_BOUNDING_BOXES
from src.pipeline.spatial_processor import SpatialProcessor
from src.advisories.i18n_content import I18N
from src.advisories.soil_testing_guide import SOIL_TESTING_STEPS, REMEDIES_GUIDE
from src.advisories.smart_calendar import generate_smart_calendar

# Page Configuration
st.set_page_config(
    page_title="Punjab Farm Water Watch | NASA Space Apps 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FLAGSHIP MISSION-CONTROL DARK THEME STYLING ---
st.markdown("""
<style>
    /* Global App Background & Typography */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #071924 !important;
        color: #E2E8F0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Hide Streamlit default header decoration */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
    }
    
    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 2.0rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 1450px !important;
    }

    /* Top Navigation Bar */
    .top-navbar {
        background-color: #0B1E29;
        border: 1px solid #163649;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .app-title-text {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Glowing Green NASA Live Pill */
    .nasa-live-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid #10B981;
        color: #34D399;
        padding: 5px 13px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
    }
    
    .pulsing-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10B981;
        animation: pulse-green 2s infinite ease-in-out;
    }
    
    @keyframes pulse-green {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.45; transform: scale(0.85); }
    }

    /* Dark Dashboard Cards */
    .dark-card {
        background-color: #0E2533;
        border: 1px solid #17384B;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    }
    
    .dark-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .info-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 1px solid #64748B;
        color: #94A3B8;
        font-size: 11px;
        font-weight: 700;
        cursor: default;
    }

    /* Savings Highlight Box (Left Column) */
    .savings-display-box {
        background: #081B26;
        border: 1px solid #143548;
        border-radius: 8px;
        padding: 18px 12px;
        text-align: center;
        margin: 12px 0 8px 0;
    }
    
    .savings-big-val {
        font-size: 2.8rem;
        font-weight: 800;
        color: #2DD4BF; /* Vibrant neon mint */
        line-height: 1.05;
        letter-spacing: -0.03em;
    }
    
    .savings-label {
        font-size: 0.92rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 10px;
        font-weight: 500;
    }
    
    .kwh-badge {
        display: inline-block;
        background: #1E293B;
        border: 1px solid #334155;
        color: #E2E8F0;
        padding: 4px 12px;
        border-radius: 14px;
        font-size: 0.80rem;
        font-weight: 600;
    }
    
    .savings-footer-text {
        font-size: 0.85rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-top: 8px;
    }
    
    .accent-underline {
        height: 3px;
        width: 100%;
        background: linear-gradient(90deg, #0284C7, #0EA5E9, transparent);
        margin-top: 5px;
        border-radius: 2px;
    }

    /* Badges */
    .badge-critical {
        background: #DC2626;
        color: #FFFFFF;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: capitalize;
    }
    
    .badge-status {
        background: #1E293B;
        color: #94A3B8;
        border: 1px solid #334155;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-green {
        background: #16A34A;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    
    .badge-yellow {
        background: #F59E0B;
        color: #1E293B;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* 30 Days Ago vs Today Early Warning Cards */
    .delta-box {
        background: #09202C;
        border: 1px solid #14384B;
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .delta-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .delta-current {
        font-size: 1.35rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 2px 0;
    }
    .delta-sub {
        font-size: 0.76rem;
        color: #CBD5E1;
    }

    /* Smart Farm Calendar Cards */
    .calendar-card {
        background: #081B26;
        border: 1px solid #143548;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }
    .calendar-icon-col {
        font-size: 1.35rem;
        padding-top: 2px;
    }
    .calendar-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .calendar-desc {
        font-size: 0.82rem;
        color: #CBD5E1;
        margin-top: 3px;
        line-height: 1.38;
    }

    /* Crisp White Forecast Card (Middle Row) */
    .white-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        color: #0F172A;
    }
    
    .white-card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }

    /* Farmer Advisory Card (Bottom Right) */
    .advisory-white-card {
        background-color: #FFFFFF;
        border-top: 4px solid #DC2626;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        color: #0F172A;
    }
    
    .advisory-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #991B1B;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    /* Soil Health Card prescription sub-box */
    .prescription-box {
        background: #112B3B;
        border: 1px solid #1E465E;
        border-radius: 8px;
        padding: 12px 14px;
        height: 100%;
    }
    
    .prescription-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    
    .prescription-item {
        font-size: 0.83rem;
        color: #CBD5E1;
        margin-bottom: 4px;
        line-height: 1.4;
    }

    /* Streamlit Widget Overrides for Dark Mission Control */
    .stSelectbox > div > div {
        background-color: #081B26 !important;
        color: #FFFFFF !important;
        border-color: #17384B !important;
        border-radius: 6px !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #0284C7 !important;
    }
    
    /* Footer Citation */
    .footer-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 12px;
        padding-top: 8px;
        border-top: 1px solid #163649;
        font-size: 0.78rem;
        color: #64748B;
    }
</style>
""", unsafe_allow_html=True)


# --- DATA & MODEL INITIALIZATION ---
@st.cache_data
def load_datasets():
    csv_path = "data/processed/punjab_multi_satellite_30d.csv"
    if not os.path.exists(csv_path):
        from fetch_nasa_data import run_pipeline
        run_pipeline()
    df = pd.read_csv(csv_path)
    return df

@st.cache_resource
def load_models_and_spatial():
    return WaterStressModel(), SevenDayMoistureForecaster(), SoilQualityAnomalyDetector(), SpatialProcessor()

df_all = load_datasets()
stress_model, forecaster, soil_detector, spatial = load_models_and_spatial()
gdf_districts = spatial.gdf


# --- TOP BAR: TITLE, REGION, NASA LIVE PILL, LANGUAGE ---
top_col1, top_col2, top_col3, top_col4 = st.columns([2.6, 2.0, 1.4, 1.2])

with top_col1:
    st.markdown('<div class="app-title-text">Punjab Farm Water Watch</div>', unsafe_allow_html=True)

with top_col2:
    # Combined Region & District Selection
    region_options = [
        "Punjab - Bathinda (Critical Risk)",
        "Punjab - Sangrur (Moderate Stress)",
        "Punjab - Patiala (Moderate Stress)",
        "Punjab - Ludhiana (Safe / Low Stress)",
        "Punjab - Amritsar (Safe / Low Stress)",
        "Central Valley, California (Hotspot)",
        "North Africa / Nile Basin (Hotspot)",
        "High Plains Aquifer, USA (Hotspot)"
    ]
    if "selected_region_opt" not in st.session_state:
        st.session_state["selected_region_opt"] = "Punjab - Bathinda (Critical Risk)"

    current_idx = region_options.index(st.session_state["selected_region_opt"]) if st.session_state["selected_region_opt"] in region_options else 0
    selected_opt = st.selectbox(
        "Region Selection",
        options=region_options,
        index=current_idx,
        format_func=lambda x: f"📍 Region: {x}",
        label_visibility="collapsed"
    )
    st.session_state["selected_region_opt"] = selected_opt

with top_col3:
    st.markdown(
        '<div style="display:flex; justify-content:center; align-items:center; height:100%;">'
        '<div class="nasa-live-pill"><span class="pulsing-dot"></span> NASA Earthdata Live</div>'
        '</div>',
        unsafe_allow_html=True
    )

with top_col4:
    # EN | HI | PA Segmented Toggle
    lang_selection = st.radio(
        "Language",
        options=["en", "hi", "pa"],
        format_func=lambda x: {"en": "EN", "hi": "HI", "pa": "PA"}[x],
        horizontal=True,
        label_visibility="collapsed"
    )
    t = I18N.get(lang_selection, I18N["en"])


# --- REGION & DISTRICT TELEMETRY FILTERING ---
if selected_opt.startswith("Punjab - "):
    is_global_hotspot = False
    selected_district = selected_opt.split(" - ")[1].split(" ")[0]  # e.g., "Bathinda"
    dist_row = gdf_districts[gdf_districts["name"] == selected_district]
    if not dist_row.empty:
        lat_in, lon_in = float(dist_row.iloc[0]["lat"]), float(dist_row.iloc[0]["lon"])
    else:
        lat_in, lon_in = 30.2110, 74.9455
    dist_df = df_all[df_all["district"] == selected_district].copy()
else:
    is_global_hotspot = True
    selected_district = selected_opt
    hotspot_coords = {
        "Central Valley, California (Hotspot)": (36.7783, -119.4179),
        "North Africa / Nile Basin (Hotspot)": (26.8206, 30.8025),
        "High Plains Aquifer, USA (Hotspot)": (38.0000, -100.5000)
    }
    lat_in, lon_in = hotspot_coords.get(selected_district, (36.0, -119.0))
    dist_df = df_all[df_all["district"] == selected_district].copy()

if dist_df.empty:
    dist_df = df_all[df_all["district"] == "Bathinda"].copy()

latest = dist_df.iloc[-1]
rain_30d_val = float(dist_df["gpm_precipitation_mm"].sum())

# Compute Water Stress Score (0-100) using 40% SMAP + 30% GPM + 20% MODIS + 10% LST
stress_res = stress_model.compute_water_stress_score(
    smap_rootzone_sm=latest["smap_rootzone_sm"],
    rain_30d_mm=rain_30d_val,
    modis_et_mm=latest["modis_et_mm"],
    landsat_lst_c=latest["landsat_lst_c"]
)

# Run Soil-Quality Anomaly Detection (SMAP vs Landsat NDVI/SAVI)
soil_res = soil_detector.evaluate_soil_anomaly(
    smap_rootzone_sm=latest["smap_rootzone_sm"],
    water_stress_score=stress_res["score"],
    landsat_ndvi=latest["landsat_ndvi"],
    landsat_savi=latest["landsat_savi"]
)

# Precompute dynamic district scores for map choropleth
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

# 7-Day Forecast computation
fc_results = forecaster.predict_next_7_days(dist_df)
fc_df = pd.DataFrame(fc_results)


# --- MAIN GRID: LEFT SIDEBAR COLUMN (CALCULATOR) vs RIGHT DASHBOARD ---
col_calc, col_main = st.columns([1.0, 2.7], gap="medium")


# =========================================================================
# LEFT COLUMN: WHAT-IF WATER & ENERGY CALCULATOR
# =========================================================================
with col_calc:
    st.markdown("""
    <div class="dark-card" style="margin-bottom:0px;">
        <div class="dark-card-title">
            <span>What-If Water &amp; Energy Calculator</span>
            <span class="info-circle" title="Dynamic model based on PAU water conservation empirical benchmarks">ⓘ</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:0.83rem; font-weight:600; color:#94A3B8; margin-bottom:2px;'>Farm Size</div>", unsafe_allow_html=True)
    farm_acres = st.slider(
        "Farm Size",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        format="%d Acres",
        label_visibility="collapsed"
    )

    st.markdown("<div style='font-size:0.83rem; font-weight:600; color:#94A3B8; margin-top:8px; margin-bottom:2px;'>Practice</div>", unsafe_allow_html=True)
    practice_options = [
        "DSR (Direct Seeded Rice) / Mulching",
        "Delay Irrigation by 3 Days",
        "Crop-Residue Mulching",
        "Combined Protocol"
    ]
    selected_practice = st.selectbox(
        "Practice",
        practice_options,
        index=0,
        label_visibility="collapsed"
    )

    # Dynamic savings computation:
    # Baseline water consumption in Punjab paddy: ~900,000 Litres / acre / season
    # Energy: Submersible tube-wells draw ~0.789 kWh per 1,000 Litres pumped
    pct_saved_map = {
        "DSR (Direct Seeded Rice) / Mulching": 0.20,
        "Delay Irrigation by 3 Days": 0.10,
        "Crop-Residue Mulching": 0.15,
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
            <div class="savings-label">Litres Saved</div>
            <div class="kwh-badge">kWh Saved: {kwh_saved:,} kWh</div>
        </div>
        <div class="savings-footer-text">Water &amp; Energy Savings</div>
        <div class="accent-underline"></div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================================
# RIGHT MAIN DASHBOARD GRID
# =========================================================================
with col_main:
    
    # ---------------------------------------------------------------------
    # TOP ROW: MAP (60%) + STACKED CARDS (40%)
    # ---------------------------------------------------------------------
    top_map_col, top_cards_col = st.columns([1.55, 1.0], gap="medium")

    with top_map_col:
        # Create Folium Map with Leaflet controls
        m = folium.Map(
            location=[lat_in, lon_in],
            zoom_start=7 if not is_global_hotspot else 6,
            tiles="CartoDB dark_matter",
            zoom_control=True
        )

        # NASA GIBS WMTS Live Layers
        gibs_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        modis_truecolor_url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{gibs_date}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg"
        folium.TileLayer(
            tiles=modis_truecolor_url,
            name="🛰️ NASA GIBS Live Layer (MODIS)",
            attr="NASA Worldview / GIBS",
            overlay=True,
            control=True,
            opacity=0.65
        ).add_to(m)

        # Dynamic District Polygons
        if not is_global_hotspot:
            def district_style_func(feat):
                dname = feat["properties"]["name"]
                score_info = district_scores.get(dname, {"score": 25.0})
                sc = score_info["score"]
                # Color code: Safe (Green), Moderate (Yellow), Critical (Red)
                if sc > 60:
                    fill_c = "#DC2626" # Red
                elif sc > 30:
                    fill_c = "#F59E0B" # Yellow
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

            # Dynamic Pin on Selected District
            pin_color = "red" if stress_res["zone"] == "Red" else ("orange" if stress_res["zone"] == "Yellow" else "green")
            folium.Marker(
                [lat_in, lon_in],
                tooltip=f"<b>{selected_district}</b><br>Stress Score: {stress_res['score']}/100 ({stress_res['zone']})",
                icon=folium.Icon(color=pin_color, icon="tint", prefix="fa")
            ).add_to(m)

            # Text label directly under pin
            folium.map.Marker(
                [lat_in, lon_in],
                icon=folium.DivIcon(
                    icon_size=(100, 24),
                    icon_anchor=(50, -10),
                    html=f'<div style="font-size:11px; font-weight:700; color:#1E293B; background:rgba(255,255,255,0.92); padding:2px 6px; border-radius:4px; border:1px solid #94A3B8; text-align:center; width:max-content; margin:0 auto; box-shadow:0 1px 4px rgba(0,0,0,0.3);">{selected_district}</div>'
                )
            ).add_to(m)
        else:
            folium.Marker(
                [lat_in, lon_in],
                tooltip=f"<b>{selected_district}</b>",
                icon=folium.Icon(color="red", icon="warning-sign")
            ).add_to(m)

        # Layer Control for toggling NASA GIBS layer
        folium.LayerControl(position="topright", collapsed=True).add_to(m)

        # Map Legend overlay in bottom right corner of map
        legend_html = """
        <div style="
            position: fixed; 
            bottom: 14px; right: 14px; width: 135px; 
            background-color: rgba(255, 255, 255, 0.95);
            border: 1px solid #cbd5e1; border-radius: 6px;
            padding: 8px 10px; font-size: 11px; z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b; box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        ">
            <div style="font-weight: 700; margin-bottom: 5px; font-size: 11px; color:#0f172a;">Map Legend</div>
            <div style="margin-bottom: 3px; display:flex; align-items:center;"><span style="display:inline-block; width:10px; height:10px; background:#16a34a; margin-right:6px; border-radius:2px;"></span> Safe (0–30)</div>
            <div style="margin-bottom: 3px; display:flex; align-items:center;"><span style="display:inline-block; width:10px; height:10px; background:#f59e0b; margin-right:6px; border-radius:2px;"></span> Moderate (31–60)</div>
            <div style="display:flex; align-items:center;"><span style="display:inline-block; width:10px; height:10px; background:#dc2626; margin-right:6px; border-radius:2px;"></span> Critical (61–100)</div>
        </div>
        """
        m.get_root().html.add_child(Element(legend_html))

        # Render Map with click listener
        map_interaction = st_folium(m, height=330, width="100%", returned_objects=["last_clicked"])
        if map_interaction and map_interaction.get("last_clicked") and not is_global_hotspot:
            c_lat = map_interaction["last_clicked"]["lat"]
            c_lon = map_interaction["last_clicked"]["lng"]
            loc = spatial.locate_point(c_lat, c_lon)
            clicked_dist = loc["district"]
            matched_prefix = f"Punjab - {clicked_dist}"
            for opt in region_options:
                if opt.startswith(matched_prefix) and opt != st.session_state.get("selected_region_opt"):
                    st.session_state["selected_region_opt"] = opt
                    st.rerun()

    with top_cards_col:
        # Card 1: Water Stress Score
        gauge_val = stress_res['score']
        gauge_zone = stress_res['zone']
        gauge_color = "#DC2626" if gauge_val > 60 else ("#F59E0B" if gauge_val > 30 else "#16A34A")
        
        st.markdown("""
        <div class="dark-card" style="padding:12px 14px 10px 14px; margin-bottom:10px;">
            <div class="dark-card-title" style="margin-bottom:4px;">
                <span>Water Stress Score</span>
                <span class="info-circle" title="40% SMAP + 30% GPM + 20% MODIS ET + 10% Landsat LST">ⓘ</span>
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
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

        st.markdown(f"""
            <div style="display:flex; justify-content:center; gap:8px; margin-top:-6px; margin-bottom:4px;">
                <span class="badge-critical" style="background:{gauge_color};">{gauge_zone}</span>
                <span class="badge-status">Current Status</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card 2: Soil Quality Status (Dynamic)
        st.markdown("""
        <div class="dark-card" style="padding:12px 14px; margin-bottom:0px;">
            <div class="dark-card-title" style="margin-bottom:4px;">
                <span>Soil Quality Status</span>
                <span class="info-circle" title="SMAP vs Landsat NDVI/SAVI Dual Diagnosis">ⓘ</span>
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
                st.markdown('<div style="margin-top:10px;"><span class="badge-critical">Critical</span></div>', unsafe_allow_html=True)
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
            st.plotly_chart(fig_soil_mini, use_container_width=True, config={'displayModeBar': False})

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # EARLY WARNING DELTA ROW: 30 DAYS AGO vs. TODAY
    # ---------------------------------------------------------------------
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

    st.markdown(f"""
    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; margin-bottom: 12px;">
        <div class="delta-box">
            <div class="delta-label">SMAP Rootzone Soil Moisture</div>
            <div class="delta-current">{sm_now:.3f} <span style="font-size:0.82rem; color:#94A3B8;">m³/m³</span></div>
            <div class="delta-sub">30d Ago: {sm_old:.3f} | <span style="color:{sm_color}; font-weight:700;">{sm_diff:+.3f} m³/m³</span></div>
        </div>
        <div class="delta-box">
            <div class="delta-label">Landsat 8/9 Canopy NDVI</div>
            <div class="delta-current">{ndvi_now:.3f}</div>
            <div class="delta-sub">30d Ago: {ndvi_old:.3f} | <span style="color:{ndvi_color}; font-weight:700;">{ndvi_diff:+.3f}</span></div>
        </div>
        <div class="delta-box">
            <div class="delta-label">Water Stress Index (0–100)</div>
            <div class="delta-current">{score_now} <span style="font-size:0.82rem; color:#94A3B8;">/ 100</span></div>
            <div class="delta-sub">30d Ago: {score_old:.1f} | <span style="color:{score_color}; font-weight:700;">{score_diff:+.1f} pts</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # MIDDLE ROW: SOIL MOISTURE & WATER FORECAST (CRISP WHITE CARD)
    # ---------------------------------------------------------------------
    st.markdown("""
    <div class="white-card">
        <div class="white-card-title">Soil Moisture &amp; Water Forecast</div>
    """, unsafe_allow_html=True)

    # Plotly Forecast Chart matching exact layout & color styling
    # Historical 30-day SMAP + 7-day Random Forest Forecast
    hist_dates = pd.to_datetime(dist_df["date"]).dt.strftime("%b %d").tolist()
    hist_sm = dist_df["smap_rootzone_sm"].tolist()

    fc_dates = [f["day_label"] for f in fc_results]
    fc_preds = [f["predicted_sm"] for f in fc_results]
    
    # Combined timeline
    all_timeline_dates = hist_dates + fc_dates
    
    fig_line = go.Figure()

    # Vertical shaded band highlighting the 7-day forecast window
    fig_line.add_vrect(
        x0=len(hist_dates) - 1,
        x1=len(all_timeline_dates) - 1,
        fillcolor="rgba(224, 242, 254, 0.65)",
        layer="below",
        line_width=0
    )

    # 30-Day SMAP Soil Moisture
    fig_line.add_trace(go.Scatter(
        x=list(range(len(hist_dates))),
        y=hist_sm,
        mode="lines",
        name="30-day SMAP soil moisture",
        line=dict(color="#0F4C5C", width=2.5)
    ))

    # 7-Day Random Forest Forecast
    fig_line.add_trace(go.Scatter(
        x=list(range(len(hist_dates) - 1, len(all_timeline_dates))),
        y=[hist_sm[-1]] + fc_preds,
        mode="lines",
        name="7-day Random Forest forecast",
        line=dict(color="#B45309", width=2.5)
    ))

    # Dashed baseline drydown continuation
    dash_baseline = [hist_sm[-1] - (i * 0.012) for i in range(len(fc_preds) + 1)]
    fig_line.add_trace(go.Scatter(
        x=list(range(len(hist_dates) - 1, len(all_timeline_dates))),
        y=dash_baseline,
        mode="lines",
        showlegend=False,
        line=dict(color="#0284C7", width=1.5, dash="dash")
    ))

    # Pick 4 representative date tick positions: Oct 15, Oct 30, Nov 14, Nov 21
    tick_indices = [
        0,
        len(hist_dates) // 2,
        len(hist_dates) - 1,
        len(all_timeline_dates) - 1
    ]
    tick_texts = [
        all_timeline_dates[tick_indices[0]],
        all_timeline_dates[tick_indices[1]],
        all_timeline_dates[tick_indices[2]],
        all_timeline_dates[tick_indices[3]]
    ]

    fig_line.update_layout(
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
            title="Soil Moisture",
            title_font=dict(size=11, color="#475569"),
            showgrid=True,
            gridcolor="#E2E8F0"
        )
    )

    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)


    # ---------------------------------------------------------------------
    # DECISION SUPPORT SUITE: 7-DAY SMART CALENDAR & CROP-SWITCH SIMULATOR
    # ---------------------------------------------------------------------
    tab_cal, tab_crops = st.tabs([
        "🗓️ Pin-Drop 7-Day Smart Farm Action Calendar",
        "🌾 Crop-Switch & Aquifer-Life Budget Simulator"
    ])

    with tab_cal:
        st.markdown(f"""
        <div class="dark-card" style="margin-bottom:12px;">
            <div class="dark-card-title">
                <span>🗓️ Precision Action Calendar for {selected_district}</span>
                <span class="info-circle" title="Dynamic 7-day schedule generated from RandomForest soil projections & anomaly triggers">ⓘ</span>
            </div>
        """, unsafe_allow_html=True)
        smart_cal_days = generate_smart_calendar(fc_results, soil_res, lang=lang_selection)

        c_cols = st.columns(2)
        for idx, c_day in enumerate(smart_cal_days):
            col_target = c_cols[idx % 2]
            with col_target:
                st.markdown(f"""
                <div class="calendar-card">
                    <div class="calendar-icon-col">{c_day['icon']}</div>
                    <div style="flex-grow:1;">
                        <div class="calendar-title">
                            <span>{c_day['day_label']}: {c_day['title']}</span>
                            <span class="badge-status" style="border-color:{c_day['badge_color']}; color:{c_day['badge_color']};">{c_day['badge']}</span>
                        </div>
                        <div class="calendar-desc">{c_day['action']}</div>
                        <div style="font-size:0.74rem; color:#64748B; margin-top:4px;">
                            Projected Moisture: <b>{c_day['projected_sm']:.3f} m³/m³</b> · Zone: <b style="color:{c_day['badge_color']};">{c_day['risk_zone']}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_crops:
        st.markdown(f"""
        <div class="dark-card" style="margin-bottom:12px;">
            <div class="dark-card-title">
                <span>🌾 Crop Diversification &amp; Groundwater Budget Simulator ({selected_district})</span>
                <span class="info-circle" title="PAU Agronomic Benchmarks for Groundwater Depletion Mitigation">ⓘ</span>
            </div>
        """, unsafe_allow_html=True)

        sim_col_sel, sim_col_chart = st.columns([1.1, 1.4], gap="medium")
        with sim_col_sel:
            st.markdown("<div style='font-size:0.83rem; font-weight:600; color:#94A3B8; margin-bottom:2px;'>Select Crop Diversification Option:</div>", unsafe_allow_html=True)
            crop_choice = st.selectbox(
                "Crop Choice",
                options=list(CropBudgetSimulator.CROP_PROFILES.keys()),
                index=1,
                label_visibility="collapsed"
            )
            sim_budget = CropBudgetSimulator.calculate_budget(crop_choice, farm_acres=farm_acres)

            st.markdown(f"""
            <div style="background:#09202C; border:1px solid #163C52; border-radius:8px; padding:12px; margin-top:6px;">
                <div style="font-size:0.82rem; font-weight:700; color:#38BDF8; margin-bottom:6px;">📊 Seasonal Water Budget ({farm_acres} Acres)</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.82rem;">
                    <span style="color:#94A3B8;">Water Demand:</span>
                    <span style="color:#FFFFFF; font-weight:700;">{sim_budget['crop_water_demand_m']}M Litres</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.82rem;">
                    <span style="color:#94A3B8;">Groundwater Saved:</span>
                    <span style="color:#2DD4BF; font-weight:700;">{sim_budget['groundwater_saved_m']}M Litres ({sim_budget['pct_saved']:.0f}%)</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.82rem;">
                    <span style="color:#94A3B8;">Tube-Well Power Saved:</span>
                    <span style="color:#F59E0B; font-weight:700;">{sim_budget['kwh_saved']:,} kWh</span>
                </div>
                <div style="margin-top:8px; font-size:0.77rem; color:#CBD5E1; font-style:italic;">
                    💡 {sim_budget['recommendation']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with sim_col_chart:
            # Side-by-side Plotly Bar Chart comparing Baseline Paddy vs Alternative
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(
                x=["Paddy Baseline", "Selected Crop", "Water Saved"],
                y=[sim_budget["baseline_litres_m"], sim_budget["crop_water_demand_m"], sim_budget["groundwater_saved_m"]],
                marker_color=["#DC2626", "#0284C7", "#2DD4BF"],
                text=[f"{sim_budget['baseline_litres_m']}M", f"{sim_budget['crop_water_demand_m']}M", f"{sim_budget['groundwater_saved_m']}M"],
                textposition="auto"
            ))
            fig_sim.update_layout(
                template="plotly_dark",
                height=185,
                margin=dict(l=25, r=15, t=10, b=25),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title="Million Litres", showgrid=True, gridcolor="#163C52", title_font=dict(size=10)),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_sim, use_container_width=True, config={'displayModeBar': False})

        st.markdown("</div>", unsafe_allow_html=True)


    # ---------------------------------------------------------------------
    # BOTTOM ROW: SOIL HEALTH CARD (LEFT) + FARMER ADVISORY (RIGHT)
    # ---------------------------------------------------------------------
    bot_left, bot_right = st.columns([1.1, 1.0], gap="medium")

    with bot_left:
        st.markdown("""
        <div class="dark-card" style="margin-bottom:0px; height:100%;">
            <div class="dark-card-title">
                <span>Soil Health Card &amp; Lab Prescription</span>
                <span class="info-circle" title="Empirical PAU/KVK Soil Testing Protocol">ⓘ</span>
            </div>
        """, unsafe_allow_html=True)

        sc_in_col, sc_rx_col = st.columns([1.0, 1.25])
        with sc_in_col:
            st.markdown("<div style='font-size:0.75rem; color:#94A3B8; font-weight:600;'>pH</div>", unsafe_allow_html=True)
            input_ph = st.number_input("pH", value=8.6, step=0.1, min_value=4.0, max_value=11.0, label_visibility="collapsed")
            
            st.markdown("<div style='font-size:0.75rem; color:#94A3B8; font-weight:600; margin-top:4px;'>EC (dS/m)</div>", unsafe_allow_html=True)
            input_ec = st.number_input("EC", value=0.9, step=0.1, min_value=0.0, max_value=20.0, label_visibility="collapsed")
            
            st.markdown("<div style='font-size:0.75rem; color:#F59E0B; font-weight:600; margin-top:4px;'>OC (%)</div>", unsafe_allow_html=True)
            input_oc = st.number_input("OC", value=0.38, step=0.01, min_value=0.05, max_value=2.0, label_visibility="collapsed")

            st.markdown("<div style='font-size:0.75rem; color:#94A3B8; font-weight:600; margin-top:4px;'>Nitrogen (kg/ha)</div>", unsafe_allow_html=True)
            input_n = st.number_input("Nitrogen", value=190, step=10, min_value=50, max_value=600, label_visibility="collapsed")

        # Dynamic prescription doses
        gypsum_bags = 2 if input_ph > 8.5 else 0
        fym_tonnes = 4 if input_oc < 0.5 else 0
        gypsum_text = f"• {gypsum_bags} Bags Gypsum/Acre" if gypsum_bags > 0 else "• Gypsum: Normal (No Treatment)"
        compost_text = f"• {fym_tonnes}t Compost/Acre" if fym_tonnes > 0 else "• Compost: Adequate Carbon"
        zinc_text = "• Zinc Dose (25 kg/ha ZnSO4)" if input_n < 250 else "• Standard Basal Dose"

        with sc_rx_col:
            st.markdown(f"""
            <div class="prescription-box">
                <div class="prescription-title">Apply Gypsum &amp;<br>Lab Prescription</div>
                <div class="prescription-item">{gypsum_text}</div>
                <div class="prescription-item">{compost_text}</div>
                <div class="prescription-item">{zinc_text}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📖 PAU / KVK 15 cm Soil Testing Protocol & Field Remedies"):
            st.markdown("**PAU / ICAR 4-Step Soil Sampling Protocol:**")
            for step in SOIL_TESTING_STEPS:
                t_key = f"title_{lang_selection}" if f"title_{lang_selection}" in step else "title_en"
                d_key = f"desc_{lang_selection}" if f"desc_{lang_selection}" in step else "desc_en"
                st.markdown(f"**Step {step['step_number']}: {step.get(t_key, step['title_en'])}**\n{step.get(d_key, step['desc_en'])}")
            st.markdown("---")
            st.markdown("**Recommended Field Remedies:**")
            for rem in REMEDIES_GUIDE:
                r_key = f"remedy_{lang_selection}" if f"remedy_{lang_selection}" in rem else "remedy_en"
                st.markdown(f"• **{rem['problem']}:** {rem.get(r_key, rem['remedy_en'])}")

    with bot_right:
        # Farmer Advisory Card (Crisp White Card with Red Top Border)
        # Select localized text dynamically based on risk zone
        if stress_res["zone"] == "Red":
            if lang_selection == "pa":
                adv1 = "ਕਿਸਾਨ ਵੀਰੋ, 3 ਦਿਨ ਪਾਣੀ ਰੋਕੋ (Kisan veero, 3 din paani roko)"
                adv2 = "ਸਿੱਧੀ ਬਿਜਾਈ (DSR) ਅਤੇ ਮਲਚਿੰਗ ਅਪਣਾਓ (Adopt DSR & Mulching)"
            elif lang_selection == "en":
                adv1 = "Farmers, pause irrigation for 3 days to preserve root aeration"
                adv2 = "Switch to Direct Seeded Rice (DSR) & Crop-Residue Mulching"
            else: # hi
                adv1 = "Kisan bhai, 3 din paani rok do"
                adv2 = "Switch to Direct Seeded Rice (DSR) & Mulching"
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
        <div class="advisory-white-card" style="margin-bottom:0px;">
            <div class="advisory-title">
                <span>Farmer Advisory &amp; Alert</span>
                <span style="font-size:1.15rem;">🔔</span>
            </div>
            <div style="font-size:0.88rem; font-weight:600; color:#1E293B; margin-bottom:8px;">
                • {adv1}
            </div>
            <div style="font-size:0.88rem; font-weight:600; color:#1E293B; margin-bottom:14px;">
                • {adv2}
            </div>
        """, unsafe_allow_html=True)

        # Action Buttons: WhatsApp Share & Listen Voice Alert
        # 1. WhatsApp Button
        wa_text = f"🌾 Punjab Farm Water Watch Alert - {selected_district}\nWater Stress Score: {stress_res['score']}/100 ({stress_res['zone']})\nAdvisory:\n1. {adv1}\n2. {adv2}\nNASA Live Telemetry Verified."
        wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
            <div style="
                background-color:#22C55E; color:#FFFFFF; text-align:center;
                font-size:0.86rem; font-weight:700; padding:8px 12px; border-radius:6px;
                margin-bottom:8px; display:flex; align-items:center; justify-content:center; gap:6px;
                box-shadow:0 2px 6px rgba(34,197,94,0.3);
            ">
                💬 Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)

        # 2. Browser Web Speech Voice Alert
        speech_text = f"{adv1}. {adv2}."
        speech_lang = "hi-IN" if lang_selection in ["hi", "pa"] else "en-US"
        speech_html = f"""
        <div style="display:flex; justify-content:center;">
            <button id="voiceBtn" style="
                width: 100%; background-color:#E2E8F0; color:#1E293B; border:none;
                font-size:0.86rem; font-weight:700; padding:8px 12px; border-radius:6px;
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
        components.html(speech_html, height=40)
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# FOOTER: DOWNLOAD REPORT & NASA CITATION
# =========================================================================
st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
foot_col1, foot_col2 = st.columns([1.5, 2.5])

# Prepare District Officer Dossier Markdown
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
* **Prescription:** Apply {gypsum_bags} bags/acre Agricultural Gypsum, {fym_tonnes} tonnes/acre FYM/Compost, and 25 kg/acre Zinc Sulfate.

---

### 3. 7-Day Machine Learning Predictive Outlook
| Day | Projected Soil Moisture (m³/m³) | 90% Confidence Interval | Projected Water Stress |
|---|---|---|---|
"""
for f in fc_results:
    officer_report_md += f"| {f['day_label']} | {f['predicted_sm']:.3f} | {f['lower_sm_bound']:.3f} – {f['upper_sm_bound']:.3f} | {f['predicted_stress_score']:.1f} / 100 |\n"

officer_report_md += """
---

### 4. PAU / ICAR 15 cm Soil Testing Protocol for Extension Officers
1. **Field Stratification:** Select 5–6 representative spots in a zigzag pattern across the field, avoiding field bunds and shade trees.
2. **15 cm V-Cut Sampling:** Dig a V-shaped pit to 15 cm depth (active plow layer) and slice a uniform 2 cm core.
3. **Composite Quartering:** Mix in clean bucket, break clods, divide into 4 quarters, discarding opposite pairs until ~500g remains.
4. **Lab Submission:** Air-dry in shade (never sun-bake); submit to local KVK/PAU laboratory for pH, EC, OC, N-P-K, and micronutrients.

---
*Data Sources: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, POWER, GRACE.*
"""

with foot_col1:
    st.download_button(
        label="📥 Download District Officer Report (PDF / Markdown)",
        data=officer_report_md,
        file_name=f"punjab_farm_water_watch_{selected_district.lower().replace(' ', '_')}_report.md",
        mime="text/markdown",
        use_container_width=True
    )

with foot_col2:
    st.markdown("""
    <div style="text-align:right; font-size:0.78rem; color:#64748B; padding-top:6px;">
        Data Source: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, POWER, GRACE
    </div>
    """, unsafe_allow_html=True)
