"""
Punjab Farm Water Watch - Standard FastAPI Web Application
Developed by Team The SMAP Squad for NASA Space Apps Challenge 2026 (Delhi NCR)
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from pydantic import BaseModel
import pandas as pd
import geopandas as gpd

# Local models and data
from model import (
    WaterStressModel,
    SevenDayMoistureForecaster,
    SoilQualityAnomalyDetector,
    CropBudgetSimulator
)
from src.pipeline.spatial_processor import SpatialProcessor
from src.advisories.smart_calendar import generate_smart_calendar
from src.advisories.soil_testing_guide import SOIL_TESTING_STEPS, REMEDIES_GUIDE

app = FastAPI(title="Punjab Farm Water Watch", version="2.0.0")

# Initialize models
stress_model = WaterStressModel()
forecaster = SevenDayMoistureForecaster()
soil_detector = SoilQualityAnomalyDetector()
spatial = SpatialProcessor()

# Load processed satellite dataset
CSV_PATH = "data/processed/punjab_multi_satellite_30d.csv"
if not os.path.exists(CSV_PATH):
    from fetch_nasa_data import run_pipeline
    run_pipeline()

df_satellite = pd.read_csv(CSV_PATH)
df_satellite["date"] = pd.to_datetime(df_satellite["date"])

# Precompute district risk boundaries GeoJSON
districts_gdf = spatial.gdf

CORE_PUNJAB = ["Bathinda", "Sangrur", "Patiala", "Ludhiana", "Amritsar"]
ALL_PUNJAB_DISTRICTS = CORE_PUNJAB + sorted([d for d in districts_gdf["name"].unique() if d not in CORE_PUNJAB])
GLOBAL_HOTSPOTS = {
    "Central Valley (California, USA)": {"lat": 36.7783, "lon": -119.4179, "region": "North America"},
    "Nile Delta (Egypt)": {"lat": 30.8025, "lon": 31.0000, "region": "North Africa"},
    "Murray-Darling Basin (Australia)": {"lat": -33.9189, "lon": 142.1583, "region": "Oceania"}
}


class CropSimRequest(BaseModel):
    crop_choice: str
    farm_acres: float = 10.0


class SoilPrescriptionRequest(BaseModel):
    ph: float = 8.6
    ec: float = 0.9
    oc: float = 0.38
    nitrogen: int = 190


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Punjab Farm Water Watch",
        "nasa_live_status": True,
        "engine": "FastAPI Standard Web Server"
    }


@app.get("/api/districts")
def get_districts():
    return {
        "punjab_districts": ALL_PUNJAB_DISTRICTS,
        "global_hotspots": list(GLOBAL_HOTSPOTS.keys())
    }


@app.get("/api/geojson")
def get_geojson():
    # Return GeoJSON with precomputed scores
    features = []
    for _, row in districts_gdf.iterrows():
        dname = row["name"]
        sub = df_satellite[df_satellite["district"] == dname]
        if not sub.empty:
            l_row = sub.iloc[-1]
            r30 = float(sub["gpm_precipitation_mm"].sum())
            sc = stress_model.compute_water_stress_score(
                l_row["smap_rootzone_sm"], r30, l_row["modis_et_mm"], l_row["landsat_lst_c"]
            )
        else:
            sc = {"score": 25.0, "zone": "Green", "badge_color": "#16A34A", "status": "No Stress"}

        geom = json.loads(gpd.GeoSeries([row.geometry]).to_json())["features"][0]["geometry"]
        features.append({
            "type": "Feature",
            "properties": {
                "name": dname,
                "soil_type": row.get("soil_type", "Alluvial Loam"),
                "primary_crop": row.get("primary_crop", "Wheat-Rice"),
                "stress_score": sc["score"],
                "zone": sc["zone"],
                "color": "#DC2626" if sc["score"] > 60 else ("#F59E0B" if sc["score"] > 30 else "#16A34A")
            },
            "geometry": geom
        })
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/telemetry")
def get_telemetry(district: str = "Bathinda", lang: str = "en"):
    is_hotspot = district in GLOBAL_HOTSPOTS

    if is_hotspot:
        coords = GLOBAL_HOTSPOTS[district]
        lat = coords["lat"]
        lon = coords["lon"]
        dist_df = df_satellite[df_satellite["district"] == "Bathinda"].copy()
    else:
        dist_sub = df_satellite[df_satellite["district"] == district]
        matching_dist = districts_gdf[districts_gdf["name"] == district]
        if dist_sub.empty:
            if not matching_dist.empty:
                dist_sub = df_satellite[df_satellite["district"] == "Bathinda"].copy()
                dist_sub["district"] = district
            else:
                district = "Bathinda"
                dist_sub = df_satellite[df_satellite["district"] == "Bathinda"]
        dist_df = dist_sub.copy()
        if not matching_dist.empty:
            lat = float(matching_dist.geometry.centroid.y.iloc[0])
            lon = float(matching_dist.geometry.centroid.x.iloc[0])
        else:
            lat, lon = 30.2110, 74.9455

    latest = dist_df.iloc[-1]
    rain_30d = float(dist_df["gpm_precipitation_mm"].sum())

    # Stress model
    stress_res = stress_model.compute_water_stress_score(
        smap_rootzone_sm=float(latest["smap_rootzone_sm"]),
        rain_30d_mm=rain_30d,
        modis_et_mm=float(latest["modis_et_mm"]),
        landsat_lst_c=float(latest["landsat_lst_c"])
    )

    # Soil anomaly diagnosis
    soil_res = soil_detector.evaluate_soil_anomaly(
        smap_rootzone_sm=float(latest["smap_rootzone_sm"]),
        water_stress_score=float(stress_res["score"]),
        landsat_ndvi=float(latest["landsat_ndvi"]),
        landsat_savi=float(latest["landsat_savi"])
    )

    # 7-day Forecast
    fc_results = forecaster.predict_next_7_days(dist_df)

    # 7-day Smart Action Calendar
    calendar_days = generate_smart_calendar(fc_results, soil_res, lang=lang)

    # 30-day Delta metrics
    row_30d = dist_df.iloc[0]
    sm_old = float(row_30d["smap_rootzone_sm"])
    sm_now = float(latest["smap_rootzone_sm"])
    sm_diff = sm_now - sm_old

    ndvi_old = float(row_30d["landsat_ndvi"])
    ndvi_now = float(latest["landsat_ndvi"])
    ndvi_diff = ndvi_now - ndvi_old

    score_old = stress_model.compute_water_stress_score(
        smap_rootzone_sm=sm_old,
        rain_30d_mm=float(dist_df["gpm_precipitation_mm"].head(10).sum()) * 1.5,
        modis_et_mm=float(row_30d["modis_et_mm"]),
        landsat_lst_c=float(row_30d["landsat_lst_c"])
    )["score"]
    score_now = stress_res["score"]
    score_diff = score_now - score_old

    # Localized farmer advice
    if stress_res["zone"] == "Red":
        if lang == "pa":
            adv1 = "ਕਿਸਾਨ ਵੀਰੋ, 3 ਦਿਨ ਪਾਣੀ ਰੋਕੋ (Kisan veero, 3 din paani roko)"
            adv2 = "ਸਿੱਧੀ ਬਿਜਾਈ (DSR) ਅਤੇ ਮਲਚਿੰਗ ਅਪਣਾਓ (Adopt DSR & Mulching)"
        elif lang == "hi":
            adv1 = "किसान भाई, 3 दिन पानी रोक दें (जड़ क्षेत्र को हवा लगने दें)"
            adv2 = "सीधी बिजाई (DSR) और पुआल मल्चिंग अपनाएं"
        else:
            adv1 = "Farmers, pause irrigation for 3 days to preserve root aeration"
            adv2 = "Switch to Direct Seeded Rice (DSR) & Crop-Residue Mulching"
    elif stress_res["zone"] == "Yellow":
        if lang == "pa":
            adv1 = "ਜੜ੍ਹ ਖੇਤਰ ਵਿੱਚ ਦਰਮਿਆਨੀ ਨਮੀ ਦੀ ਘਾਟ - ਸਿੰਚਾਈ 2 ਦਿਨ ਟਾਲੋ"
            adv2 = "ਵਾਸ਼ਪੀਕਰਨ ਰੋਕਣ ਲਈ ਪਰਾਲੀ ਦੀ ਮਲਚਿੰਗ ਕਰੋ"
        elif lang == "hi":
            adv1 = "जड़-क्षेत्र में मध्यम नमी की कमी - सिंचाई 2 दिन टालें"
            adv2 = "वाष्पीकरण रोकने के लिए खेत में पुआल की मल्चिंग करें"
        else:
            adv1 = "Moderate moisture deficit: Delay flood irrigation by 2 days"
            adv2 = "Apply straw mulching to curb high surface evapotranspiration losses"
    else:
        if lang == "pa":
            adv1 = "ਫ਼ਸਲ ਲਈ ਪਾਣੀ ਕਾਫ਼ੀ ਹੈ - ਬੇਲੋੜੀ ਸਿੰਚਾਈ ਤੋਂ ਬਚੋ"
            adv2 = "ਜ਼ਮੀਨੀ ਪਾਣੀ ਬਚਾਉਣ ਲਈ ਤੁਪਕਾ ਜਾਂ ਫੁਹਾਰਾ ਸਿੰਚਾਈ ਅਪਣਾਓ"
        elif lang == "hi":
            adv1 = "फसल की मांग के लिए पानी पर्याप्त है - अतिरिक्त सिंचाई से बचें"
            adv2 = "भूजल स्तर बनाए रखने के लिए संतुलित सिंचाई करें"
        else:
            adv1 = "Water reserves are currently sufficient for crop demand"
            adv2 = "Avoid unnecessary over-irrigation to conserve regional groundwater"

    # Historical timeline data for line chart
    history_dates = dist_df["date"].dt.strftime("%b %d").tolist()
    history_sm = dist_df["smap_rootzone_sm"].round(3).tolist()

    return {
        "district": district,
        "is_hotspot": is_hotspot,
        "lat": lat,
        "lon": lon,
        "stress": stress_res,
        "soil_diagnosis": soil_res,
        "advisory": {"line1": adv1, "line2": adv2},
        "deltas": {
            "sm_now": round(sm_now, 3),
            "sm_old": round(sm_old, 3),
            "sm_diff": round(sm_diff, 3),
            "ndvi_now": round(ndvi_now, 3),
            "ndvi_old": round(ndvi_old, 3),
            "ndvi_diff": round(ndvi_diff, 3),
            "score_now": round(score_now, 1),
            "score_old": round(score_old, 1),
            "score_diff": round(score_diff, 1)
        },
        "latest": {
            "smap_rootzone_sm": round(float(latest["smap_rootzone_sm"]), 3),
            "smap_surface_sm": round(float(latest["smap_surface_sm"]), 3),
            "gpm_rain_30d": round(rain_30d, 1),
            "modis_et_mm": round(float(latest["modis_et_mm"]), 2),
            "landsat_ndvi": round(float(latest["landsat_ndvi"]), 3),
            "landsat_savi": round(float(latest["landsat_savi"]), 3),
            "landsat_lst_c": round(float(latest["landsat_lst_c"]), 1),
            "grace_anomaly_cm": round(float(latest["grace_water_anomaly_cm"]), 2)
        },
        "chart_data": {
            "history_dates": history_dates,
            "history_sm": history_sm,
            "forecast_dates": [f["day_label"] for f in fc_results],
            "forecast_sm": [round(f["predicted_sm"], 3) for f in fc_results],
            "forecast_lower": [round(f["lower_sm_bound"], 3) for f in fc_results],
            "forecast_upper": [round(f["upper_sm_bound"], 3) for f in fc_results]
        },
        "forecast_results": fc_results,
        "calendar_days": calendar_days
    }


@app.post("/api/simulator/crop")
def simulate_crop(req: CropSimRequest):
    return CropBudgetSimulator.calculate_budget(req.crop_choice, farm_acres=req.farm_acres)


@app.post("/api/simulator/soil")
def simulate_soil(req: SoilPrescriptionRequest):
    gypsum_bags = 2 if req.ph > 8.5 else 0
    fym_tonnes = 4 if req.oc < 0.5 else 0
    gypsum_text = f"• {gypsum_bags} Bags Gypsum/Acre" if gypsum_bags > 0 else "• Gypsum: Normal (No Treatment Needed)"
    compost_text = f"• {fym_tonnes}t Compost / FYM / Acre" if fym_tonnes > 0 else "• Compost: Adequate Carbon"
    zinc_text = "• Zinc Sulfate Dose (25 kg/ha ZnSO4)" if req.nitrogen < 250 else "• Basal N-P-K Application"

    status = "Alkaline / Low Carbon Soil — Immediate Conditioning Required" if (gypsum_bags > 0 or fym_tonnes > 0) else "Balanced Agronomic State"

    return {
        "gypsum_bags": gypsum_bags,
        "fym_tonnes": fym_tonnes,
        "prescription": [gypsum_text, compost_text, zinc_text],
        "status": status,
        "status_color": "#F87171" if (gypsum_bags > 0 or fym_tonnes > 0) else "#4ADE80"
    }


@app.get("/api/report/{district}")
def get_report(district: str = "Bathinda"):
    telemetry = get_telemetry(district)
    latest = telemetry["latest"]
    stress = telemetry["stress"]
    soil = telemetry["soil_diagnosis"]
    fc = telemetry["forecast_results"]

    md = f"""# Punjab Farm Water Watch - District Officer Brief
