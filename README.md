# Punjab Farm Water Watch 🛰️🌾
**NASA Space Apps Challenge 2026 · Delhi NCR**  
**Team:** The SMAP Squad  
**Project:** Punjab Farm Water Watch — Water Scarcity & Soil-Quality Early Warning System powered by NASA Earth Observations

---

## 🌍 1. The Challenge & Context

Punjab is ground zero for a critical groundwater depletion crisis in South Asia:
* **0.5 m/year Groundwater Decline:** Over 20+ years of satellite observations, NASA GRACE / GRACE-FO have tracked ~3,122 km³ of human-driven freshwater loss across global agricultural hotspots.
* **Global Food Security Linchpin:** Punjab produces **47% of India's central wheat procurement pool** and drives **~26% of global Basmati rice exports**. A failure in Punjab's water and soil systems directly impacts international food security.
* **The Hidden Soil Quality Barrier:** Even when seeds and irrigation are available, unpredictable soil degradation—secondary salinization from alkaline tubewells, puddling-induced subsurface hardpans, and low organic carbon (<0.40%)—severely suppresses crop yields across Punjab districts.

**Punjab Farm Water Watch** is an operational diagnostic and early-warning platform that combines six open NASA Earth Observation datasets to simultaneously diagnose hydrological water scarcity, flag hidden soil degradation, forecast 7-day soil moisture drydown, and deliver trilingual agronomic advisories.

---

## 🛰️ 2. The 6 NASA Earth Observation Datasets

| Dataset | Short Name | Spatial / Temporal Resolution | System Role | Source DAAC |
|---|---|---|---|---|
| **NASA SMAP L4** | `SPL4SMGP` | 9 km / 3-hourly | Primary rootzone (0–100 cm) and surface (0–5 cm) volumetric soil moisture | NSIDC DAAC |
| **NASA GPM IMERG** | `GPM_3IMERGDF` | 0.1° / Daily | Precipitation tracking and 30-day cumulative rainfall deficits | GES DISC DAAC |
| **MODIS MOD16A2** | `MOD16A2` | 500 m / 8-day | Evapotranspiration (ET) measuring crop atmospheric water loss | LP DAAC |
| **Landsat 8/9 OLI/TIRS** | `HLSL30` | 30 m / 16-day | Vegetation vigor (NDVI, SAVI, NDWI) and Land Surface Temperature (LST) | LP DAAC |
| **NASA POWER DAV** | API | Daily | Agroclimatology (ambient temperature, solar radiation, humidity, wind speed) | NASA Langley |
| **NASA GRACE / GRACE-FO** | Mass Anomaly | Regional / Monthly | 20-year groundwater equivalent thickness anomaly & secular trend baseline | JPL / PO.DAAC |

---

## 🧮 3. Water Stress Scoring Engine (0–100)

The system computes a weighted, multi-satellite scarcity index designed for Punjab's alluvial agro-hydrological conditions:

$$\text{Water Stress Score} = 0.40 \times \text{SMAP Deficit} + 0.30 \times \text{GPM Deficit} + 0.20 \times \text{MODIS ET} + 0.10 \times \text{Landsat LST}$$

### Component Formulations:
1. **SMAP Soil Moisture Deficit ($40\%$):**
   $$\text{SMAP Deficit} = \text{clip}\left(\frac{0.36 - \text{SM}}{0.36 - 0.10} \times 100, 0, 100\right)$$
   *(0.36 = Field Capacity, 0.10 = Permanent Wilting Point)*
2. **GPM Rainfall Deficit ($30\%$):**
   $$\text{GPM Deficit} = \left(1.0 - \min\left(\frac{\text{Rain}_{30\text{d}}}{50.0}, 1.0\right)\right) \times 100$$
3. **MODIS ET Anomaly ($20\%$):**
   Atmospheric moisture draw scaled from 2.0 mm/day (low) to 7.0 mm/day (extreme draw).
4. **Landsat LST Heat Anomaly ($10\%$):**
   Canopy thermal stress scaled from 25°C (optimal) to 42°C (severe thermal stress).

