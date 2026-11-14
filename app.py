"""
Punjab Farm Water Watch - Interactive NASA Earth Observation Dashboard
Developed by Team The SMAP Squad for NASA Space Apps Challenge 2026 (Delhi NCR)

5 High-Impact Upgrades for Judging:
1. Live NASA GIBS Satellite Tile Overlay on Folium Map with LayerControl (MODIS Terra TrueColor & LST)
2. Interactive "What-If" Water & Tube-Well Energy Savings Calculator (litres, kWh, district scale)
3. Interactive Soil Health Card & Instant Lab Prescription (pH, EC, OC, N inputs with PAU/KVK advice)
4. One-Click WhatsApp Alert & Web Speech Voice Advisory (English, हिन्दी, ਪੰਜਾਬੀ)
5. One-Click Downloadable District Officer Action Brief (Markdown & CSV) with full NASA citations
"""

import os
import urllib.parse
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd

# Local models, spatial processor, and localized guides
from model import WaterStressModel, SevenDayMoistureForecaster, SoilQualityAnomalyDetector
from fetch_nasa_data import NASADataFetcher, REGIONAL_BOUNDING_BOXES
from src.pipeline.spatial_processor import SpatialProcessor
from src.advisories.i18n_content import I18N
from src.advisories.soil_testing_guide import SOIL_TESTING_STEPS, REMEDIES_GUIDE

