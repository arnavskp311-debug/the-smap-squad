"""
Punjab Farm Water Watch - Machine Learning & Diagnostic Scoring Engine
Team: The SMAP Squad · NASA Space Apps Challenge 2026 (Delhi NCR)

Wires directly into src/ modules for unified, production-grade architecture:
1. WaterStressEngine / WaterStressModel (0-100 Multi-Satellite Scarcity Index)
   Formula: 0.40 * SMAP + 0.30 * GPM + 0.20 * MODIS + 0.10 * Landsat LST
2. SevenDayMoistureForecaster / MoistureForecaster (scikit-learn RandomForestRegressor)
3. SoilQualityAnomalyDetector / SoilQualityChecker (Dual Diagnosis SMAP vs Landsat NDVI Anomaly)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Wire into core src/ modules
from src.models.water_stress_engine import WaterStressEngine
from src.models.soil_quality_checker import SoilQualityChecker
from src.models.forecast_model import MoistureForecaster


class WaterStressModel(WaterStressEngine):
    """
    Subclasses WaterStressEngine to provide compute_water_stress_score method
    with exact unified weights (40% SMAP, 30% GPM, 20% MODIS, 10% LST).
    """
    def compute_water_stress_score(self, smap_rootzone_sm, rain_30d_mm, modis_et_mm, landsat_lst_c):
        res = self.calculate_score(smap_rootzone_sm, rain_30d_mm, modis_et_mm, landsat_lst_c)
        return {
            "score": res["score"],
            "zone": res["zone"],
            "status": res["status"],
            "badge_color": res["badge_color"],
            "action_code": res["action_code"],
            "deficits": {
                "smap_deficit": res["components"]["sm_stress"],
                "gpm_deficit": res["components"]["rain_stress"],
                "et_anomaly": res["components"]["et_stress"],
                "lst_anomaly": res["components"]["lst_stress"]
            },
            "contributions": {
                "smap": res["contributions"]["smap_moisture"],
                "gpm": res["contributions"]["rainfall_deficit"],
                "et": res["contributions"]["evapotranspiration"],
                "lst": res["contributions"]["thermal_heat"]
            }
        }


class SevenDayMoistureForecaster(MoistureForecaster):
    """
    Subclasses MoistureForecaster to train RandomForestRegressor on historical lags
    and project 7-day rootzone soil moisture with 90% confidence uncertainty bounds.
    """
    def __init__(self, n_estimators=100, random_state=42):
        super().__init__(n_estimators=n_estimators, random_state=random_state)


class SoilQualityAnomalyDetector(SoilQualityChecker):
    """
    Subclasses SoilQualityChecker to provide evaluate_soil_anomaly method.
    """
    def evaluate_soil_anomaly(self, smap_rootzone_sm, water_stress_score, landsat_ndvi, landsat_savi=None):
        res = self.evaluate_dual_diagnosis(smap_rootzone_sm, landsat_ndvi, landsat_savi)
        status_code = "HIDDEN_SOIL_QUALITY_ALERT" if res["anomaly_detected"] else (
            "WATER_DEFICIT" if res["anomaly_type"] in ["WATER_DEFICIT", "WATER_DEFICIT_DROUGHT"] else res["anomaly_type"]
        )
        return {
            "alert_triggered": res["anomaly_detected"],
            "status_code": status_code,
            "severity": res["severity"],
            "title": res["title"],
            "diagnosis": res["summary"],
            "probable_issues": [c["cause"] if isinstance(c, dict) else str(c) for c in res["probable_causes"]],
            "action_required": res["recommended_action"]
        }


class CropBudgetSimulator:
    """
    Simulates water demand, groundwater conservation, and tube-well electricity
    for crop diversification alternatives across Punjab agricultural districts.
    """
    CROP_PROFILES = {
        "Traditional Paddy (Baseline)": {
            "water_litres_per_acre": 900000,
            "pct_saving": 0.0,
            "duration_days": 120,
            "color": "#DC2626",
            "pau_recommendation": "Standard flooded paddy - high groundwater extraction."
        },
        "Direct Seeded Rice / DSR (~20% less water)": {
            "water_litres_per_acre": 720000,
            "pct_saving": 0.20,
            "duration_days": 110,
            "color": "#0284C7",
            "pau_recommendation": "Direct seeding eliminates nursery puddling, saving 180,000 L/acre."
        },
        "Maize / Kharif Pulses (~60% less water)": {
            "water_litres_per_acre": 360000,
            "pct_saving": 0.60,
            "duration_days": 95,
            "color": "#16A34A",
            "pau_recommendation": "Drastic water reduction; protects deep aquifers from secular decline."
        },
        "Moong + Mulching (~45% less water)": {
            "water_litres_per_acre": 495000,
            "pct_saving": 0.45,
            "duration_days": 65,
            "color": "#F59E0B",
            "pau_recommendation": "Short duration pulse fixes atmospheric nitrogen and conserves 405,000 L/acre."
        }
    }

    @classmethod
    def calculate_budget(cls, crop_choice, farm_acres=10):
        prof = cls.CROP_PROFILES.get(crop_choice, cls.CROP_PROFILES["Traditional Paddy (Baseline)"])
        base_prof = cls.CROP_PROFILES["Traditional Paddy (Baseline)"]

        baseline_litres = farm_acres * base_prof["water_litres_per_acre"]
        crop_water_litres = farm_acres * prof["water_litres_per_acre"]
        groundwater_saved = max(0, baseline_litres - crop_water_litres)
        kwh_saved = int(groundwater_saved * 0.000789)

        return {
            "crop_name": crop_choice,
            "farm_acres": farm_acres,
            "baseline_litres_m": round(baseline_litres / 1e6, 2),
            "crop_water_demand_m": round(crop_water_litres / 1e6, 2),
            "groundwater_saved_m": round(groundwater_saved / 1e6, 2),
            "pct_saved": prof["pct_saving"] * 100.0,
            "kwh_saved": kwh_saved,
            "duration_days": prof["duration_days"],
            "recommendation": prof["pau_recommendation"]
        }
