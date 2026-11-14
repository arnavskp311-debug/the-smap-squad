"""
Water Stress Scoring Engine for Punjab Farm Water Watch.
Combines NASA SMAP L4, GPM IMERG, MODIS MOD16A2, and Landsat LST into a weighted 0-100 Scarcity Index.
Classifies into Green (0-30), Yellow (31-60), and Red (61-100) risk zones.
"""

import numpy as np


class WaterStressEngine:
    def __init__(self):
        # Weights according to agro-hydrological impact in Punjab
        self.w_sm = 0.40     # SMAP rootzone moisture deficit
        self.w_rain = 0.25   # GPM 30-day precipitation deficit
        self.w_et = 0.20     # MODIS evapotranspiration demand
        self.w_lst = 0.15    # Landsat Land Surface Temperature anomaly

        # Critical physical thresholds for Punjab alluvial soils
        self.field_capacity_sm = 0.36   # m^3/m^3
        self.wilting_point_sm = 0.10    # m^3/m^3
        self.normal_30d_rain_mm = 50.0  # mm baseline expectation
        self.normal_et_mm_day = 4.0     # mm/day
        self.normal_lst_c = 30.0        # Celsius

    def calculate_score(self, smap_rootzone_sm, rain_30d_mm, modis_et_daily, landsat_lst_c):
        """
        Calculates individual component stress (0-100) and weighted final score.
        Returns:
            dict containing total_score, zone (Green/Yellow/Red), and feature contributions.
        """
        # 1. Soil Moisture Stress (0 = full field capacity, 100 = at or below wilting point)
        if smap_rootzone_sm >= self.field_capacity_sm:
            sm_stress = 0.0
        elif smap_rootzone_sm <= self.wilting_point_sm:
            sm_stress = 100.0
        else:
            sm_stress = (self.field_capacity_sm - smap_rootzone_sm) / (self.field_capacity_sm - self.wilting_point_sm) * 100.0

        # 2. 30-day Rainfall Deficit Stress (0 = adequate rain >= 50mm, 100 = zero rain)
        rain_ratio = min(rain_30d_mm / self.normal_30d_rain_mm, 1.0)
        rain_stress = (1.0 - rain_ratio) * 100.0

        # 3. Evapotranspiration Demand Stress (higher ET = faster crop drying)
        # Scaled from 2.0 mm/day (0 stress) to 7.0 mm/day (100 stress)
        et_stress = np.clip((modis_et_daily - 2.0) / (7.0 - 2.0) * 100.0, 0.0, 100.0)

        # 4. Thermal Stress from Land Surface Temp (Landsat LST)
        # 25C = 0 stress, 42C = 100 stress
        lst_stress = np.clip((landsat_lst_c - 25.0) / (42.0 - 25.0) * 100.0, 0.0, 100.0)

        # Weighted combination
        total_score = (
            self.w_sm * sm_stress +
            self.w_rain * rain_stress +
            self.w_et * et_stress +
            self.w_lst * lst_stress
        )
        total_score = round(float(np.clip(total_score, 0.0, 100.0)), 1)

        # Determine Risk Zone
        if total_score <= 30.0:
            zone = "Green"
            status_text = "Low / No Water Stress"
            action_code = "SAFE"
        elif total_score <= 60.0:
            zone = "Yellow"
            status_text = "Moderate Stress (Monitor & Conserve)"
            action_code = "CAUTION"
        else:
            zone = "Red"
            status_text = "High Scarcity (Critical Deficit)"
            action_code = "CRITICAL"

        # Calculate percentage contribution for SHAP-style transparency
        weighted_parts = {
            "smap_moisture": self.w_sm * sm_stress,
            "rainfall_deficit": self.w_rain * rain_stress,
            "evapotranspiration": self.w_et * et_stress,
            "thermal_heat": self.w_lst * lst_stress,
        }
        sum_weighted = sum(weighted_parts.values()) or 1.0
        contributions = {k: round((v / sum_weighted) * 100, 1) for k, v in weighted_parts.items()}

        return {
            "score": total_score,
            "zone": zone,
            "status": status_text,
            "action_code": action_code,
            "components": {
                "sm_stress": round(sm_stress, 1),
                "rain_stress": round(rain_stress, 1),
                "et_stress": round(et_stress, 1),
                "lst_stress": round(lst_stress, 1)
            },
            "contributions": contributions
        }