# Page Configuration
st.set_page_config(
    page_title="Punjab Farm Water Watch | NASA Space Apps 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Styling
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
    .calculator-box { background: #fdfefe; border: 1px solid #dcdfe6; border-radius: 10px; padding: 18px; margin-top: 8px; }
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
        district_scores[d] = {"score": 25.0, "zone": "Green", "badge_color": "#28a745", "status": "No Stress"}

# 7-Day Forecast computation
fc_results = forecaster.predict_next_7_days(dist_df)
fc_df = pd.DataFrame(fc_results)

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
        <div class="metric-label">{t['kpi_rain']}</div>
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

# --- CORE TIER: INTERACTIVE MAP WITH NASA GIBS SATELLITE TILE OVERLAYS ---
st.markdown(f"### 🗺️ {t['pin_drop_title']} & Live NASA GIBS Satellite Layers")
st.caption("Interact with live NASA GIBS WMTS satellite imagery (MODIS TrueColor & Thermal) toggled directly over Punjab district boundaries.")

map_left, map_right = st.columns([3.2, 1.8])

with map_left:
    if not is_global_hotspot:
        center_lat, center_lon, zoom_level = lat_in, lon_in, 8
    else:
        center_lat, center_lon, zoom_level = lat_in, lon_in, 6

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles="CartoDB positron")

    # --- FEATURE 1: LIVE NASA GIBS SATELLITE TILE OVERLAYS ---
    gibs_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # 1. NASA GIBS MODIS Terra True Color TileLayer
    modis_truecolor_url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{gibs_date}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg"
    folium.TileLayer(
        tiles=modis_truecolor_url,
        name=f"🛰️ NASA GIBS MODIS True Color ({gibs_date})",
        attr="NASA Worldview / GIBS",
        overlay=True,
        control=True,
        opacity=0.70
    ).add_to(m)

    # 2. NASA GIBS Land Surface Temperature (Thermal)
    lst_thermal_url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Land_Surface_Temp_Day/default/{gibs_date}/GoogleMapsCompatible_Level7/{{z}}/{{y}}/{{x}}.png"
    folium.TileLayer(
        tiles=lst_thermal_url,
        name=f"🌡️ NASA GIBS Land Surface Temp Day",
        attr="NASA Worldview / GIBS",
        overlay=True,
        control=True,
        opacity=0.55
    ).add_to(m)

    if not is_global_hotspot:
        def dynamic_district_style(feat):
            dname = feat["properties"]["name"]
            score_data = district_scores.get(dname, {"badge_color": "#28a745"})
            return {
                "fillColor": score_data["badge_color"],
                "color": "#2c3e50",
                "weight": 2.2,
                "fillOpacity": 0.40
            }

        folium.GeoJson(
            gdf_districts,
            name="Punjab District Risk Boundaries",
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

    # LayerControl to toggle NASA GIBS vs District choropleth
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    map_interaction = st_folium(m, height=450, width="100%", returned_objects=["last_clicked"])

    if map_interaction and map_interaction.get("last_clicked") and not is_global_hotspot:
        new_lat = map_interaction["last_clicked"]["lat"]
        new_lon = map_interaction["last_clicked"]["lng"]
        if abs(new_lat - lat_in) > 0.001 or abs(new_lon - lon_in) > 0.001:
            st.session_state["pin_coords"] = (new_lat, new_lon)

with map_right:
    st.markdown("#### ⚖️ Explainable Water Stress Drivers")
    st.markdown(f"**Mathematical Formulation (NASA 4-Layer Index):**")
    st.latex(r"\text{Score} = 0.40 \times \text{SMAP} + 0.30 \times \text{GPM} + 0.20 \times \text{ET} + 0.10 \times \text{LST}")

    st.write(f"• **SMAP Rootzone Deficit ({stress_res['contributions']['smap']}%):**")
    st.progress(int(stress_res['deficits']['smap_deficit']))

    st.write(f"• **GPM 30-Day Rain Deficit ({stress_res['contributions']['gpm']}%):**")
    st.progress(int(stress_res['deficits']['gpm_deficit']))

    st.write(f"• **MODIS Evapotranspiration ({stress_res['contributions']['et']}%):**")
    st.progress(int(stress_res['deficits']['et_anomaly']))

    st.write(f"• **Landsat LST Heat Anomaly ({stress_res['contributions']['lst']}%):**")
    st.progress(int(stress_res['deficits']['lst_anomaly']))

    st.divider()
    if soil_res["alert_triggered"]:
        st.error(f"🚨 **{soil_res['title']}**\n\n{soil_res['diagnosis']}")
    else:
        st.success(f"✅ **{soil_res['title']}**\n\n{soil_res['diagnosis']}")

st.divider()

# --- ANALYTICS & INTERACTIVE MODULE TABS ---
tab_timeline, tab_forecast, tab_calculator, tab_soil_card, tab_advisories = st.tabs([
    f"📈 {t['history_slider']}",
    f"🔮 {t['forecast_header']}",
    "⚡ 'What-If' Water & Energy Calculator",
    "🧪 Soil Health Card & Instant Prescription",
    f"📢 {t['advisory_header']} & Audio"
])

# --- TAB 1: 30-DAY MULTI-SATELLITE TIMELINE ---
with tab_timeline:
    date_min = pd.to_datetime(dist_df["date"].min()).date()
    date_max = pd.to_datetime(dist_df["date"].max()).date()
    slider_range = st.slider(
        "Select Telemetry Date Window:",
        min_value=date_min,
        max_value=date_max,
        value=(date_min, date_max),
        format="YYYY-MM-DD"
    )

    mask_date = (pd.to_datetime(dist_df["date"]).dt.date >= slider_range[0]) & (pd.to_datetime(dist_df["date"]).dt.date <= slider_range[1])
    filtered_df = dist_df[mask_date]

    fig_time = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=(
            f"NASA SMAP L4 Rootzone & Surface Soil Moisture (0–100 cm & 0–5 cm) - {selected_district}",
            f"NASA GPM IMERG Daily Rainfall & Landsat 8/9 NDVI - {selected_district}"
        )
    )

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
    st.markdown(f"<div class='provenance-tag'>🛡️ Source: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, NASA POWER, GRACE</div>", unsafe_allow_html=True)

# --- TAB 2: 7-DAY ML FORECAST ---
with tab_forecast:
    st.markdown("#### 7-Day RandomForest Soil Moisture Forecast")
    st.caption("Trained on past 7 days of SMAP soil moisture, GPM rainfall, and NASA POWER daily temperature with 90% confidence uncertainty intervals.")

    col_fc1, col_fc2 = st.columns([3, 2])
    with col_fc1:
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=fc_df["day_label"].tolist() + fc_df["day_label"].tolist()[::-1],
            y=fc_df["upper_sm_bound"].tolist() + fc_df["lower_sm_bound"].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.20)',
            line=dict(color='rgba(255,255,255,0)'),
            name='90% Confidence Interval'
        ))
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