### Risk Classification:
* 🟢 **0–30: Green (No Stress)** — Water reserves sufficient; cross-examine NDVI for soil health.
* 🟡 **31–60: Yellow (Moderate Stress)** — Irrigation caution; monitor tubewell hours and prepare mulching.
* 🔴 **61–100: Red (High Scarcity)** — Critical deficit; switch to Direct Seeded Rice (DSR) and delay flood irrigation.

---

## 🧪 4. Dual-Diagnosis Soil-Quality Diagnostic Innovation

A unique innovation of Punjab Farm Water Watch is resolving **unexplained crop failure** when water is available:

```text
┌───────────────────────────────────────┐
│     Dual-Diagnosis Logic Gate         │
├───────────────────────────────────────┤
│ IF SMAP Water Stress is 0–30 (GREEN)  │
│   AND Landsat NDVI < 0.42 / SAVI < 0.35│
│ THEN:                                 │
│   🚨 TRIGGER SOIL QUALITY ALERT       │
└───────────────────────────────────────┘
```

When satellite radar confirms adequate soil moisture yet optical reflectance reveals weak canopy vigor, the limiting factor is **not water**, but chemical or physical soil degradation:
* **Secondary Soil Alkalinity / Sodicity:** pH > 8.5, ESP > 15% from alkaline tubewell irrigation.
* **Secondary Salinization:** EC > 4.0 dS/m from capillary salt rise in canal commands.
* **Organic Carbon Depletion & Hardpan:** Puddling-induced dense layer at 15–20 cm depth impeding root respiration.

### How to Test Soil (PAU / KVK Protocol):
1. **Zigzag Selection:** Pick 5–6 spots across the field away from trees and bunds.
2. **15 cm V-Cut:** Dig a 15 cm V-shaped pit (active plow layer) and take a uniform 2 cm slice.
3. **Quartering Method:** Mix in a plastic bucket, divide into 4 quarters, and retain ~500 grams.
4. **Lab Testing:** Submit to local Krishi Vigyan Kendra (KVK) or Punjab Agricultural University (PAU) lab for **pH, EC, Organic Carbon, N-P-K, and micronutrients (Zinc/Iron)**.
5. **Targeted Remedies:** Apply **Gypsum** for sodic soil, **Dhaincha (Sesbania) green manuring** for organic carbon, and **0.5% $ZnSO_4$ foliar spray**. Maintain **Zero Stubble Burning**.

---

## 🔮 5. 7-Day Machine Learning Predictive Forecast

* Uses a `scikit-learn` `RandomForestRegressor` trained on historical 7-day lags of SMAP soil moisture, GPM rainfall, and NASA POWER daily temperature.
* Generates an iterative 7-day projection with **90% confidence uncertainty interval bands** based on ensemble tree spread.

---

## 🌟 6. Five High-Impact Features for NASA Space Apps Judging

To deliver maximum operational utility for both smallholder farmers and district agricultural policymakers, Punjab Farm Water Watch incorporates 5 flagship interactive capabilities:

### 1. 🛰️ Live NASA GIBS Satellite Tile Overlays on Interactive Folium Map
* Integrated NASA Global Imagery Browse Services (GIBS) Web Map Tile Service (WMTS) layers.
* Toggle between **MODIS Terra True Color (Corrected Reflectance)** and **MODIS Terra Land Surface Temperature (Day)** directly over Punjab district polygons with a live `folium.LayerControl()`.
* Enables visual corroboration between numeric water stress scores and true satellite-observed canopy greenness and surface heat patterns.

### 2. ⚡ "What-If" Water & Tube-Well Energy Savings Simulator
* Dynamic parametric calculator with an interactive **Farm Size (1–100 Acres)** slider.
* Models 4 field-proven conservation interventions:
  - **Direct Seeded Rice (DSR):** ~20% water reduction.
  - **3-Day Delayed Irrigation:** ~10% water reduction based on SMAP rootzone adequacy.
  - **Crop-Residue Mulching:** ~15% evaporation suppression.
  - **Combined Protocol:** ~30% cumulative water and energy savings.
