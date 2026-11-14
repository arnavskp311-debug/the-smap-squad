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

## 🌟 6. Flagship Dark NASA Mission-Control UI & Five High-Impact Features

Punjab Farm Water Watch features a **flagship dark NASA mission-control interface** (deep teal `#081822` / `#0A1C28` background, glowing green `NASA Earthdata Live` status pill, crisp white forecast and alert cards, warm amber `#F59E0B` highlights, and high-contrast typography):

### 1. 🛰️ Live NASA GIBS Satellite Tile Overlays & Interactive Folium Map
* Integrated NASA Global Imagery Browse Services (GIBS) Web Map Tile Service (WMTS) layers (`MODIS Terra True Color` and `MODIS Terra Land Surface Temperature Day`).
* Features a prominent **Bathinda pin** and dynamic district choropleths colored by `WaterStressModel` scores (`Safe 0–30` Green, `Moderate 31–60` Yellow, `Critical 61–100` Red) with an embedded **Map Legend**.
* Coupled with stacked **Water Stress Score** gauge arc (showing `76/100 Critical`) and **Soil Quality Status** dual-diagnosis card.

### 2. ⚡ "What-If" Water & Tube-Well Energy Savings Simulator (Left Sidebar)
* Parametric slider for **Farm Size (1–100 Acres)** and **Conservation Practice** selector (`DSR / Mulching`, `Delay Irrigation by 3 Days`, `Crop-Residue Mulching`, or `Combined Protocol`).
* Dynamic KPI display featuring **1.8M Litres Saved** (in vibrant neon mint `#2DD4BF`) and **kWh Saved: 1,420 kWh** at 10 acres, with subsoil and electricity consumption formulas.

### 3. 📈 Crisp White "Soil Moisture & Water Forecast" Card & 30-Day Early-Warning Deltas
* Dedicated high-contrast white card showcasing past 30 days of **NASA SMAP L4 soil moisture** alongside a **7-day Random Forest forecast** with a light-blue shaded forecast window.
* **"30 Days Ago vs. Today" Early-Warning Delta Cards:** High-contrast 3-metric comparison row tracking the trajectory of **SMAP Root-Zone Soil Moisture**, **Landsat Canopy NDVI**, and **Water Stress Score**, empirically demonstrating early detection of subterranean moisture deficits.

### 4. 🗓️ Pin-Drop "7-Day Smart Farm Action Calendar"
* Dynamically translates the 7-day RandomForest moisture projections and dual-diagnosis soil alerts into a structured **Day 1 – Day 7 action schedule**.
* Guides farmers through irrigation holds, 15 cm V-cut soil sampling, straw mulching, gypsum application, and tube-well meter auditing in **English, Hindi, and Punjabi**.

### 5. 🌾 Crop-Switch & Aquifer-Life Budget Simulator
* Interactive water budget and diversification calculator modeling:
  - `Traditional Paddy (Baseline)` (900,000 L/acre)
  - `Direct Seeded Rice / DSR` (~20% water saved)
  - `Maize / Kharif Pulses` (~60% water saved)
  - `Moong + Mulching` (~45% water saved)
* Computes real-time **Seasonal Water Demand (Million Litres)**, **Groundwater Saved**, and **Estimated Tube-Well Power Saved (kWh)** with side-by-side Plotly bar visualizations.

### 6. 🧪 Interactive Soil Health Card & Instant Lab Prescription
* Empirical soil testing calculator with inputs for **pH (8.6)**, **EC (0.9 dS/m)**, **Organic Carbon (0.38%)**, and **Nitrogen (kg/ha)**.
* Generates an instant prescription box with **Agricultural Gypsum bags/acre**, **Compost tonnes/acre**, and **Zinc Sulfate dosage**, paired with an expandable PAU 4-step sampling protocol.

### 7. 📢 Farmer Advisory & Alert Card with WhatsApp & Web Speech Voice Alerts
* High-impact alert card with localized advice (*"Kisan bhai, 3 din paani rok do"*, *"Switch to Direct Seeded Rice (DSR) & Mulching"* in English, Hindi, and Punjabi).
* Includes a one-click **"Share on WhatsApp"** (`wa.me`) community broadcast button and a **"Listen Voice Alert"** button powered by browser-native Web Speech API (`window.speechSynthesis`).
* **Download District Officer Report:** One-click download button exporting an official Markdown dossier and 30-day NASA telemetry CSV.

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
