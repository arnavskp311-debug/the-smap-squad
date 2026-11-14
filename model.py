"""
Punjab Farm Water Watch - Machine Learning & Diagnostic Scoring Engine
Team: The SMAP Squad · NASA Space Apps Challenge 2026 (Delhi NCR)

Contains:
1. 0-100 Water Stress Score (Weighted Multi-Satellite Index)
   Score = 0.40 * SMAP_Deficit + 0.30 * GPM_Rain_Deficit + 0.20 * MODIS_ET_Anomaly + 0.10 * Landsat_LST_Anomaly
   Classification: 0-30 Green (No Stress), 31-60 Yellow (Moderate Stress), 61-100 Red (High Scarcity)
2. 7-Day Soil Moisture Forecaster (scikit-learn RandomForestRegressor)
3. SMAP-vs-Landsat NDVI/SAVI Soil-Quality Anomaly Detector (Hidden Salinity/Alkalinity Alert)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


class WaterStressModel:
    """Computes the 0-100 Water Stress Score using 4 NASA satellite inputs."""
    def __init__(self):
        # Exact weights requested
        self.w_smap = 0.40
        self.w_gpm = 0.30
        self.w_et = 0.20
        self.w_lst = 0.10

        # Physical agronomic thresholds for Punjab alluvial soils
        self.field_capacity_sm = 0.36   # m^3/m^3 (Optimum rootzone water)
        self.wilting_point_sm = 0.10    # m^3/m^3 (Permanent wilting point)
        self.baseline_30d_rain_mm = 50.0  # Normal 30-day rain expectation
        self.et_min = 2.0               # mm/day (Low atmospheric draw)
        self.et_max = 7.0               # mm/day (Extreme crop transpiration demand)
        self.lst_min = 25.0             # Celsius (Optimal canopy temperature)
        self.lst_max = 42.0             # Celsius (Extreme heat stress)

    def compute_water_stress_score(self, smap_rootzone_sm, rain_30d_mm, modis_et_mm, landsat_lst_c):
        """
        Calculates individual deficits (0-100) and weighted final Water Stress Score.
        """
        # 1. SMAP Soil Moisture Deficit
        if smap_rootzone_sm >= self.field_capacity_sm:
            smap_deficit = 0.0
        elif smap_rootzone_sm <= self.wilting_point_sm:
            smap_deficit = 100.0
        else:
            smap_deficit = (self.field_capacity_sm - smap_rootzone_sm) / (self.field_capacity_sm - self.wilting_point_sm) * 100.0

        # 2. GPM Rainfall Deficit
        rain_ratio = min(rain_30d_mm / self.baseline_30d_rain_mm, 1.0)
        gpm_deficit = (1.0 - rain_ratio) * 100.0

        # 3. MODIS ET Anomaly
        et_anomaly = np.clip((modis_et_mm - self.et_min) / (self.et_max - self.et_min) * 100.0, 0.0, 100.0)

        # 4. Landsat LST Anomaly
        lst_anomaly = np.clip((landsat_lst_c - self.lst_min) / (self.lst_max - self.lst_min) * 100.0, 0.0, 100.0)

        # Weighted combination: 0.40 * SMAP + 0.30 * GPM + 0.20 * ET + 0.10 * LST
        total_score = (
            self.w_smap * smap_deficit +
            self.w_gpm * gpm_deficit +
            self.w_et * et_anomaly +
            self.w_lst * lst_anomaly
        )
        total_score = round(float(np.clip(total_score, 0.0, 100.0)), 1)

        # Classification into exact requested zones
        if total_score <= 30.0:
            zone = "Green"
            status = "No Stress (Safe)"
            badge_color = "#28a745"
            action_code = "SAFE"
        elif total_score <= 60.0:
            zone = "Yellow"
            status = "Moderate Stress"
            badge_color = "#ffc107"
            action_code = "CAUTION"
        else:
            zone = "Red"
            status = "High Scarcity"
            badge_color = "#dc3545"
            action_code = "CRITICAL"

        return {
            "score": total_score,
            "zone": zone,
            "status": status,
            "badge_color": badge_color,
            "action_code": action_code,
            "deficits": {
                "smap_deficit": round(float(smap_deficit), 1),
                "gpm_deficit": round(float(gpm_deficit), 1),
                "et_anomaly": round(float(et_anomaly), 1),
                "lst_anomaly": round(float(lst_anomaly), 1)
            },
            "contributions": {
                "smap": round((self.w_smap * smap_deficit / max(total_score, 1e-3)) * 100, 1),
                "gpm": round((self.w_gpm * gpm_deficit / max(total_score, 1e-3)) * 100, 1),
                "et": round((self.w_et * et_anomaly / max(total_score, 1e-3)) * 100, 1),
                "lst": round((self.w_lst * lst_anomaly / max(total_score, 1e-3)) * 100, 1)
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
        return self

    def predict_next_7_days(self, recent_df):
        """Generates 7-day ahead forecast with 90% confidence uncertainty interval."""
        if not self.fitted:
            self.train_model(recent_df)

        last_7_sm = list(recent_df["smap_rootzone_sm"].tail(7).values)
        if len(last_7_sm) < 7:
            last_7_sm = [recent_df["smap_rootzone_sm"].iloc[-1]] * 7

        avg_rain = float(recent_df["gpm_precipitation_mm"].tail(7).mean())
        avg_temp = float(recent_df["power_temp_c"].tail(7).mean())
        avg_et = float(recent_df["modis_et_mm"].tail(7).mean())

        forecast_results = []
        current_lags = list(reversed(last_7_sm))  # lag1, lag2, ... lag7

        for day_step in range(1, 8):
            feat_vector = np.array([current_lags + [avg_rain, avg_temp, avg_et]])
            
            # Predict mean and tree-level variance for uncertainty estimation
            tree_preds = np.array([tree.predict(feat_vector)[0] for tree in self.model.estimators_])
            pred_mean = float(np.mean(tree_preds))
            pred_std = float(np.std(tree_preds))

            # Apply physics-guided natural soil drydown in the absence of rain
            drydown_slope = avg_et * 0.0028
            adjusted_mean = max(0.08, pred_mean - (day_step * drydown_slope * 0.6))
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


class SoilQualityAnomalyDetector:
    """
    Detects hidden soil degradation (salinity, alkalinity, low organic carbon)
    whenever SMAP indicates adequate water (Green zone) yet Landsat NDVI/SAVI indicates weak crop vigor.
    """
    def __init__(self):
        self.adequate_water_sm_threshold = 0.22  # m^3/m^3
        self.weak_ndvi_threshold = 0.42          # Below 0.42 indicates depressed vegetative vigor
        self.weak_savi_threshold = 0.35          # SAVI threshold

    def evaluate_soil_anomaly(self, smap_rootzone_sm, water_stress_score, landsat_ndvi, landsat_savi=None):
        """
        Cross-checks SMAP moisture against Landsat vegetation indices.
        """
        if landsat_savi is None:
            landsat_savi = landsat_ndvi * 0.82

        is_water_green = (water_stress_score <= 30.0) or (smap_rootzone_sm >= self.adequate_water_sm_threshold)
        is_plant_growth_weak = (landsat_ndvi <= self.weak_ndvi_threshold) or (landsat_savi <= self.weak_savi_threshold)

        if is_water_green and is_plant_growth_weak:
            return {
                "alert_triggered": True,
                "status_code": "SOIL_QUALITY_ALERT",
                "severity": "HIGH" if landsat_ndvi < 0.35 else "MODERATE",
                "title": "Hidden Soil-Quality Degradation Alert",
                "diagnosis": (
                    f"SMAP confirms adequate soil water ({smap_rootzone_sm:.2f} m³/m³, Stress Score: {water_stress_score:.1f} Green), "
                    f"yet Landsat NDVI ({landsat_ndvi:.2f}) indicates abnormally weak crop vigor. "
                    "Water is NOT the limiting factor. The crop is suffering from chemical or physical soil degradation."
                ),
                "probable_issues": [
                    "Secondary Soil Salinity / Sodic Crust (EC > 4.0 dS/m, pH > 8.5) from alkaline tubewell irrigation.",
                    "Severe Organic Carbon Depletion (< 0.40%) & Micronutrient Starvation (Zinc/Iron deficiency).",
                    "Puddling-induced dense subsurface hardpan at 15-20 cm depth impeding root aeration."
                ],
                "action_required": "PRIORITY_SOIL_TEST"
            }
        elif not is_water_green and is_plant_growth_weak:
            return {
                "alert_triggered": False,
                "status_code": "WATER_DEFICIT",
                "severity": "NORMAL",
                "title": "Water Deficit Induced Stress",
                "diagnosis": "Both soil moisture and vegetation vigor are low; crop stress is directly caused by water scarcity.",
                "probable_issues": ["Prolonged drydown / Delayed irrigation"],
                "action_required": "IRRIGATION_MANAGEMENT"
            }
        else:
            return {
                "alert_triggered": False,
                "status_code": "OPTIMAL_HEALTH",
                "severity": "NONE",
                "title": "Optimal Soil & Water Balance",
                "diagnosis": "SMAP moisture and Landsat NDVI/SAVI are both strong; healthy crop canopy with no soil quality anomalies.",
                "probable_issues": [],
                "action_required": "ROUTINE_MONITORING"
            }
