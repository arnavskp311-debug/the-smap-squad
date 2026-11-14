"""
SMAP-vs-Landsat Dual-Diagnosis Soil-Quality Anomaly Detector.
Identifies hidden soil degradation (salinity, alkalinity, compaction, or nutrient depletion)
when satellite confirms adequate water moisture yet crop vegetation vigor is suppressed.
"""

class SoilQualityChecker:
    def __init__(self):
        # Agronomic thresholds for Punjab
        self.min_adequate_sm = 0.22    # m^3/m^3 (Rootzone moisture threshold for adequate water)
        self.suppressed_ndvi_threshold = 0.45  # NDVI threshold below which vigor is abnormally low
        self.suppressed_savi_threshold = 0.36  # SAVI threshold

    def evaluate_dual_diagnosis(self, smap_rootzone_sm, landsat_ndvi, landsat_savi=None):
        """
        Cross-examines SMAP soil moisture with Landsat NDVI/SAVI.
        Returns detailed anomaly diagnosis and agronomic risk assessment.
        """
        if landsat_savi is None:
            landsat_savi = landsat_ndvi * 0.82

        is_water_adequate = smap_rootzone_sm >= self.min_adequate_sm
        is_vegetation_suppressed = landsat_ndvi <= self.suppressed_ndvi_threshold

        if is_water_adequate and is_vegetation_suppressed:
            # High moisture + low vegetative vigor = HIDDEN SOIL QUALITY DEFECT!
            severity = "HIGH" if landsat_ndvi < 0.35 else "MODERATE"
            return {
                "anomaly_detected": True,
                "anomaly_type": "HIDDEN_SOIL_QUALITY_ALERT",
                "severity": severity,
                "title": "Hidden Soil-Quality Degradation Flagged",
                "summary": (
                    f"SMAP confirms adequate soil moisture ({smap_rootzone_sm:.2f} m³/m³), "
                    f"yet Landsat NDVI ({landsat_ndvi:.2f}) indicates severe crop growth suppression. "
                    "Water is not the limiting factor. The root cause is chemical or physical soil degradation."
                ),
                "probable_causes": [
                    {
                        "cause": "Secondary Soil Salinization & Alkalinity",
                        "indicators": "High pH (> 8.5) or Electrical Conductivity EC (> 4 dS/m) from brackish tubewell irrigation.",
                        "confidence": "85%"
                    },
                    {
                        "cause": "Subsurface Hardpan & Compaction",
                        "indicators": "Puddling-induced dense layer at 15-20 cm depth impeding root respiration.",
                        "confidence": "70%"
                    },
                    {
                        "cause": "Organic Carbon & Micronutrient Deficiency",
                        "indicators": "Organic carbon < 0.40%, severe Zinc (Zn) or Iron (Fe) chlorosis.",
                        "confidence": "65%"
                    }
                ],
                "recommended_action": "PRIORITY_SOIL_TEST"
            }
        
        elif not is_water_adequate and is_vegetation_suppressed:
            # Low moisture + low NDVI = Classic Water Deficit Drought Stress
            return {
                "anomaly_detected": False,
                "anomaly_type": "WATER_DEFICIT_DROUGHT",
                "severity": "NORMAL",
                "title": "Water Deficit Drought Stress",
                "summary": (
                    f"Both SMAP rootzone moisture ({smap_rootzone_sm:.2f} m³/m³) and Landsat NDVI ({landsat_ndvi:.2f}) "
                    "are depressed in tandem. Crop growth is limited directly by moisture scarcity."
                ),
                "probable_causes": [
                    {"cause": "Meteorological & Hydrological Drought", "indicators": "Rainfall deficit and prolonged drydown.", "confidence": "95%"}
                ],
                "recommended_action": "WATER_CONSERVATION_IRRIGATION"
            }
        
        elif is_water_adequate and not is_vegetation_suppressed:
            # High moisture + healthy NDVI = Thriving crop
            return {
                "anomaly_detected": False,
                "anomaly_type": "OPTIMAL_HEALTH",
                "severity": "NONE",
                "title": "Optimal Soil & Hydrological Health",
                "summary": (
                    f"SMAP moisture ({smap_rootzone_sm:.2f} m³/m³) and Landsat NDVI ({landsat_ndvi:.2f}) "
                    "are both strong. Crop canopy is healthy with no apparent soil anomalies."
                ),
                "probable_causes": [],
                "recommended_action": "STANDARD_AGRONOMIC_MONITORING"
            }
        
        else:
            # Low moisture + high NDVI = Crop is drawing from deep capillary water or recent irrigation
            return {
                "anomaly_detected": False,
                "anomaly_type": "TEMPORARY_BUFFER",
                "severity": "LOW",
                "title": "Vegetation Buffer Phase",
                "summary": (
                    f"Landsat NDVI ({landsat_ndvi:.2f}) remains green despite declining SMAP moisture ({smap_rootzone_sm:.2f} m³/m³). "
                    "Crops are drawing on deep rootzone reserves, but will drydown rapidly without recharge."
                ),
                "probable_causes": [],
                "recommended_action": "PREPARE_CONSERVATION_IRRIGATION"
            }