# --- FEATURE 2: "WHAT-IF" WATER & TUBE-WELL ENERGY SAVINGS CALCULATOR ---
with tab_calculator:
    st.markdown("### ⚡ 'What-If' Water & Tube-Well Energy Savings Simulator")
    st.caption("Quantifies seasonal groundwater preservation, electricity cost reduction, and district-scale scalability across Punjab's 1.4 million tube wells.")

    calc_c1, calc_c2 = st.columns([1.5, 2.5])
    with calc_c1:
        st.markdown("#### 🚜 Farm Simulation Parameters")
        farm_acres = st.slider("Farm Size (Acres):", min_value=1, max_value=100, value=10, step=1)
        
        practice_options = {
            "Direct Seeded Rice (DSR) (~20% water saved)": {"water_pct": 0.20, "power_pct": 0.20},
            "Delay Irrigation by 3 Days (~10% water saved)": {"water_pct": 0.10, "power_pct": 0.10},
            "Crop-Residue Mulching (~15% water saved)": {"water_pct": 0.15, "power_pct": 0.15},
            "Combined Protocol (DSR + Mulching + Satellite Alerts) (~30% water saved)": {"water_pct": 0.30, "power_pct": 0.30}
        }
        selected_practice = st.selectbox("Select Conservation Practice:", list(practice_options.keys()), index=0)
        chosen_pct = practice_options[selected_practice]["water_pct"]

    # Agronomic baselines for Punjab Paddy
    baseline_water_per_acre_litres = 2200000  # 22 Lakh Litres per acre per season
    baseline_kwh_per_acre = 420              # kWh grid electricity per acre for pumping

    # Farm-level savings
    water_saved_litres = farm_acres * baseline_water_per_acre_litres * chosen_pct
    kwh_saved = farm_acres * baseline_kwh_per_acre * chosen_pct
    diesel_eq_litres = kwh_saved * 0.28      # diesel equivalent if using backup pump
    co2_saved_kg = kwh_saved * 0.82          # 0.82 kg CO2 per kWh grid electricity

    # District-level extrapolation (10% adoption across ~10,000 tube wells / ~50,000 acres in district)
    district_acres_target = 50000
    district_water_saved_gl = (district_acres_target * baseline_water_per_acre_litres * chosen_pct) / 1e9  # Gigalitres (Billion Litres)
    district_kwh_gwh = (district_acres_target * baseline_kwh_per_acre * chosen_pct) / 1e6               # GWh
    district_co2_tonnes = (district_kwh_gwh * 1e6 * 0.82) / 1000

    with calc_c2:
        st.markdown("#### 💧 Simulated Farm-Level Seasonal Impact")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Groundwater Saved", f"{water_saved_litres/100000:.1f} Lakh L", f"{(water_saved_litres/1e6):.2f} Million Litres")
        with sc2:
            st.metric("Pumping Power Saved", f"{kwh_saved:,.0f} kWh", f"₹{(kwh_saved * 6.5):,.0f} Cost Equivalent")
        with sc3:
            st.metric("Carbon Emissions Averted", f"{co2_saved_kg:,.0f} kg CO₂", f"{diesel_eq_litres:,.0f} L Diesel Eq.")

        st.markdown("---")
        st.markdown(f"#### 🌐 District-Scale Scalability Impact ({selected_district} Basin)")
        st.caption(f"Projected impact if 10% of district tube-well commands (~50,000 acres) adopt {selected_practice.split('(')[0]}:")
        
        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown(f"""
            <div class="metric-box" style="border-top-color: #28a745;">
                <div class="metric-label">Regional Water Conserved</div>
                <div class="metric-val">{district_water_saved_gl:.2f} <span style="font-size:1rem;">GL</span></div>
                <div class="metric-sub">{district_water_saved_gl * 1000:,.0f} Million Litres preserved</div>
            </div>
            """, unsafe_allow_html=True)
        with d2:
            st.markdown(f"""
            <div class="metric-box" style="border-top-color: #1f77b4;">
                <div class="metric-label">Grid Electricity Relieved</div>
                <div class="metric-val">{district_kwh_gwh:.2f} <span style="font-size:1rem;">GWh</span></div>
                <div class="metric-sub">{district_kwh_gwh * 1000:,.0f} Megawatt-hours saved</div>
            </div>
            """, unsafe_allow_html=True)
        with d3:
            st.markdown(f"""
            <div class="metric-box" style="border-top-color: #6f42c1;">
                <div class="metric-label">Climate Mitigation</div>
                <div class="metric-val">{district_co2_tonnes:,.0f} <span style="font-size:1rem;">t CO₂</span></div>
                <div class="metric-sub">Carbon abatement per season</div>
            </div>
            """, unsafe_allow_html=True)

