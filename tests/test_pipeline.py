import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.earthaccess_client import NASADataPipeline
from src.pipeline.spatial_processor import SpatialProcessor
from src.models.water_stress_engine import WaterStressEngine
from src.models.forecast_model import MoistureForecaster
from src.models.soil_quality_checker import SoilQualityChecker

def test_system():
    print("1. Testing NASADataPipeline...")
    pipe = NASADataPipeline()
    df = pipe.get_district_timeseries("Bathinda", 30)
    assert not df.empty, "DataFrame should not be empty"
    print(f"   Success! TimeSeries rows: {len(df)}")

    print("2. Testing SpatialProcessor...")
    sp = SpatialProcessor()
    loc = sp.locate_point(30.2110, 74.9455)
    assert loc["district"] == "Bathinda", "Point should resolve to Bathinda"
    print(f"   Success! Resolved district: {loc['district']}")

    print("3. Testing WaterStressEngine...")
    wse = WaterStressEngine()
    res = wse.calculate_score(0.18, 12.0, 5.2, 36.5)
    assert 0 <= res["score"] <= 100, "Score should be between 0 and 100"
    print(f"   Success! Stress score: {res['score']}, Zone: {res['zone']}")

    print("4. Testing MoistureForecaster (RandomForest)...")
    fc = MoistureForecaster()
    preds = fc.predict_next_7_days(df)
    assert len(preds) == 7, "Should produce exactly 7 days forecast"
    print(f"   Success! 7-day forecast generated, Day +1: {preds[0]['predicted_sm']} m3/m3")

    print("5. Testing SoilQualityChecker (SMAP vs NDVI Anomaly)...")
    sq = SoilQualityChecker()
    diag = sq.evaluate_dual_diagnosis(smap_rootzone_sm=0.29, landsat_ndvi=0.31)
    assert diag["anomaly_detected"] is True, "Should detect hidden soil anomaly when moisture is high and NDVI is low"
    print(f"   Success! Anomaly flagged: {diag['anomaly_type']}")

    print("\n✅ ALL MODULE INTEGRATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_system()
