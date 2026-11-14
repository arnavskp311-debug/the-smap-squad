"""
Pytest Suite for Punjab Farm Water Watch (NASA Space Apps Challenge 2026)
Verifies models, data pipelines, weights, spatial queries, and anomaly detection.
"""

import os
import pytest
import numpy as np
import pandas as pd
import xarray as xr

from model import WaterStressModel, SevenDayMoistureForecaster, SoilQualityAnomalyDetector
from src.models.water_stress_engine import WaterStressEngine
from src.models.forecast_model import MoistureForecaster
from src.models.soil_quality_checker import SoilQualityChecker
from src.pipeline.spatial_processor import SpatialProcessor
from src.pipeline.earthaccess_client import NASADataPipeline


def test_unified_weights():
    """Verify that both WaterStressModel and WaterStressEngine use identical weights summing to 1.0."""
    wse = WaterStressEngine()
    wsm = WaterStressModel()

    assert wse.w_sm == 0.40
    assert wse.w_rain == 0.30
    assert wse.w_et == 0.20
    assert wse.w_lst == 0.10
    assert round(wse.w_sm + wse.w_rain + wse.w_et + wse.w_lst, 5) == 1.0

    assert wsm.w_sm == 0.40
    assert wsm.w_rain == 0.30
    assert wsm.w_et == 0.20
    assert wsm.w_lst == 0.10


def test_scoring_zones():
    """Test classification into Green (0-30), Yellow (31-60), and Red (61-100)."""
    wsm = WaterStressModel()

    # Optimal moisture and rain -> Green
    res_green = wsm.compute_water_stress_score(smap_rootzone_sm=0.36, rain_30d_mm=55.0, modis_et_mm=2.0, landsat_lst_c=25.0)
    assert res_green["zone"] == "Green"
    assert res_green["score"] <= 30.0

    # Moderate conditions -> Yellow
    res_yellow = wsm.compute_water_stress_score(smap_rootzone_sm=0.23, rain_30d_mm=25.0, modis_et_mm=4.5, landsat_lst_c=32.0)
    assert res_yellow["zone"] == "Yellow"
    assert 30.0 < res_yellow["score"] <= 60.0

    # Severe drought conditions -> Red
    res_red = wsm.compute_water_stress_score(smap_rootzone_sm=0.10, rain_30d_mm=5.0, modis_et_mm=6.5, landsat_lst_c=40.0)
    assert res_red["zone"] == "Red"
    assert res_red["score"] > 60.0


def test_forecaster_drydown_and_bounds():
    """Verify 7-day RandomForest forecaster handles unfitted frames safely and bounds intervals."""
    # Test unfitted state safety
    mf = MoistureForecaster()
    dummy_df = pd.DataFrame({
        "smap_rootzone_sm": [0.25, 0.24, 0.23, 0.22, 0.21],
        "gpm_precipitation_mm": [0.0, 0.0, 0.0, 0.0, 0.0],
        "modis_et_mm": [4.5, 4.6, 4.4, 4.5, 4.5],
        "landsat_lst_c": [32.0, 32.5, 33.0, 32.2, 32.8]
    })
    preds = mf.predict_next_7_days(dummy_df)
    assert len(preds) == 7
    for p in preds:
        assert p["lower_sm_bound"] <= p["predicted_sm"] <= p["upper_sm_bound"]
        assert 0.0 <= p["predicted_stress_score"] <= 100.0


def test_soil_quality_anomaly_check():
    """Verify SMAP-vs-Landsat NDVI dual diagnosis logic."""
    detector = SoilQualityAnomalyDetector()

    # Adequate water but weak crop vigor -> Alert!
    alert = detector.evaluate_soil_anomaly(smap_rootzone_sm=0.30, water_stress_score=20.0, landsat_ndvi=0.32)
    assert alert["alert_triggered"] is True
    assert alert["status_code"] == "HIDDEN_SOIL_QUALITY_ALERT"

    # Both low -> Drought stress, not soil anomaly
    drought = detector.evaluate_soil_anomaly(smap_rootzone_sm=0.14, water_stress_score=75.0, landsat_ndvi=0.25)
    assert drought["alert_triggered"] is False
    assert drought["status_code"] == "WATER_DEFICIT"


def test_spatial_processor_lookup():
    """Verify pin-drop spatial query resolves to proper district."""
    sp = SpatialProcessor()
    loc = sp.locate_point(lat=30.2110, lon=74.9455)
    assert loc["district"] == "Bathinda"
    assert loc["is_inside"] is True


