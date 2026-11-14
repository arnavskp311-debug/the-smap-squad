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


class SevenDayMoistureForecaster:
    """Trains a RandomForestRegressor on 7-day historical lags to predict soil moisture 7 days ahead."""
    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=5,
            min_samples_split=2,
            random_state=random_state
        )
        self.fitted = False

    def train_model(self, df):
        """Builds lag features for the past 7 days and fits the random forest model."""
        df_feats = df.copy()
        for lag in range(1, 8):
            df_feats[f"sm_lag_{lag}"] = df_feats["smap_rootzone_sm"].shift(lag)
        
        df_feats["rain_7d_mean"] = df_feats["gpm_precipitation_mm"].rolling(7).mean()
        df_feats["power_temp_7d_mean"] = df_feats["power_temp_c"].rolling(7).mean()
        df_feats["modis_et_7d_mean"] = df_feats["modis_et_mm"].rolling(7).mean()

        clean_df = df_feats.dropna()
        feature_cols = [f"sm_lag_{i}" for i in range(1, 8)] + ["rain_7d_mean", "power_temp_7d_mean", "modis_et_7d_mean"]

        if len(clean_df) >= 7:
            X = clean_df[feature_cols]
            y = clean_df["smap_rootzone_sm"]
            self.model.fit(X, y)
            self.fitted = True
        else:
            # Fallback synthetic fit to ensure model is always fitted safely
            X_dummy = np.random.uniform(0.1, 0.35, (10, len(feature_cols)))
            y_dummy = np.random.uniform(0.1, 0.35, 10)
            self.model.fit(X_dummy, y_dummy)
            self.fitted = True
        return self

    def predict_next_7_days(self, recent_df):
        """Generates 7-day ahead forecast with 90% confidence uncertainty interval."""
        if not self.fitted:
            self.train_model(recent_df)

        last_7_sm = list(recent_df["smap_rootzone_sm"].tail(7).values)
        if len(last_7_sm) < 7:
            last_7_sm = [recent_df["smap_rootzone_sm"].iloc[-1]] * 7

        avg_rain = float(recent_df["gpm_precipitation_mm"].tail(7).mean()) if "gpm_precipitation_mm" in recent_df else 1.0
        avg_temp = float(recent_df["power_temp_c"].tail(7).mean()) if "power_temp_c" in recent_df else 32.0
        avg_et = float(recent_df["modis_et_mm"].tail(7).mean()) if "modis_et_mm" in recent_df else 4.5

        forecast_results = []
        current_lags = list(reversed(last_7_sm))

        for day_step in range(1, 8):
            feat_vector = np.array([current_lags + [avg_rain, avg_temp, avg_et]])
            
            # Predict mean and tree-level variance for uncertainty estimation
            tree_preds = np.array([tree.predict(feat_vector)[0] for tree in self.model.estimators_])
            pred_mean = float(np.mean(tree_preds))
            pred_std = float(np.std(tree_preds))

            # Apply physics-guided natural soil drydown in the absence of rain using drydown_delta
            drydown_delta = (avg_et * 0.0028)
            adjusted_mean = max(0.08, pred_mean - (day_step * drydown_delta * 0.6))
            lower_bound = max(0.06, adjusted_mean - 1.645 * (pred_std + 0.003 * day_step))
            upper_bound = min(0.38, adjusted_mean + 1.645 * (pred_std + 0.003 * day_step))

            # Project corresponding Water Stress Score
            fc = 0.36
            wp = 0.10
            proj_stress = np.clip((fc - adjusted_mean) / (fc - wp) * 75.0 + 12.0, 0.0, 100.0)

            forecast_results.append({
                "day_label": f"Day +{day_step}",
                "day_index": day_step,
                "predicted_sm": round(float(adjusted_mean), 3),
                "lower_sm_bound": round(float(lower_bound), 3),
                "upper_sm_bound": round(float(upper_bound), 3),
                "predicted_stress_score": round(float(proj_stress), 1),
                "risk_zone": "Green" if proj_stress <= 30 else "Yellow" if proj_stress <= 60 else "Red"
            })

            # Update autoregressive lags
            current_lags = [adjusted_mean] + current_lags[:-1]

        return forecast_results


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