**NASA Space Apps Challenge 2026 · Delhi NCR**
**Team:** The SMAP Squad (Arnav Sharma [Lead & Coder], Chetan Kaushik [Coder], Aryan Sharma [Researcher], Amisha Ajana [Designer])
**Target District:** {district} (Coordinates: {telemetry['lat']:.4f}°N, {telemetry['lon']:.4f}°E)
**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

### 1. Water Stress Score & Multi-Satellite Metrics
* **Composite Water Stress Score:** {stress['score']} / 100 ({stress['zone']} Zone)
* **NASA SMAP L4 Rootzone Moisture (0–100 cm):** {latest['smap_rootzone_sm']:.3f} m³/m³
* **NASA SMAP L4 Surface Moisture (0–5 cm):** {latest['smap_surface_sm']:.3f} m³/m³
* **NASA GPM IMERG 30-Day Precipitation:** {latest['gpm_rain_30d']:.1f} mm
* **MODIS MOD16A2 Evapotranspiration:** {latest['modis_et_mm']:.2f} mm/day
* **Landsat 8/9 OLI Canopy NDVI:** {latest['landsat_ndvi']:.3f}
* **Landsat 8/9 OLI Canopy SAVI:** {latest['landsat_savi']:.3f}
* **NASA GRACE Groundwater Anomaly:** {latest['grace_anomaly_cm']:.2f} cm

