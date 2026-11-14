"""
Punjab Farm Water Watch - Interactive NASA Earth Observation Dashboard
Developed by Team The SMAP Squad for NASA Space Apps Challenge 2026 (Delhi NCR)

Core Capabilities:
- Trilingual Support: English, Hindi (हिन्दी), Punjabi (ਪੰਜਾਬੀ)
- Interactive Leaflet/Folium Map with Dynamic District Colors & Pin-Drop Field Query
- 0-100 Water Stress Score Engine (SMAP 40%, GPM 30%, MODIS 20%, Landsat 10%)
- 7-Day RandomForestRegressor Predictive Forecast with 90% Confidence Interval
- SMAP-vs-Landsat NDVI/SAVI Dual Diagnosis for Hidden Soil-Quality & Salinity Degradation
- Step-by-Step 15 cm PAU/KVK Soil Testing Guide & In-App Remedies (Gypsum, Green Manuring, ZnSO4)
- Global Groundwater Hotspot Mode with Dynamic Regional Data (Central Valley, Nile Basin, High Plains)
- Strict NASA Data Provenance & Citations
"""

import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from datetime import datetime, timedelta

# Import models, spatial processor, and localized guides from src/ and model.py
from model import WaterStressModel, SevenDayMoistureForecaster, SoilQualityAnomalyDetector
from fetch_nasa_data import NASADataFetcher, REGIONAL_BOUNDING_BOXES
from src.pipeline.spatial_processor import SpatialProcessor
from src.advisories.i18n_content import I18N
from src.advisories.soil_testing_guide import SOIL_TESTING_STEPS, REMEDIES_GUIDE

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Punjab Farm Water Watch | NASA Space Apps 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Accessible, Publication-Ready UI
st.markdown("""
<style>
    .metric-box {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 5px solid #1f77b4;
        margin-bottom: 12px;
    }
    .metric-label { font-size: 0.85rem; font-weight: 600; color: #666; text-transform: uppercase; margin-bottom: 4px; }
    .metric-val { font-size: 2.0rem; font-weight: 700; color: #1a1a1a; margin-bottom: 2px; }
    .metric-sub { font-size: 0.82rem; color: #777; }
    .tag-green { background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .tag-yellow { background: #ffc107; color: #212529; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .tag-red { background: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .tag-soil-alert { background: #6f42c1; color: white; padding: 5px 12px; border-radius: 14px; font-weight: 700; font-size: 0.88rem; }
    .provenance-tag { font-size: 0.82rem; font-style: italic; color: #555; background: #eef2f7; padding: 6px 12px; border-radius: 6px; display: inline-block; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)


# --- INITIALIZE SERVICES & CACHE ---
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

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=110)
    st.markdown("### **NASA Space Apps Challenge 2026**")
    st.markdown("**Team:** The SMAP Squad · Delhi NCR")
    st.divider()

    # Language Toggle
    lang_code = st.selectbox(
        "🌐 Language / ਭਾਸ਼ਾ / भाषा",
        options=["en", "hi", "pa"],
        format_func=lambda x: {"en": "English", "hi": "हिन्दी (Hindi)", "pa": "ਪੰਜਾਬੀ (Punjabi)"}[x]
    )
    t = I18N[lang_code]

    # Global Hotspot Mode Switcher
    st.subheader(f"🌍 {t.get('select_region', 'Select Region / Hotspot')}")
    region_options = list(REGIONAL_BOUNDING_BOXES.keys())
    selected_region = st.selectbox("Region", region_options, index=0)
    is_global_hotspot = selected_region != "Punjab, India (Primary)"

    st.divider()
    if not is_global_hotspot:
        st.subheader(f"📍 {t.get('district_select', 'Select District')}")
        district_names = list(gdf_districts["name"])
        selected_district = st.selectbox("District", district_names, index=0)

        dist_row = gdf_districts[gdf_districts["name"] == selected_district].iloc[0]
        st.caption(f"Soil Type: **{dist_row['soil_type']}** | Rotation: **{dist_row['primary_crop']}**")

        st.markdown(f"#### 🎯 {t.get('pin_drop_title', 'Pin-Drop Coordinates')}")
        lat_in = st.number_input("Latitude (°N)", value=float(dist_row["lat"]), format="%.4f")
        lon_in = st.number_input("Longitude (°E)", value=float(dist_row["lon"]), format="%.4f")
    else:
        st.info(f"Viewing Global Hotspot: **{selected_region}**.\nNASA GRACE monitors secular groundwater loss across this basin.")
        selected_district = selected_region
        # Set representative centroid coordinates for global hotspot
        hotspot_coords = {
            "Central Valley, California (Hotspot)": (36.7783, -119.4179),
            "North Africa / Nile Basin (Hotspot)": (26.8206, 30.8025),
            "High Plains Aquifer, USA (Hotspot)": (38.0000, -100.5000)
        }
        lat_in, lon_in = hotspot_coords.get(selected_region, (36.0, -119.0))

    st.divider()
    st.markdown("#### 🛰️ 6 NASA Datasets Active")
    st.caption("• NASA SMAP L4 (Soil Moisture 0-100cm)\n• GPM IMERG (Daily Rain)\n• MODIS MOD16A2 (ET)\n• Landsat 8/9 (NDVI/SAVI/LST)\n• NASA POWER (Temp, Humidity, Wind)\n• GRACE/GRACE-FO (Groundwater Anomaly)")

# Filter data for active district or global hotspot
dist_df = df_all[df_all["district"] == selected_district].copy()
if dist_df.empty:
    dist_df = df_all[df_all["district"] == "Bathinda"].copy()

latest = dist_df.iloc[-1]
rain_30d_val = float(dist_df["gpm_precipitation_mm"].sum())

# Compute Water Stress Score (0-100)
stress_res = stress_model.compute_water_stress_score(
    smap_rootzone_sm=latest["smap_rootzone_sm"],
    rain_30d_mm=rain_30d_val,
    modis_et_mm=latest["modis_et_mm"],
    landsat_lst_c=latest["landsat_lst_c"]
)

# Run Soil-Quality Anomaly Detection (SMAP vs Landsat NDVI)
soil_res = soil_detector.evaluate_soil_anomaly(
    smap_rootzone_sm=latest["smap_rootzone_sm"],
    water_stress_score=stress_res["score"],
    landsat_ndvi=latest["landsat_ndvi"],
    landsat_savi=latest["landsat_savi"]
)

# --- PRECOMPUTE DYNAMIC DISTRICT SCORES FOR MAP CHOROPLETH ---
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
        district_scores[d] = {"score": 25.0, "zone": "Green", "badge_color": "#28a745", "status": "No Stress"}

# --- MAIN DASHBOARD HEADER ---
head_col1, head_col2 = st.columns([3.8, 1.2])
with head_col1:
    st.title(f"🌾 {t['title']}")
    st.markdown(f"**{t['subtitle']}**")
    st.caption(f"{t['team_credit']} · Domain: Earth Observation & Agronomic Resilience")

with head_col2:
    tag_class = f"tag-{stress_res['zone'].lower()}"
    st.markdown(f"<div style='text-align:right; margin-top:14px;'><span class='{tag_class}'>{stress_res['zone'].upper()} ZONE ({stress_res['score']}/100)</span></div>", unsafe_allow_html=True)
    if soil_res["alert_triggered"]:
        st.markdown(f"<div style='text-align:right; margin-top:8px;'><span class='tag-soil-alert'>⚠️ {t['anomaly_alert']}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:right; margin-top:8px;'><span class='tag-green'>✅ {t['anomaly_normal']}</span></div>", unsafe_allow_html=True)

st.divider()

# --- TOP TIER: 5 HIGH-CONTRAST KPI METRIC CARDS ---
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-box" style="border-top-color: {stress_res['badge_color']};">
        <div class="metric-label">{t['kpi_stress_score']}</div>
        <div class="metric-val">{stress_res['score']}<span style="font-size:1.1rem; color:#888;"> / 100</span></div>
        <div class="metric-sub"><span class="{tag_class}">{stress_res['status']}</span></div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{t['kpi_smap_moisture']}</div>
        <div class="metric-val">{latest['smap_rootzone_sm']:.3f} <span style="font-size:0.9rem;">m³/m³</span></div>
        <div class="metric-sub">Surface: {latest['smap_surface_sm']:.3f} m³/m³ (NASA SMAP L4)</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{t['kpi_30d_rain']}</div>
        <div class="metric-val">{rain_30d_val:.1f} <span style="font-size:0.9rem;">mm</span></div>
        <div class="metric-sub">30-day cumulative (GPM IMERG)</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{t['kpi_et_loss']}</div>
        <div class="metric-val">{latest['modis_et_mm']:.1f} <span style="font-size:0.9rem;">mm/day</span></div>
        <div class="metric-sub">Atmospheric crop draw (MODIS MOD16A2)</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    soil_badge = "<span class='tag-soil-alert'>ANOMALY DETECTED</span>" if soil_res["alert_triggered"] else "<span class='tag-green'>NORMAL</span>"
    st.markdown(f"""
    <div class="metric-box" style="border-top-color: {'#6f42c1' if soil_res['alert_triggered'] else '#28a745'};">
        <div class="metric-label">{t['kpi_soil_health']}</div>
        <div class="metric-val">NDVI {latest['landsat_ndvi']:.2f}</div>
        <div class="metric-sub">{soil_badge} (Landsat 8/9 OLI)</div>
    </div>
    """, unsafe_allow_html=True)

# --- CORE TIER: INTERACTIVE LEAFLET/FOLIUM MAP & PIN-DROP QUERY ---
st.markdown(f"### 🗺️ {t['pin_drop_title']}")
st.caption(t["pin_drop_instruct"])

map_left, map_right = st.columns([3, 2])

with map_left:
    if not is_global_hotspot:
        center_lat, center_lon, zoom_level = lat_in, lon_in, 8
    else:
        center_lat, center_lon, zoom_level = lat_in, lon_in, 6

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles="CartoDB positron")

    if not is_global_hotspot:
        # Dynamic style function: Colors each district polygon dynamically according to latest WaterStressModel score
        def dynamic_district_style(feat):
            dname = feat["properties"]["name"]
            score_data = district_scores.get(dname, {"badge_color": "#28a745"})
            return {
                "fillColor": score_data["badge_color"],
                "color": "#2c3e50",
                "weight": 2.2,
                "fillOpacity": 0.45
            }

        folium.GeoJson(
            gdf_districts,
            name="Punjab Agricultural Districts",
            style_function=dynamic_district_style,
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "soil_type", "primary_crop"],
                aliases=["District:", "Soil Type:", "Primary Crop:"]
            )
        ).add_to(m)

        # Place pin marker at active query point
        folium.Marker(
            [lat_in, lon_in],
            popup=f"<b>Field Query Point</b><br>District: {selected_district}<br>Stress Score: {stress_res['score']}/100 ({stress_res['zone']})",
            icon=folium.Icon(color="red" if stress_res["zone"]=="Red" else "orange" if stress_res["zone"]=="Yellow" else "green", icon="info-sign")
        ).add_to(m)
    else:
        folium.Marker(
            [lat_in, lon_in],
            popup=f"<b>Global Groundwater Hotspot</b><br>{selected_region}<br>NASA GRACE Secular Deficit: -1.8 to -4.2 cm/yr",
            icon=folium.Icon(color="red", icon="warning-sign")
        ).add_to(m)

    map_interaction = st_folium(m, height=430, width="100%", returned_objects=["last_clicked"])

    if map_interaction and map_interaction.get("last_clicked") and not is_global_hotspot:
        new_lat = map_interaction["last_clicked"]["lat"]
        new_lon = map_interaction["last_clicked"]["lng"]
        if abs(new_lat - lat_in) > 0.001 or abs(new_lon - lon_in) > 0.001:
            st.session_state["pin_coords"] = (new_lat, new_lon)

with map_right:
    st.markdown("#### ⚖️ Explainable Water Stress Drivers")
    st.markdown(f"**Mathematical Formulation (NASA 4-Layer Index):**")
    st.latex(r"\text{Score} = 0.40 \times \text{SMAP} + 0.30 \times \text{GPM} + 0.20 \times \text{ET} + 0.10 \times \text{LST}")

    st.write(f"• **SMAP Rootzone Moisture Deficit ({stress_res['contributions']['smap']}% impact):**")
    st.progress(int(stress_res['deficits']['smap_deficit']))

    st.write(f"• **GPM 30-Day Rainfall Deficit ({stress_res['contributions']['gpm']}% impact):**")
    st.progress(int(stress_res['deficits']['gpm_deficit']))

    st.write(f"• **MODIS Evapotranspiration Draw ({stress_res['contributions']['et']}% impact):**")
    st.progress(int(stress_res['deficits']['et_anomaly']))

    st.write(f"• **Landsat LST / Thermal Heat Anomaly ({stress_res['contributions']['lst']}% impact):**")
    st.progress(int(stress_res['deficits']['lst_anomaly']))

    st.divider()
    if soil_res["alert_triggered"]:
        st.error(f"🚨 **{soil_res['title']}**\n\n{soil_res['diagnosis']}")
    else:
        st.success(f"✅ **{soil_res['title']}**\n\n{soil_res['diagnosis']}")

st.divider()

# --- ANALYTICS TIER: 30-DAY TIMELINE & 7-DAY ML FORECAST ---
st.markdown(f"### 📊 {t['history_slider']} & Predictive Analytics")

# 30-Day Date Range Slider
date_min = pd.to_datetime(dist_df["date"].min()).date()
date_max = pd.to_datetime(dist_df["date"].max()).date()
slider_range = st.slider(
    "Select Analysis Window (Past 30 Days):",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
    format="YYYY-MM-DD"
)

mask_date = (pd.to_datetime(dist_df["date"]).dt.date >= slider_range[0]) & (pd.to_datetime(dist_df["date"]).dt.date <= slider_range[1])
filtered_df = dist_df[mask_date]

tab_charts, tab_ml, tab_soil_guide, tab_advisories_panel = st.tabs([
    f"📈 {t['history_slider']}",
    f"🔮 {t['forecast_header']}",
    "🧪 Soil-Testing Guide & In-App Remedies",
    f"📢 {t['advisory_header']}"
])

with tab_charts:
    fig_time = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=(
            f"NASA SMAP L4 Rootzone & Surface Soil Moisture (0–100 cm & 0–5 cm) - {selected_district}",
            f"NASA GPM IMERG Daily Rainfall & Landsat 8/9 NDVI - {selected_district}"
        )
    )

    # Subplot 1: Soil Moisture
    fig_time.add_trace(
        go.Scatter(x=filtered_df["date"], y=filtered_df["smap_rootzone_sm"], name="SMAP Rootzone SM (m³/m³)", line=dict(color="#1f77b4", width=2.8)),
        row=1, col=1
    )
    fig_time.add_trace(
        go.Scatter(x=filtered_df["date"], y=filtered_df["smap_surface_sm"], name="SMAP Surface SM (m³/m³)", line=dict(color="#aec7e8", width=1.5, dash="dash")),
        row=1, col=1
    )
    fig_time.add_hline(y=0.36, line_dash="dot", line_color="green", annotation_text="Field Capacity (0.36)", row=1, col=1)
    fig_time.add_hline(y=0.10, line_dash="dot", line_color="red", annotation_text="Wilting Point (0.10)", row=1, col=1)

    # Subplot 2: GPM Rainfall bars and Landsat NDVI line
    fig_time.add_trace(
        go.Bar(x=filtered_df["date"], y=filtered_df["gpm_precipitation_mm"], name="GPM IMERG Rain (mm/day)", marker_color="#2ca02c", opacity=0.7),
        row=2, col=1
    )
    fig_time.add_trace(
        go.Scatter(x=filtered_df["date"], y=filtered_df["landsat_ndvi"], name="Landsat NDVI", line=dict(color="#d62728" if soil_res["alert_triggered"] else "#2b5c8f", width=2.2), yaxis="y2"),
        row=2, col=1
    )

    fig_time.update_layout(
        height=520,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_time.update_yaxes(title_text="Soil Moisture (m³/m³)", row=1, col=1)
    fig_time.update_yaxes(title_text="Rainfall (mm/day)", row=2, col=1)
    st.plotly_chart(fig_time, use_container_width=True)

    # Explicit NASA Provenance
    st.markdown(f"<div class='provenance-tag'>🛡️ Source: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, NASA POWER, GRACE</div>", unsafe_allow_html=True)

with tab_ml:
    st.markdown("#### 7-Day RandomForest Soil Moisture Forecast")
    st.caption("Trained on past 7 days of SMAP soil moisture, GPM rainfall, and NASA POWER daily temperature with 90% confidence uncertainty intervals.")

    fc_results = forecaster.predict_next_7_days(dist_df)
    fc_df = pd.DataFrame(fc_results)

    col_fc1, col_fc2 = st.columns([3, 2])
    with col_fc1:
        fig_fc = go.Figure()
        # Uncertainty envelope
        fig_fc.add_trace(go.Scatter(
            x=fc_df["day_label"].tolist() + fc_df["day_label"].tolist()[::-1],
            y=fc_df["upper_sm_bound"].tolist() + fc_df["lower_sm_bound"].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.20)',
            line=dict(color='rgba(255,255,255,0)'),
            name='90% Confidence Interval'
        ))
        # Projected mean
        fig_fc.add_trace(go.Scatter(
            x=fc_df["day_label"],
            y=fc_df["predicted_sm"],
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            name='RandomForest Projected Moisture'
        ))
        fig_fc.add_hline(y=0.18, line_dash="dash", line_color="orange", annotation_text="Moderate Scarcity Threshold")
        fig_fc.update_layout(
            title=f"Projected Rootzone Moisture ({selected_district})",
            xaxis_title="Forecast Horizon",
            yaxis_title="Predicted Soil Moisture (m³/m³)",
            template="plotly_white",
            height=380
        )
        st.plotly_chart(fig_fc, use_container_width=True)
        st.markdown(f"<div class='provenance-tag'>🛡️ Source: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, NASA POWER, GRACE</div>", unsafe_allow_html=True)

    with col_fc2:
        st.markdown("##### 📅 Day-by-Day Forecast Breakdown")
        for f in fc_results:
            b_class = f"tag-{f['risk_zone'].lower()}"
            st.markdown(
                f"**{f['day_label']}:** Moisture `{f['predicted_sm']} m³/m³` "
                f"({f['lower_sm_bound']}–{f['upper_sm_bound']}) | "
                f"Stress: <span class='{b_class}'>{f['predicted_stress_score']}/100</span>",
                unsafe_allow_html=True
            )

with tab_soil_guide:
    st.markdown("### 🧪 Step-by-Step Soil-Testing Guide & Targeted Remedies")
    st.markdown(
        "When SMAP indicates adequate water (Green zone) yet Landsat NDVI/SAVI shows weak plant growth, "
        "crop yield is being suppressed by **salinity, alkalinity, soil compaction, or organic carbon loss**. "
        "Follow this ICAR & Punjab Agricultural University (PAU) field protocol:"
    )

    col_sg1, col_sg2 = st.columns(2)
    with col_sg1:
        st.markdown("#### 📋 How to Collect a Soil Sample (15 cm Depth)")
        for step in SOIL_TESTING_STEPS:
            title_text = step.get(f"title_{lang_code}", step["title_en"])
            desc_text = step.get(f"desc_{lang_code}", step["desc_en"])
            with st.expander(f"Step {step['step_number']}: {title_text}"):
                st.write(desc_text)

    with col_sg2:
        st.markdown("#### 🛠️ In-App Soil Remediation & Fixes")
        for item in REMEDIES_GUIDE:
            remedy_text = item.get(f"remedy_{lang_code}", item["remedy_en"])
            st.warning(f"**Issue:** {item['problem']}\n\n**Recommended Remedy:** {remedy_text}")

with tab_advisories_panel:
    st.markdown(f"### 📢 {t['advisory_header']} ({lang_code.upper()})")
    
    advisory_key = stress_res["action_code"]
    advisories = t["advisories"].get(advisory_key, t["advisories"]["CAUTION"])

    if stress_res["zone"] == "Red":
        st.error(f"🚨 **CRITICAL SCARCITY ALERT (Score: {stress_res['score']}/100)**")
    elif stress_res["zone"] == "Yellow":
        st.warning(f"⚠️ **MODERATE WATER STRESS ALERT (Score: {stress_res['score']}/100)**")
    else:
        st.success(f"✅ **NORMAL / SAFE WATER ZONE (Score: {stress_res['score']}/100)**")

    for adv in advisories:
        st.markdown(f"- 🌾 **{adv}**")

    st.divider()
    st.markdown("#### 🌾 Core Climate-Smart Practices for Punjab Wheat-Paddy Rotations")
    adv_c1, adv_c2 = st.columns(2)
    with adv_c1:
        st.info("🚜 **Tar-Watter Direct Seeded Rice (DSR):** Saves 15–20 cm of irrigation water, reduces pumping electricity costs, and protects soil structure from puddling hardpan compaction.")
    with adv_c2:
        st.success("🌱 **Crop Residue Mulching:** Spreading 2.5 tonnes/acre of paddy straw protects surface moisture from intense May–June evapotranspiration losses and eliminates stubble burning.")

# --- FOOTER & AUDIT PROVENANCE ---
st.divider()
st.markdown("#### 🛰️ Complete NASA Earth Observation Stack")
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("**1. NASA SMAP L4 (SPL4SMGP):** 9 km / 3-hourly 0–5 cm & 0–100 cm rootzone soil moisture.")
    st.markdown("**2. NASA GPM IMERG (GPM_3IMERGDF):** 0.1° daily precipitation tracking 30-day deficits.")
with f2:
    st.markdown("**3. MODIS MOD16A2:** 500 m / 8-day evapotranspiration (ET) measuring crop atmospheric water loss.")
    st.markdown("**4. Landsat 8/9 OLI/TIRS (HLSL30):** 30 m resolution NDVI, SAVI, NDWI, and Land Surface Temperature.")
with f3:
    st.markdown("**5. NASA POWER DAV:** Daily agroclimatology temperature, solar radiation, humidity, and wind.")
    st.markdown("**6. NASA GRACE / GRACE-FO:** Regional groundwater mass anomalies tracking Punjab's 0.5 m/yr secular depletion.")

st.caption("Punjab Farm Water Watch · NASA Space Apps Challenge 2026 · Delhi NCR · Team The SMAP Squad")