* Calculates exact season-level metrics: **Litres of Groundwater Saved**, **Tube-Well Electricity Saved (kWh)**, and regional scaling across Punjab's 100,000+ agricultural tube wells (Gigalitres saved, GWh saved, and metric tonnes of $CO_2$ avoided).

### 3. 🧪 Interactive Soil Health Card & Instant Lab Prescription
* Empirical soil testing calculator accepting standard soil lab report values:
  - **Soil pH** (sodicity index)
  - **Electrical Conductivity (EC)** in dS/m (salinity index)
  - **Organic Carbon (OC)** in % (microbial and structural fertility)
  - **Available Nitrogen** in kg/ha
* Generates real-time, precision-dosed prescriptions aligned with PAU and KVK agronomic agronomy:
  - Exact agricultural **Gypsum bags/acre** based on excess alkalinity ($pH > 8.5$).
  - Recommended **Farmyard Manure (FYM)** and **Dhaincha (Sesbania) green manuring** tonnage when $OC < 0.5\%$.
  - Leaching canal-water flood schedule for salt flushes when $EC > 0.8\text{ dS/m}$.
  - Calibrated basal dose of Zinc Sulfate Heptahydrate ($ZnSO_4$, 21%) to eliminate widespread zinc deficiencies in Indo-Gangetic soils.

### 4. 📢 One-Click WhatsApp Alert & Web Speech Audio Advisory (Trilingual)
* **WhatsApp Community Broadcast:** A direct `wa.me/?text=...` deep link that formats a complete, URL-encoded alert with the district name, Water Stress Score, 7-day forecast, and localized advisories for instant dissemination in farmer WhatsApp groups.
* **Browser-Native Web Speech API Narration:** Integrates accessible audio synthesis (`window.speechSynthesis`) in **English**, **Hindi (हिन्दी)**, and **Punjabi (ਪੰਜਾਬੀ)**, allowing illiterate or visually impaired growers to hear real-time irrigation guidance (*"Kisan bhai, 3 din paani rok do"* / *"ਕਿਸਾਨ ਵੀਰੋ, 3 ਦਿਨ ਪਾਣੀ ਰੋਕੋ"*).

### 5. 📄 One-Click Downloadable District Officer Action Brief (Markdown & CSV)
* Generates a timestamped, official **District Water & Soil Action Brief** ready for Chief Agriculture Officers (CAOs) and Krishi Vigyan Kendra extension specialists.
* Includes exact district coordinates, complete 6-satellite NASA telemetry, Water Stress attribution weights, dual-diagnosis soil audit, 7-day predictive projection table with confidence intervals, and field intervention instructions.
* Dual-export capability: Formatted executive **Markdown dossier** and raw **30-day NASA telemetry CSV**.

---

## 🚀 7. Installation & Execution Guide

### Prerequisites
* Python 3.11+
* `uv` or `pip` package manager

### Setup
```bash
# Clone the repository
cd "c:\Users\DAV-3\Desktop\Project\The SMAP Squad\Smap code"

# Create and activate virtual environment
uv venv .venv
.venv\Scripts\activate

# Install all dependencies
uv pip install -r requirements.txt
```

### Run Data Ingestion Pipeline
```bash
python fetch_nasa_data.py
```
* Queries NASA CMR for SMAP L4, GPM IMERG, MODIS, Landsat, POWER, and GRACE.
* Clips gridded rasters using `xarray` and `rasterio` to Punjab district boundaries (`Bathinda`, `Ludhiana`, `Patiala`, `Amritsar`, `Sangrur`).
* Outputs processed time-series to `data/processed/` and audit logs to `data/logs/`.

### Run Interactive Dashboard
```bash
streamlit run app.py
```
*Or double-click `run_app.bat` on Windows.*

---

## 👥 8. Team & Credits
* **Challenge:** NASA Space Apps Challenge 2026 (Delhi NCR)
* **Team:** The SMAP Squad
* **Data Sources:** NASA Earth Science Data Systems (ESDS), NASA Earthdata, LP DAAC, NSIDC DAAC, GES DISC, NASA Langley POWER, JPL PO.DAAC.
