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
