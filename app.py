"""
Punjab Farm Water Watch - Interactive NASA Earth Observation Dashboard
Developed by Team The SMAP Squad for NASA Space Apps Challenge 2026 (Delhi NCR)

Core Capabilities:
- Trilingual Support: English, Hindi (हिन्दी), Punjabi (ਪੰਜਾਬੀ)
- Interactive Leaflet/Folium Map with Pin-Drop Field Query & District Choropleth
- 0-100 Water Stress Score Engine (SMAP 40%, GPM 30%, MODIS 20%, Landsat 10%)
- 7-Day RandomForestRegressor Predictive Forecast with 90% Confidence Interval
- SMAP-vs-Landsat NDVI/SAVI Dual Diagnosis for Hidden Soil-Quality & Salinity Degradation
- Step-by-Step 15 cm PAU/KVK Soil Testing Guide & In-App Remedies (Gypsum, Green Manuring, ZnSO4)
- Global Groundwater Hotspot Mode (Punjab, Central Valley, Nile Basin, High Plains)
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

# Import analytical models and data fetcher
from model import WaterStressModel, SevenDayMoistureForecaster, SoilQualityAnomalyDetector
from fetch_nasa_data import NASADataFetcher, REGIONAL_BOUNDING_BOXES

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


# --- MULTILINGUAL DICTIONARIES ---
LANG_DICT = {
    "en": {
        "title": "Punjab Farm Water Watch",
        "subtitle": "Water Scarcity & Soil-Quality Early Warning System powered by NASA Earth Observations",
        "team": "NASA Space Apps Challenge 2026 · Delhi NCR · Team The SMAP Squad",
        "lang_name": "English",
        "select_region": "Select Monitoring Region / Hotspot",
        "select_district": "Select Punjab District",
        "pindrop_title": "Interactive Pin-Drop Field Query",
        "pindrop_help": "Click anywhere on the satellite map to query field-specific soil moisture & water stress.",
        "kpi_score": "Water Stress Score",
        "kpi_smap": "SMAP Rootzone Soil Moisture",
        "kpi_rain": "GPM 30-Day Rainfall",
        "kpi_et": "MODIS Evapotranspiration",
        "kpi_soil": "Soil Health Diagnostics",
        "alert_title": "Actionable Farmer Advisories",
        "forecast_title": "7-Day Machine Learning Moisture & Stress Forecast",
        "timeline_title": "30-Day Multi-Satellite Observation Timeline",
        "provenance_watermark": "Source: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, NASA POWER, GRACE",
        "red_advisories": [
            "Kisan bhai, delay irrigation by 3 days if light rain is forecast ('3 din paani rok do').",
            "Transition immediately to Direct Seeded Rice (DSR) or alternate wetting & drying (AWD) to save 25% water.",
            "Apply paddy straw / crop residue mulching at 2-3 tonnes/acre to reduce soil evaporation.",
            "Prioritize evening irrigation to avoid peak midday evaporative losses."
        ],
        "yellow_advisories": [
            "Moderate rootzone moisture deficit detected. Monitor tubewell electricity schedules closely.",
            "Inspect soil surface for cracking; apply light conservation irrigation only.",
            "Prepare straw mulching before temperature rises."
        ],
        "green_advisories": [
            "Rootzone moisture is currently sufficient for crop growth.",
            "Avoid over-irrigation to conserve critical regional groundwater.",
            "Check field drainage to prevent water stagnation in low-lying plots."
        ]
    },
    "hi": {
        "title": "पंजाब फार्म वाटर वॉच (Punjab Farm Water Watch)",
        "subtitle": "नासा (NASA) उपग्रह डेटा द्वारा संचालित जल संकट एवं मृदा-गुणवत्ता पूर्व चेतावनी प्रणाली",
        "team": "नासा स्पेस ऐप्स चैलेंज 2026 · दिल्ली एनसीआर · टीम द स्मैप स्क्वाड (The SMAP Squad)",
        "lang_name": "हिन्दी (Hindi)",
        "select_region": "निगरानी क्षेत्र / हॉटस्पॉट चुनें",
        "select_district": "पंजाब का जिला चुनें",
        "pindrop_title": "इंटरएक्टिव पिन-ड्रॉप खेत जांच (Pin-Drop)",
        "pindrop_help": "खेत की नमी और जल संकट की स्थिति जानने के लिए उपग्रह मानचित्र पर कहीं भी क्लिक करें।",
        "kpi_score": "जल तनाव स्कोर (0-100)",
        "kpi_smap": "स्मैप (SMAP) जड़-क्षेत्र मृदा नमी",
        "kpi_rain": "GPM 30-दिनों की कुल बारिश",
        "kpi_et": "MODIS वाष्पीकरण दर (ET)",
        "kpi_soil": "मृदा गुणवत्ता जांच",
        "alert_title": "किसान भाइयों के लिए जरूरी सलाह",
        "forecast_title": "7-दिवसीय मशीन लर्निंग पूर्वानुमान (RandomForest)",
        "timeline_title": "30-दिनों का उपग्रह अवलोकन इतिहास",
        "provenance_watermark": "स्रोत: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, NASA POWER, GRACE",
        "red_advisories": [
            "किसान भाई, 3 दिन पानी रोक दो ('Kisan bhai, 3 din paani rok do') - यदि हल्की बारिश की संभावना हो।",
            "धान की सीधी बिजाई (DSR) या तर-वत्तर विधि अपनाएं, जिससे 20-25% पानी की बचत होती है।",
            "वाष्पीकरण रोकने के लिए खेत में 2-3 टन प्रति एकड़ पुआल की मल्चिंग (Mulching) करें।",
            "दोपहर की तेज धूप के बजाय शाम को सिंचाई करें ताकि पानी भाप बनकर न उड़े।"
        ],
        "yellow_advisories": [
            "जड़-क्षेत्र में नमी की मध्यम कमी है। बिजली शेड्यूल के अनुसार ही ट्यूबवेल चलाएं।",
            "खेत में दरारें देखें और आवश्यकता पड़ने पर ही हल्की सिंचाई करें।",
            "आगामी तापमान वृद्धि से पहले मल्चिंग की तैयारी रखें।"
        ],
        "green_advisories": [
            "फसल के लिए मिट्टी में पानी पर्याप्त है।",
            "भूजल बचाने के लिए अतिरिक्त सिंचाई से बचें।",
            "निचले खेतों में जलभराव रोकने के लिए उचित जल निकासी रखें।"
        ]
    },
    "pa": {
        "title": "ਪੰਜਾਬ ਫਾਰਮ ਵਾਟਰ ਵਾਚ (Punjab Farm Water Watch)",
        "subtitle": "ਨਾਸਾ (NASA) ਉਪਗ੍ਰਹਿ ਡਾਟੇ 'ਤੇ ਅਧਾਰਤ ਪਾਣੀ ਦੀ ਘਾਟ ਅਤੇ ਮਿੱਟੀ ਦੀ ਪਰਖ ਪ੍ਰਣਾਲੀ",
        "team": "ਨਾਸਾ ਸਪੇਸ ਐਪਸ ਚੈਲੇਂਜ 2026 · ਦਿੱਲੀ ਐਨਸੀਆਰ · ਟੀਮ ਦ ਸਮੈਪ ਸਕੁਐਡ (The SMAP Squad)",
        "lang_name": "ਪੰਜਾਬੀ (Punjabi)",
        "select_region": "ਨਿਗਰਾਨੀ ਖੇਤਰ / ਹੌਟਸਪੌਟ ਚੁਣੋ",
        "select_district": "ਪੰਜਾਬ ਦਾ ਜ਼ਿਲ੍ਹਾ ਚੁਣੋ",
        "pindrop_title": "ਪਿੰਨ-ਡ੍ਰੌਪ ਖੇਤ ਪਰਖ (Pin-Drop Query)",
        "pindrop_help": "ਖੇਤ ਵਿੱਚ ਨਮੀ ਅਤੇ ਪਾਣੀ ਦੇ ਤਣਾਅ ਦੀ ਜਾਂਚ ਲਈ ਨਕਸ਼ੇ 'ਤੇ ਕਿਤੇ ਵੀ ਕਲਿੱਕ ਕਰੋ।",
        "kpi_score": "ਪਾਣੀ ਦੀ ਘਾਟ ਦਾ ਸਕੋਰ (0-100)",
        "kpi_smap": "SMAP ਜੜ੍ਹ-ਖੇਤਰ ਮਿੱਟੀ ਨਮੀ",
        "kpi_rain": "GPM 30 ਦਿਨਾਂ ਦੀ ਕੁੱਲ ਬਾਰਿਸ਼",
        "kpi_et": "MODIS ਵਾਸ਼ਪੀਕਰਨ ਦਰ (ET)",
        "kpi_soil": "ਮਿੱਟੀ ਦੀ ਗੁਣਵੱਤਾ ਸਥਿਤੀ",
        "alert_title": "ਕਿਸਾਨਾਂ ਲਈ ਜ਼ਰੂਰੀ ਸਲਾਹ",
        "forecast_title": "7 ਦਿਨਾਂ ਦਾ ਮਸ਼ੀਨ ਲਰਨਿੰਗ ਭਵਿੱਖਬਾਣੀ ਅੰਦਾਜ਼ਾ",
        "timeline_title": "30 ਦਿਨਾਂ ਦਾ ਉਪਗ੍ਰਹਿ ਨਿਰੀਖਣ ਰਿਕਾਰਡ",
        "provenance_watermark": "ਸਰੋਤ: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, NASA POWER, GRACE",
        "red_advisories": [
            "ਕਿਸਾਨ ਵੀਰੋ, 3 ਦਿਨ ਪਾਣੀ ਰੋਕ ਲਵੋ ('Kisan veero, 3 din paani rok lo') - ਜੇਕਰ ਮੀਂਹ ਦੇ ਆਸਾਰ ਹੋਣ।",
            "ਝੋਨੇ ਦੀ ਸਿੱਧੀ ਬਿਜਾਈ (DSR) ਜਾਂ ਤਰ-ਵੱਤਰ ਵਿਧੀ ਦੀ ਵਰਤੋਂ ਕਰੋ, ਜਿਸ ਨਾਲ 25% ਪਾਣੀ ਬਚਦਾ ਹੈ।",
            "ਜ਼ਮੀਨ ਵਿੱਚ ਸਿੱਲ੍ਹ ਬਚਾਉਣ ਲਈ 2-3 ਟਨ ਪ੍ਰਤੀ ਏਕੜ ਪਰਾਲੀ ਦੀ ਮਲਚਿੰਗ (Mulching) ਕਰੋ।",
            "ਸਿੰਚਾਈ ਹਮੇਸ਼ਾ ਸ਼ਾਮ ਵੇਲੇ ਕਰੋ ਤਾਂ ਜੋ ਤੇਜ਼ ਧੁੱਪ ਵਿੱਚ ਪਾਣੀ ਉੱਡ ਨਾ ਜਾਵੇ।"
        ],
        "yellow_advisories": [
            "ਜੜ੍ਹਾਂ ਵਿੱਚ ਨਮੀ ਦੀ ਦਰਮਿਆਨੀ ਕਮੀ ਹੈ। ਟਿਊਬਵੈੱਲ ਬਿਜਲੀ ਦੇ ਸ਼ਡਿਊਲ ਅਨੁਸਾਰ ਹੀ ਚਲਾਓ।",
            "ਖੇਤ ਵਿੱਚ ਤਰੇੜਾਂ ਦੀ ਜਾਂਚ ਕਰੋ ਅਤੇ ਸਿਰਫ਼ ਹਲਕਾ ਪਾਣੀ ਲਾਓ।",
            "ਗਰਮੀ ਵਧਣ ਤੋਂ ਪਹਿਲਾਂ ਪਰਾਲੀ ਦੀ ਮਲਚਿੰਗ ਦਾ ਪ੍ਰਬੰਧ ਕਰੋ।"
        ],
        "green_advisories": [
            "ਫਸਲ ਲਈ ਮਿੱਟੀ ਵਿੱਚ ਪਾਣੀ ਕਾਫੀ ਹੈ।",
            "ਜ਼ਮੀਨੀ ਪਾਣੀ ਬਚਾਉਣ ਲਈ ਬੇਲੋੜੀ ਸਿੰਚਾਈ ਨਾ ਕਰੋ।",
            "ਨੀਵੇਂ ਖੇਤਾਂ ਵਿੱਚ ਪਾਣੀ ਖੜ੍ਹਨ ਤੋਂ ਰੋਕਣ ਲਈ ਨਿਕਾਸੀ ਦਾ ਪ੍ਰਬੰਧ ਰੱਖੋ।"
        ]
    }
}

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
def load_models():
    return WaterStressModel(), SevenDayMoistureForecaster(), SoilQualityAnomalyDetector()

df_all = load_datasets()
stress_model, forecaster, soil_detector = load_models()

# Load District GeoJSON
geojson_path = "data/geo/punjab_districts.geojson"
gdf_districts = gpd.read_file(geojson_path)
if gdf_districts.crs is None:
    gdf_districts.set_crs(epsg=4326, inplace=True)

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
        format_func=lambda x: LANG_DICT[x]["lang_name"]
    )
    t = LANG_DICT[lang_code]

    # Global Hotspot Mode Switcher
    st.subheader(f"🌍 {t['select_region']}")
    selected_region = st.selectbox("Monitoring Region", list(REGIONAL_BOUNDING_BOXES.keys()), index=0)
    is_global_hotspot = selected_region != "Punjab, India (Primary)"

    st.divider()
    if not is_global_hotspot:
        st.subheader(f"📍 {t['select_district']}")
        district_names = list(gdf_districts["name"])
        selected_district = st.selectbox("District", district_names, index=0)

        dist_row = gdf_districts[gdf_districts["name"] == selected_district].iloc[0]
        st.caption(f"Soil Type: **{dist_row['soil_type']}** | Rotation: **{dist_row['primary_crop']}**")

        st.markdown("#### 🎯 Pin-Drop GPS Coordinates")
        lat_in = st.number_input("Latitude (°N)", value=float(dist_row["lat"]), format="%.4f")
        lon_in = st.number_input("Longitude (°E)", value=float(dist_row["lon"]), format="%.4f")
    else:
        st.info(f"Viewing Global Hotspot: **{selected_region}**.\nNASA GRACE monitors secular groundwater loss across this basin.")
        selected_district = "Bathinda"
        lat_in, lon_in = 36.5, -119.5 if "Central Valley" in selected_region else (28.0, 31.0 if "Nile" in selected_region else (37.0, -100.5))

    st.divider()
    st.markdown("#### 🛰️ 6 NASA Datasets Active")
    st.caption("• NASA SMAP L4 (Soil Moisture 0-100cm)\n• GPM IMERG (Daily Rain)\n• MODIS MOD16A2 (ET)\n• Landsat 8/9 (NDVI/SAVI/LST)\n• NASA POWER (Temp, Humidity, Wind)\n• GRACE/GRACE-FO (Groundwater Anomaly)")

# Filter data for active district
dist_df = df_all[df_all["district"] == selected_district].copy()
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

# --- MAIN DASHBOARD HEADER ---
head_col1, head_col2 = st.columns([3.8, 1.2])
with head_col1:
    st.title(f"🌾 {t['title']}")
    st.markdown(f"**{t['subtitle']}**")
    st.caption(f"{t['team']} · Domain: Earth Observation & Agronomic Resilience")

with head_col2:
    tag_class = f"tag-{stress_res['zone'].lower()}"
    st.markdown(f"<div style='text-align:right; margin-top:14px;'><span class='{tag_class}'>{stress_res['zone'].upper()} ZONE ({stress_res['score']}/100)</span></div>", unsafe_allow_html=True)
    if soil_res["alert_triggered"]:
        st.markdown("<div style='text-align:right; margin-top:8px;'><span class='tag-soil-alert'>⚠️ SOIL QUALITY ALERT</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:right; margin-top:8px;'><span class='tag-green'>✅ OPTIMAL SOIL-WATER BALANCE</span></div>", unsafe_allow_html=True)

st.divider()

# --- TOP TIER: 5 HIGH-CONTRAST KPI METRIC CARDS ---
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-box" style="border-top-color: {stress_res['badge_color']};">
        <div class="metric-label">{t['kpi_score']}</div>
        <div class="metric-val">{stress_res['score']}<span style="font-size:1.1rem; color:#888;"> / 100</span></div>
        <div class="metric-sub"><span class="{tag_class}">{stress_res['status']}</span></div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{t['kpi_smap']}</div>
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
        <div class="metric-label">{t['kpi_et']}</div>
        <div class="metric-val">{latest['modis_et_mm']:.1f} <span style="font-size:0.9rem;">mm/day</span></div>
        <div class="metric-sub">Atmospheric crop draw (MODIS MOD16A2)</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    soil_badge = "<span class='tag-soil-alert'>ANOMALY DETECTED</span>" if soil_res["alert_triggered"] else "<span class='tag-green'>NORMAL</span>"
    st.markdown(f"""
    <div class="metric-box" style="border-top-color: {'#6f42c1' if soil_res['alert_triggered'] else '#28a745'};">
        <div class="metric-label">{t['kpi_soil']}</div>
        <div class="metric-val">NDVI {latest['landsat_ndvi']:.2f}</div>
        <div class="metric-sub">{soil_badge} (Landsat 8/9 OLI)</div>
    </div>
    """, unsafe_allow_html=True)

# --- CORE TIER: INTERACTIVE LEAFLET/FOLIUM MAP & PIN-DROP QUERY ---
st.markdown(f"### 🗺️ {t['pindrop_title']}")
st.caption(t["pindrop_help"])

map_left, map_right = st.columns([3, 2])

with map_left:
    if not is_global_hotspot:
        center_lat, center_lon, zoom_level = lat_in, lon_in, 8
    else:
        center_lat, center_lon, zoom_level = lat_in, lon_in, 6

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles="CartoDB positron")

    if not is_global_hotspot:
        # Style function for Punjab districts
        def district_style(feat):
            dname = feat["properties"]["name"]
            # Color code Bathinda Red, Sangrur/Patiala Yellow, Ludhiana/Amritsar Green
            fill = "#dc3545" if dname == "Bathinda" else "#ffc107" if dname in ["Sangrur", "Patiala"] else "#28a745"
            return {
                "fillColor": fill,
                "color": "#2c3e50",
                "weight": 2.2,
                "fillOpacity": 0.45
            }

        folium.GeoJson(
            gdf_districts,
            name="Punjab Agricultural Districts",
            style_function=district_style,
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "soil_type", "primary_crop"],
                aliases=["District:", "Soil Type:", "Primary Crop:"]
            )
        ).add_to(m)

        # Place pin marker at active query point
        folium.Marker(
            [lat_in, lon_in],
            popup=f"<b>Field Query Point</b><br>District: {selected_district}<br>Stress Score: {stress_res['score']}/100",
            icon=folium.Icon(color="red" if stress_res["zone"]=="Red" else "orange" if stress_res["zone"]=="Yellow" else "green", icon="info-sign")
        ).add_to(m)
    else:
        folium.Marker(
            [lat_in, lon_in],
            popup=f"<b>Global Groundwater Hotspot</b><br>{selected_region}<br>NASA GRACE Secular Deficit: -1.8 to -3.2 cm/yr",
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
st.markdown(f"### 📊 {t['timeline_title']} & Predictive Analytics")

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

# Filter by selected date range
mask_date = (pd.to_datetime(dist_df["date"]).dt.date >= slider_range[0]) & (pd.to_datetime(dist_df["date"]).dt.date <= slider_range[1])
filtered_df = dist_df[mask_date]

tab_charts, tab_ml, tab_soil_guide, tab_advisories_panel = st.tabs([
    f"📈 {t['timeline_title']}",
    f"🔮 {t['forecast_title']}",
    "🧪 Soil-Testing Guide & In-App Remedies",
    f"📢 {t['alert_title']}"
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

    # NASA Attribution Provenance
    st.markdown(f"<div class='provenance-tag'>🛡️ {t['provenance_watermark']}</div>", unsafe_allow_html=True)

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
            title="Projected Rootzone Moisture (Next 7 Days)",
            xaxis_title="Forecast Horizon",
            yaxis_title="Predicted Soil Moisture (m³/m³)",
            template="plotly_white",
            height=380
        )
        st.plotly_chart(fig_fc, use_container_width=True)
        st.markdown(f"<div class='provenance-tag'>🛡️ {t['provenance_watermark']}</div>", unsafe_allow_html=True)

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
        st.markdown("""
        1. **Stratification & Spot Selection:** Walk the field in a **zigzag pattern**. Select 5–6 representative spots, strictly avoiding field bunds, compost heaps, and shade trees.
        2. **V-Shaped 15 cm Cut:** Clear surface vegetation. Dig a V-shaped pit to **15 cm depth** (active root zone layer). Take a uniform 2 cm slice from top to bottom.
        3. **Composite Mixing & Quartering:** Mix all 5–6 sub-samples in a clean plastic bucket. Break soil lumps, spread on paper, divide into 4 quarters, and discard opposite quarters until ~500 grams remain.
        4. **Lab Submission:** Air-dry sample in shade (never heat in oven/sun). Place in a labeled cloth bag stating Farmer Name, Village, and Survey No., then submit to nearest **KVK (Krishi Vigyan Kendra)** or **PAU Soil Testing Lab**.
        5. **Mandatory Lab Tests:** Ensure the lab tests for **pH (alkalinity), EC (salinity), Organic Carbon (OC), available N-P-K, and micronutrients (Zinc & Iron)**.
        """)

    with col_sg2:
        st.markdown("#### 🛠️ In-App Soil Remediation & Fixes")
        st.warning("""
        **1. Alkaline / Sodic Soil (pH > 8.5, ESP > 15%):**
        Apply **Agricultural Grade Gypsum (Calcium Sulfate)** based on soil test (typically 2–4 bags/acre). Mix thoroughly in top 10 cm before pre-sowing irrigation to flush displaced sodium downward.
        """)
        st.info("""
        **2. Saline Soil (EC > 4.0 dS/m):**
        Leach surface salts with good quality canal water. Ensure laser land leveling and deep sub-soiling to break puddling-induced hardpans.
        """)
        st.success("""
        **3. Low Organic Carbon (< 0.40%) & Micronutrient Deficiency:**
        Practice **Green Manuring with Dhaincha (Sesbania)** 45–50 days before transplanting. Apply 25 kg/acre Zinc Sulfate ($ZnSO_4$). Strictly maintain **Zero Stubble Burning** to restore soil microbial ecology.
        """)

with tab_advisories_panel:
    st.markdown(f"### 📢 {t['alert_title']} ({t['lang_name']})")
    
    if stress_res["zone"] == "Red":
        st.error(f"🚨 **CRITICAL SCARCITY ALERT (Score: {stress_res['score']}/100)**")
        for adv in t["red_advisories"]:
            st.markdown(f"- ⚠️ **{adv}**")
    elif stress_res["zone"] == "Yellow":
        st.warning(f"⚠️ **MODERATE WATER STRESS ALERT (Score: {stress_res['score']}/100)**")
        for adv in t["yellow_advisories"]:
            st.markdown(f"- 🌾 **{adv}**")
    else:
        st.success(f"✅ **NORMAL / SAFE WATER ZONE (Score: {stress_res['score']}/100)**")
        for adv in t["green_advisories"]:
            st.markdown(f"- 🌱 **{adv}**")

    st.divider()
    st.markdown("#### 🌾 Core Climate-Smart Practices for Punjab Wheat-Paddy Rotations")
    adv_c1, adv_c2 = st.columns(2)
    with adv_c1:
        st.info("🚜 **Tar-Watter Direct Seeded Rice (DSR):** Saves 15–20 cm of irrigation water, reduces methane emissions, and protects soil structure from puddling hardpan compaction.")
    with adv_c2:
        st.success("🌱 **Crop Residue Mulching:** Spreading 2.5 tonnes/acre of paddy straw protects surface moisture from intense May–June evapotranspiration losses.")

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