# --- FEATURE 3: INTERACTIVE SOIL HEALTH CARD & INSTANT LAB PRESCRIPTION ---
with tab_soil_card:
    st.markdown("### 🧪 Interactive Soil Health Card & Instant Lab Prescription")
    st.caption("Input KVK / PAU laboratory test results to generate a precision per-acre corrective prescription.")

    sh1, sh2 = st.columns([1.5, 2.5])
    with sh1:
        st.markdown("#### 🔬 Enter Soil Lab Test Values")
        input_ph = st.number_input("Soil pH (Acidity/Alkalinity):", min_value=5.0, max_value=11.0, value=8.6, step=0.1, help="Normal range is 6.5 - 8.2. Values > 8.5 indicate alkaline/sodic soil.")
        input_ec = st.number_input("Electrical Conductivity EC (dS/m):", min_value=0.05, max_value=10.0, value=0.90, step=0.05, help="Normal < 0.8 dS/m. Values > 0.8 indicate soluble salt accumulation.")
        input_oc = st.number_input("Organic Carbon OC (%):", min_value=0.05, max_value=2.50, value=0.38, step=0.02, help="Punjab soils: Low < 0.40%, Medium 0.40-0.75%, High > 0.75%.")
        input_n = st.number_input("Available Nitrogen (kg/ha):", min_value=40.0, max_value=600.0, value=190.0, step=5.0, help="Low < 280 kg/ha, Medium 280-560 kg/ha.")

    # Prescription Logic
    gypsum_bags = max(0, int(round((input_ph - 8.4) * 5.0))) if input_ph > 8.4 else 0
    fym_tonnes = 5.0 if input_oc < 0.40 else (2.5 if input_oc < 0.75 else 0.0)
    leaching_needed = input_ec > 0.80
    extra_urea_pct = 25 if input_n < 280 else 0

    with sh2:
        st.markdown(f"#### 📋 Instant Per-Acre Soil Prescription ({lang_code.upper()})")
        
        # pH / Sodic condition
        if input_ph > 8.5:
            st.error(f"""
            **1. Alkalinity / Sodic Soil Flagged (pH = {input_ph:.1f} > 8.5):**  
            Apply **{gypsum_bags} bags/acre (50 kg each) Agricultural Gypsum ($CaSO_4 \cdot 2H_2O$)**.  
            *Application Rule:* Broadcast evenly and mix in the top 10 cm of soil before pre-sowing irrigation. The calcium displaces toxic sodium ($Na^+$), restoring soil permeability.
            """)
        else:
            st.success(f"**1. Soil pH Normal (pH = {input_ph:.1f}):** No gypsum required. Soil reaction is safe for crop roots.")

        # EC / Salinity
        if leaching_needed:
            st.warning(f"""
            **2. Soluble Salt Accumulation (EC = {input_ec:.2f} dS/m > 0.8 dS/m):**  
            Provide **5–7 cm leaching flood with good-quality canal water** prior to transplanting. Maintain boundary drainage channels to export salt wash.
            """)
        else:
            st.success(f"**2. Salinity Safe (EC = {input_ec:.2f} dS/m <= 0.8 dS/m):** Electrical conductivity is within optimal limits.")

        # Organic Carbon
        if input_oc < 0.40:
            st.error(f"""
            **3. Organic Carbon Critically Low (OC = {input_oc:.2f}% < 0.40%):**  
            Incorporate **{fym_tonnes:.1f} tonnes/acre well-decomposed Farmyard Manure (FYM)** or sow **Dhaincha (*Sesbania aculeata*) green manure** 45 days before paddy. Strictly maintain **Zero Stubble Burning**.
            """)
        elif input_oc < 0.75:
            st.info(f"**3. Organic Carbon Medium (OC = {input_oc:.2f}%):** Incorporate {fym_tonnes:.1f} tonnes/acre compost or retain crop residues with Happy Seeder.")
        else:
            st.success(f"**3. Organic Carbon Optimum (OC = {input_oc:.2f}%):** Soil biological carbon is well-preserved.")

        # Nitrogen & Zinc
        st.info(f"""
        **4. Nutrient & Micronutrient Supplementation:**  
        • **Nitrogen:** Available N is {input_n:.0f} kg/ha ({'Low' if input_n < 280 else 'Medium'}). {'Increase baseline urea application by 25% split across 3 stages.' if extra_urea_pct > 0 else 'Follow standard PAU urea recommendations.'}  
        • **Zinc Micronutrient:** Broadcast **25 kg/acre Zinc Sulfate Heptahydrate (21%)** at final puddling, or apply 0.5% $ZnSO_4$ foliar spray to prevent zinc deficiency chlorosis.
        """)