---

### 2. Dual-Diagnosis Soil Quality Audit
* **Anomaly Status:** {'ALERT TRIGGERED' if soil['alert_triggered'] else 'NORMAL'}
* **Diagnosis:** {soil['diagnosis']}
* **Recommended Dose:** 2 Bags Agricultural Gypsum/Acre, 4t Compost/Acre, and 25 kg/ha Zinc Sulfate.

---

### 3. 7-Day Machine Learning Predictive Outlook
| Day | Projected Soil Moisture (m³/m³) | 90% Confidence Interval | Projected Water Stress |
|---|---|---|---|
"""
    for f in fc:
        md += f"| {f['day_label']} | {f['predicted_sm']:.3f} | {f['lower_sm_bound']:.3f} – {f['upper_sm_bound']:.3f} | {f['predicted_stress_score']:.1f} / 100 |\n"

    md += """
---

### 4. PAU / ICAR 15 cm Soil Testing Protocol for Extension Officers
1. **Field Stratification:** Select 5–6 representative spots in a zigzag pattern across the field, avoiding field bunds and shade trees.
2. **15 cm V-Cut Sampling:** Dig a V-shaped pit to 15 cm depth (active plow layer) and slice a uniform 2 cm core.
3. **Composite Quartering:** Mix in clean bucket, break clods, divide into 4 quarters, discarding opposite pairs until ~500g remains.
4. **Lab Submission:** Air-dry in shade (never sun-bake); submit to local KVK/PAU laboratory for pH, EC, OC, N-P-K, and micronutrients.

---
*Data Sources: NASA SMAP, GPM IMERG, Landsat 8/9, MODIS, POWER, GRACE.*
"""
    return PlainTextResponse(content=md, media_type="text/markdown")


# Mount static frontend directory
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Punjab Farm Water Watch Standalone Web Server...")
    print("👉 Open in browser: http://localhost:8000")
    uvicorn.run("server.py:app", host="0.0.0.0", port=8000, reload=True)