def test_processed_dataset_integrity():
    """Verify generated dataset contains Punjab districts and global hotspots."""
    csv_path = "data/processed/punjab_multi_satellite_30d.csv"
    assert os.path.exists(csv_path), "Processed CSV must exist"
    df = pd.read_csv(csv_path)

    districts = set(df["district"].unique())
    assert "Bathinda" in districts
    assert "Ludhiana" in districts
    assert "Patiala" in districts
    assert "Central Valley, California (Hotspot)" in districts
    assert "North Africa / Nile Basin (Hotspot)" in districts
    assert "High Plains Aquifer, USA (Hotspot)" in districts


def test_netcdf_multi_district_mosaic():
    """Verify NetCDF mosaic contains gridded multi-district data."""
    nc_path = "data/processed/punjab_satellite_mosaic.nc"
    assert os.path.exists(nc_path), "Mosaic NetCDF must exist"
    with xr.open_dataset(nc_path) as ds:
        assert "smap_rootzone_sm" in ds
        assert "landsat_ndvi" in ds
        assert ds["smap_rootzone_sm"].shape[0] > 10
        assert ds["smap_rootzone_sm"].shape[1] > 10


def test_i18n_and_soil_guide_integrity():
    """Verify trilingual localization dictionaries and PAU guide structures."""
    from src.advisories.i18n_content import I18N
    from src.advisories.soil_testing_guide import SOIL_TESTING_STEPS, REMEDIES_GUIDE

    for lang in ["en", "hi", "pa"]:
        assert lang in I18N, f"Missing language {lang}"
        assert "title" in I18N[lang]
        assert "advisories" in I18N[lang]
        assert "SAFE" in I18N[lang]["advisories"]
        assert "CRITICAL" in I18N[lang]["advisories"]

    assert len(SOIL_TESTING_STEPS) == 4, "Should have 4-step PAU soil sampling protocol"
    for s in SOIL_TESTING_STEPS:
        assert "title_en" in s and "title_hi" in s and "title_pa" in s
        assert "desc_en" in s and "desc_hi" in s and "desc_pa" in s

    assert len(REMEDIES_GUIDE) >= 4, "Should have at least 4 PAU field remedies"
    for r in REMEDIES_GUIDE:
        assert "remedy_en" in r and "remedy_hi" in r and "remedy_pa" in r


def test_crop_budget_simulator():
    """Verify water budget and energy savings calculation for crop alternatives."""
    from model import CropBudgetSimulator
    res = CropBudgetSimulator.calculate_budget("Direct Seeded Rice / DSR (~20% less water)", farm_acres=10)
    assert res["baseline_litres_m"] == 9.0
    assert res["crop_water_demand_m"] == 7.2
    assert res["groundwater_saved_m"] == 1.8
    assert res["kwh_saved"] > 1400
    assert res["pct_saved"] == 20.0


def test_smart_calendar_generator():
    """Verify 7-day smart calendar generation across forecast risk profiles."""
    from src.advisories.smart_calendar import generate_smart_calendar
    dummy_fc = [{"day_label": f"Day +{i}", "predicted_sm": 0.15, "risk_zone": "Red"} for i in range(1, 8)]
    dummy_soil = {"alert_triggered": True}
    cal = generate_smart_calendar(dummy_fc, dummy_soil, lang="hi")
    assert len(cal) == 7
    assert cal[0]["day_number"] == 1
    assert len(cal[0]["action"]) > 10


def test_auth_system():
    """Verify backend profile, registration, and user data persistence."""
    from server import load_users, signup_user, login_user, AuthRequest
    users = load_users()
    assert "arnav@punjabfarms.gov.in" in users
    assert users["arnav@punjabfarms.gov.in"]["member_id"] == "PWW-2026-PB-0482"

    # Test login with unregistered email fails
    unreg_req = AuthRequest(email="nonexistent@punjab.gov.in")
    login_res = login_user(unreg_req)
    assert login_res["status"] == "error"

    # Test signup
    from server import save_users
    if "steward@punjab.gov.in" in users:
        del users["steward@punjab.gov.in"]
        save_users(users)

    req = AuthRequest(
        name="Amritsar Steward",
        email="steward@punjab.gov.in",
        phone="+91 98765 00000",
        district="Amritsar",
        farm_acres=8.0,
        role="Water Steward",
        primary_crop="Mustard",
        irrigation_source="Canal Lift + Tubewell"
    )
    res = signup_user(req)
    assert res["status"] == "success"
    assert res["user"]["name"] == "Amritsar Steward"
    assert res["user"]["water_saved_litres"] == int(8.0 * 180000)
    assert "PWW-2026-PB-" in res["user"]["member_id"]

    # Test login with newly registered email succeeds
    login_res2 = login_user(req)
    assert login_res2["status"] == "success"
    assert login_res2["user"]["email"] == "steward@punjab.gov.in"