# --- TAB 5: ACTIONABLE ADVISORIES, WHATSAPP SHARING & VOICE ADVISORY ---
with tab_advisories:
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

    # --- FEATURE 4: ONE-CLICK WHATSAPP SHARE & WEB SPEECH AUDIO ---
    st.divider()
    st.markdown("#### 📲 Multi-Channel Farmer Outreach (WhatsApp & Voice)")

    outreach_col1, outreach_col2 = st.columns(2)

    with outreach_col1:
        st.markdown("##### 💬 Share Advisory on WhatsApp")
        # Prepare URL-encoded text
        share_summary = f"🚨 *Punjab Farm Water Watch Advisory*\n📍 District: {selected_district}\n💧 Water Stress: {stress_res['score']}/100 ({stress_res['zone']})\n🌱 Soil Health: {latest['landsat_ndvi']:.2f} NDVI\n\n📢 *Advisories:*\n" + "\n".join([f"• {a}" for a in advisories[:2]]) + "\n\n_Powered by NASA SMAP & Earth Observations_"
        encoded_wa_msg = urllib.parse.quote(share_summary)
        wa_url = f"https://wa.me/?text={encoded_wa_msg}"
        
        st.link_button("📲 Share Field Advisory on WhatsApp", wa_url, use_container_width=True)
        st.caption("Broadcasts formatted satellite water stress alert directly to farmer WhatsApp groups and local KVKs.")

    with outreach_col2:
        st.markdown("##### 🔊 Listen to Voice Advisory (ਆਵਾਜ਼ ਵਿੱਚ ਸੁਣੋ / आवाज़ में सुनें)")
        spoken_text = f"Punjab Farm Water Watch Advisory for {selected_district}. Water Stress Score is {stress_res['score']} out of 100. " + " ".join(advisories[:2])
        spoken_lang = "hi-IN" if lang_code == "hi" else ("hi-IN" if lang_code == "pa" else "en-IN")
        
        # Web Speech API Audio Component
        speech_html = f"""
        <div style="padding: 6px 0;">
            <button id="speakBtn" style="background-color: #2b5c8f; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 14px;">
                🔊 Read Advisory Aloud ({lang_code.upper()})
            </button>
            <button id="stopBtn" style="background-color: #e2e8f0; color: #333; border: none; padding: 10px 14px; border-radius: 8px; margin-left: 8px; cursor: pointer; font-size: 14px;">
                ⏹️ Stop
            </button>
            <div id="speechStatus" style="margin-top: 8px; font-size: 13px; color: #555;"></div>
        </div>
        <script>
            const textToSpeak = {json_text};
            const langCode = "{spoken_lang}";
            const speakBtn = document.getElementById("speakBtn");
            const stopBtn = document.getElementById("stopBtn");
            const statusDiv = document.getElementById("speechStatus");

            speakBtn.addEventListener("click", () => {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(textToSpeak);
                    utterance.lang = langCode;
                    utterance.rate = 0.95;
                    utterance.onstart = () => {{ statusDiv.innerText = "🔊 Playing voice advisory..."; }};
                    utterance.onend = () => {{ statusDiv.innerText = "✅ Completed audio playback."; }};
                    utterance.onerror = (e) => {{ statusDiv.innerText = "Audio playback status: " + e.error; }};
                    window.speechSynthesis.speak(utterance);
                }} else {{
                    statusDiv.innerText = "Web Speech API not supported in this browser window.";
                }}
            }});

            stopBtn.addEventListener("click", () => {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    statusDiv.innerText = "⏹️ Stopped.";
                }}
            }});
        </script>
        """.replace("{json_text}", pd.Series([spoken_text]).to_json(orient='values')[1:-1])

        components.html(speech_html, height=95)
        st.caption("Accessible audio narration for local growers via standard browser Web Speech API.")

    # --- FEATURE 5: ONE-CLICK DOWNLOADABLE DISTRICT OFFICER ACTION BRIEF ---
    st.divider()
    st.markdown("#### 📄 Export Official District Officer Brief")
    
    # Generate structured Markdown Brief
    brief_content = f"""# Punjab Farm Water Watch - District Action Brief
**NASA Space Apps Challenge 2026 · Delhi NCR**
**Team:** The SMAP Squad
**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Monitoring Scope & Centroid
* **Target Jurisdiction:** {selected_district}
* **Centroid Coordinates:** Latitude {lat_in:.4f}°N, Longitude {lon_in:.4f}°E
* **Agro-Ecological Classification:** Alluvial Breadbasket (Punjab)

---

## 2. Real-Time NASA Satellite Telemetry (Latest Observation)
* **NASA SMAP L4 Rootzone Moisture (0–100 cm):** {latest['smap_rootzone_sm']:.3f} m³/m³
* **NASA SMAP L4 Surface Moisture (0–5 cm):** {latest['smap_surface_sm']:.3f} m³/m³
* **NASA GPM IMERG 30-Day Cumulative Precipitation:** {rain_30d_val:.1f} mm
* **MODIS MOD16A2 Evapotranspiration:** {latest['modis_et_mm']:.2f} mm/day
* **Landsat 8/9 OLI Canopy NDVI:** {latest['landsat_ndvi']:.3f}
* **Landsat 8/9 OLI Canopy SAVI:** {latest['landsat_savi']:.3f}
* **Landsat 8/9 TIRS Land Surface Temperature:** {latest['landsat_lst_c']:.1f} °C
* **NASA POWER DAV Ambient Temperature:** {latest['power_temp_c']:.1f} °C
* **NASA GRACE Groundwater Equivalent Mass Anomaly:** {latest['grace_water_anomaly_cm']:.2f} cm

---

## 3. Water Stress Index & Attribution Breakdown
* **Composite Water Stress Score:** {stress_res['score']} / 100
* **Risk Categorization:** {stress_res['zone'].upper()} ZONE ({stress_res['status']})
* **Driver Attribution:**
  - SMAP Rootzone Soil Moisture Deficit: {stress_res['contributions']['smap']}% impact
  - GPM 30-Day Precipitation Deficit: {stress_res['contributions']['gpm']}% impact
  - MODIS Evapotranspiration Draw: {stress_res['contributions']['et']}% impact
  - Landsat Thermal Heat Anomaly: {stress_res['contributions']['lst']}% impact

---

## 4. Dual-Diagnosis Soil Health Audit
* **Anomaly Status:** {'ALERT TRIGGERED' if soil_res['alert_triggered'] else 'NORMAL'}
* **Diagnostic Code:** {soil_res['status_code']}
* **Assessment:** {soil_res['diagnosis']}
* **Prescription:**
  - Soil pH: {input_ph:.1f} -> {f'Apply {gypsum_bags} bags/acre Agricultural Gypsum' if input_ph > 8.5 else 'Normal pH range'}
  - Soil EC: {input_ec:.2f} dS/m -> {'Leaching flood with canal water required' if leaching_needed else 'Normal salinity'}
  - Soil OC: {input_oc:.2f}% -> {f'Apply {fym_tonnes} tonnes/acre Farmyard Manure & Dhaincha green manure' if input_oc < 0.5 else 'Adequate organic carbon'}
  - Zinc: 25 kg/acre Zinc Sulfate Heptahydrate (21%) recommended

---

## 5. 7-Day Machine Learning Predictive Outlook
| Day Horizon | Projected Moisture (m³/m³) | 90% Confidence Interval | Projected Water Stress | Risk Classification |
|---|---|---|---|---|
"""
    for f in fc_results:
        brief_content += f"| {f['day_label']} | {f['predicted_sm']:.3f} | {f['lower_sm_bound']:.3f} – {f['upper_sm_bound']:.3f} | {f['predicted_stress_score']:.1f} / 100 | {f['risk_zone']} |\n"

    brief_content += f"""
---

## 6. Official Field Advisories for Agricultural Officers
"""
    for adv in advisories:
        brief_content += f"* {adv}\n"

    brief_content += f"""
---
*Data Provenance: NASA Earthdata CMR (SPL4SMGP, GPM_3IMERGDF, MOD16A2, HLSL30, POWER_DAV, GRACE_TELLUS).*
"""

    down_c1, down_c2 = st.columns(2)
    with down_c1:
        st.download_button(
            label="📥 Download District Water & Soil Action Brief (Markdown)",
            data=brief_content,
            file_name=f"punjab_farm_water_watch_{selected_district.lower().replace(' ', '_')}_brief.md",
            mime="text/markdown",
            use_container_width=True
        )
    with down_c2:
        st.download_button(
            label="📊 Export 30-Day NASA Telemetry (CSV)",
            data=dist_df.to_csv(index=False),
            file_name=f"nasa_telemetry_{selected_district.lower().replace(' ', '_')}_30d.csv",
            mime="text/csv",
            use_container_width=True
        )

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
