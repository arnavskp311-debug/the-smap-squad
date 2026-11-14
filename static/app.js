// Punjab Farm Water Watch - Client Application
let currentDistrict = "Bathinda";
let currentLang = "en";
let map = null;
let geojsonLayer = null;
let marker = null;
let forecastChart = null;

// Initialize when DOM loads
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initMap();
    setupEventListeners();
    loadDistrictData(currentDistrict);
});

// Tab navigation
function initTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            tabButtons.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const target = btn.getAttribute("data-tab");
            const content = document.getElementById(target);
            if (content) {
                content.classList.add("active");
                if (target === "tab-overview" && map) {
                    setTimeout(() => map.invalidateSize(), 150);
                }
            }
        });
    });
}

// Leaflet Map setup
function initMap() {
    map = L.map("map", {
        center: [30.2110, 74.9455],
        zoom: 7,
        minZoom: 5,
        maxZoom: 14
    });

    // Base Layers
    const darkMatter = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; CartoDB & OpenStreetMap',
        maxZoom: 19
    }).addTo(map);

    const esriSatellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
        attribution: 'Tiles &copy; Esri'
    });

    // Layer control
    L.control.layers({
        "🗺️ Dark Matter": darkMatter,
        "🌍 High-Res Satellite (Esri)": esriSatellite
    }, null, { position: "topright" }).addTo(map);

    // Initial marker
    marker = L.marker([30.2110, 74.9455]).addTo(map).bindPopup("<b>Bathinda</b>");

    // Load GeoJSON district boundaries
    fetch("/api/geojson")
        .then(res => res.json())
        .then(data => {
            geojsonLayer = L.geoJSON(data, {
                style: feature => ({
                    fillColor: feature.properties.color || "#16A34A",
                    weight: 1.8,
                    opacity: 1,
                    color: "#1E293B",
                    fillOpacity: 0.70
                }),
                onEachFeature: (feature, layer) => {
                    const props = feature.properties;
                    layer.bindTooltip(`<b>${props.name}</b><br>Stress Score: ${props.stress_score}/100<br>Soil: ${props.soil_type}`);
                    layer.on("click", () => {
                        const select = document.getElementById("districtSelect");
                        select.value = props.name;
                        loadDistrictData(props.name);
                    });
                }
            }).addTo(map);
        })
        .catch(err => console.error("Error loading GeoJSON:", err));
}

// Event Listeners
function setupEventListeners() {
    // District Select
    document.getElementById("districtSelect").addEventListener("change", (e) => {
        loadDistrictData(e.target.value);
    });

    // Language Toggle
    document.querySelectorAll(".lang-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentLang = btn.getAttribute("data-lang");
            loadDistrictData(currentDistrict);
        });
    });

    // Calculator inputs
    const farmSlider = document.getElementById("farmSizeSlider");
    farmSlider.addEventListener("input", (e) => {
        document.getElementById("farmSizeLabel").innerText = e.target.value;
        updateCalculator();
        updateCropSimulator();
    });

    document.getElementById("practiceSelect").addEventListener("change", updateCalculator);
    document.getElementById("cropChoiceSelect").addEventListener("change", updateCropSimulator);

    // Soil Inputs
    ["soilPh", "soilEc", "soilOc", "soilN"].forEach(id => {
        document.getElementById(id).addEventListener("input", updateSoilPrescription);
    });

    // Voice button
    document.getElementById("btnVoice").addEventListener("click", () => {
        const line1 = document.getElementById("advLine1").innerText;
        const line2 = document.getElementById("advLine2").innerText;
        const text = `${line1}. ${line2}`;
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = currentLang === "hi" || currentLang === "pa" ? "hi-IN" : "en-US";
            utter.rate = 0.95;
            window.speechSynthesis.speak(utter);
        } else {
            alert("Web Speech API not supported in this browser.");
        }
    });
}

// Load District Telemetry
function loadDistrictData(district) {
    currentDistrict = district;
    fetch(`/api/telemetry?district=${encodeURIComponent(district)}&lang=${currentLang}`)
        .then(res => res.json())
        .then(data => {
            renderTelemetry(data);
        })
        .catch(err => console.error("Error loading telemetry:", err));
}

// Render Telemetry Data into DOM
function renderTelemetry(data) {
    // 1. Map Updates
    if (map && marker) {
        map.setView([data.lat, data.lon], data.is_hotspot ? 6 : 7);
        marker.setLatLng([data.lat, data.lon]);
        marker.bindPopup(`<b>${data.district}</b><br>Score: ${data.stress.score}/100 (${data.stress.zone})`).openPopup();
    }

    // 2. Stress Card
    const stressScoreVal = document.getElementById("stressScoreVal");
    const stressBadge = document.getElementById("stressBadge");
    stressScoreVal.innerText = `${data.stress.score}/100`;
    stressBadge.innerText = `${data.stress.zone} Zone`;
    stressBadge.className = `badge ${data.stress.zone === "Red" ? "badge-critical" : (data.stress.zone === "Yellow" ? "badge-warning" : "badge-safe")}`;

    // 3. Soil Status
    const soilBadge = document.getElementById("soilBadge");
    const soilStatusText = document.getElementById("soilStatusText");
    if (data.soil_diagnosis.alert_triggered) {
        soilBadge.innerText = "Critical";
        soilBadge.className = "badge badge-critical";
        soilStatusText.innerText = "Alert: Low Organic Carbon & Alkaline";
    } else {
        soilBadge.innerText = "Optimal";
        soilBadge.className = "badge badge-safe";
        soilStatusText.innerText = "Optimal Soil Health & Carbon Balance";
    }

    // 4. Advisory & WhatsApp
    const advLine1 = document.getElementById("advLine1");
    const advLine2 = document.getElementById("advLine2");
    advLine1.innerText = `• ${data.advisory.line1}`;
    advLine2.innerText = `• ${data.advisory.line2}`;

    const waMsg = `🌾 Punjab Farm Water Watch Alert - ${data.district}\nWater Stress: ${data.stress.score}/100 (${data.stress.zone})\n1. ${data.advisory.line1}\n2. ${data.advisory.line2}\nNASA Live Verified.`;
    document.getElementById("btnWhatsApp").href = `https://wa.me/?text=${encodeURIComponent(waMsg)}`;

    // 5. Delta Cards
    const d = data.deltas;
    document.getElementById("deltaSmNow").innerHTML = `${d.sm_now} <span style="font-size:0.82rem; color:#94A3B8;">m³/m³</span>`;
    document.getElementById("deltaSmSub").innerHTML = `30d Ago: ${d.sm_old} | <b style="color:${d.sm_diff < -0.02 ? '#DC2626' : '#16A34A'};">${d.sm_diff > 0 ? '+' : ''}${d.sm_diff}</b>`;

    document.getElementById("deltaNdviNow").innerText = d.ndvi_now;
    document.getElementById("deltaNdviSub").innerHTML = `30d Ago: ${d.ndvi_old} | <b style="color:${d.ndvi_diff < -0.04 ? '#DC2626' : '#16A34A'};">${d.ndvi_diff > 0 ? '+' : ''}${d.ndvi_diff}</b>`;

    document.getElementById("deltaScoreNow").innerHTML = `${d.score_now} <span style="font-size:0.82rem; color:#94A3B8;">/ 100</span>`;
    document.getElementById("deltaScoreSub").innerHTML = `30d Ago: ${d.score_old} | <b style="color:${d.score_diff > 5 ? '#DC2626' : '#16A34A'};">${d.score_diff > 0 ? '+' : ''}${d.score_diff} pts</b>`;

    // 6. Forecast Chart
    renderForecastChart(data.chart_data);

    // 7. Calendar
    renderCalendar(data.calendar_days);

    // 8. Download Dossier Button
    document.getElementById("btnDownloadReport").href = `/api/report/${encodeURIComponent(data.district)}`;

    // 9. Update Report Preview
    fetch(`/api/report/${encodeURIComponent(data.district)}`)
        .then(res => res.text())
        .then(txt => {
            document.getElementById("reportPreview").innerText = txt;
        });

    updateCalculator();
    updateCropSimulator();
}

// Chart.js Forecast Line Chart
function renderForecastChart(chartData) {
    const ctx = document.getElementById("forecastChart").getContext("2d");
    if (forecastChart) {
        forecastChart.destroy();
    }

    const labels = [...chartData.history_dates, ...chartData.forecast_dates];
    const histPoints = [...chartData.history_sm];
    while (histPoints.length < labels.length) histPoints.push(null);

    const fcPoints = new Array(chartData.history_dates.length - 1).fill(null);
    fcPoints.push(chartData.history_sm[chartData.history_sm.length - 1]);
    chartData.forecast_sm.forEach(val => fcPoints.push(val));

    forecastChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "30-Day SMAP Soil Moisture",
                    data: histPoints,
                    borderColor: "#0F4C5C",
                    borderWidth: 2.5,
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    label: "7-Day Random Forest Forecast",
                    data: fcPoints,
                    borderColor: "#B45309",
                    borderWidth: 2.5,
                    borderDash: [5, 5],
                    pointRadius: 3,
                    pointBackgroundColor: "#B45309",
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: "#1E293B", font: { weight: "600" } }
                }
            },
            scales: {
                x: {
                    grid: { color: "#E2E8F0" },
                    ticks: { color: "#475569", maxTicksLimit: 6 }
                },
                y: {
                    min: 0.0,
                    max: 0.65,
                    grid: { color: "#E2E8F0" },
                    ticks: { color: "#475569" },
                    title: { display: true, text: "Soil Moisture (m³/m³)", color: "#475569" }
                }
            }
        }
    });
}

// Render 7-Day Precision Calendar
function renderCalendar(days) {
    const grid = document.getElementById("calendarGrid");
    grid.innerHTML = "";
    days.forEach(d => {
        const card = document.createElement("div");
        card.className = "calendar-card";
        card.innerHTML = `
            <div class="calendar-icon">${d.icon}</div>
            <div style="flex-grow: 1;">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <b style="color:#FFF; font-size:0.86rem;">${d.day_label}: ${d.title}</b>
                    <span class="badge" style="border:1px solid ${d.badge_color}; color:${d.badge_color}; background:transparent;">${d.badge}</span>
                </div>
                <div style="font-size:0.80rem; color:#CBD5E1; margin-bottom:4px;">${d.action}</div>
                <div style="font-size:0.72rem; color:#64748B;">Projected: <b>${d.projected_sm.toFixed(3)} m³/m³</b> · Zone: <b style="color:${d.badge_color};">${d.risk_zone}</b></div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Reactive Calculator
function updateCalculator() {
    const acres = parseFloat(document.getElementById("farmSizeSlider").value);
    const practice = document.getElementById("practiceSelect").value;
    const pctMap = {
        "DSR (Direct Seeded Rice) / Mulching": 0.20,
        "Delay Irrigation by 3 Days": 0.10,
        "Crop-Residue Mulching": 0.15,
        "Combined Protocol": 0.30
    };
    const ratio = pctMap[practice] || 0.20;
    const baseline = acres * 900000;
    const saved = baseline * ratio;
    const kwh = Math.round(saved * 0.000789);

    const litresDisplay = saved >= 1000000 ? `${(saved / 1000000).toFixed(1)}M` : `${Math.round(saved).toLocaleString()}`;
    document.getElementById("calcLitresSaved").innerText = litresDisplay;
    document.getElementById("calcKwhSaved").innerText = `⚡ Electricity Saved: ${kwh.toLocaleString()} kWh`;
}

// Reactive Crop Simulator
function updateCropSimulator() {
    const acres = parseFloat(document.getElementById("farmSizeSlider").value);
    const cropChoice = document.getElementById("cropChoiceSelect").value;

    fetch("/api/simulator/crop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ crop_choice: cropChoice, farm_acres: acres })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("cropDemandVal").innerText = `${data.crop_water_demand_m}M Litres`;
        document.getElementById("cropSavedVal").innerText = `${data.groundwater_saved_m}M Litres (${Math.round(data.pct_saved)}%)`;
        document.getElementById("cropPowerVal").innerText = `${data.kwh_saved.toLocaleString()} kWh`;
        document.getElementById("cropRecommendation").innerHTML = `💡 <b>Agronomic Guidance:</b> ${data.recommendation}`;
    })
    .catch(err => console.error(err));
}

// Reactive Soil Prescription
function updateSoilPrescription() {
    const ph = parseFloat(document.getElementById("soilPh").value) || 8.6;
    const ec = parseFloat(document.getElementById("soilEc").value) || 0.9;
    const oc = parseFloat(document.getElementById("soilOc").value) || 0.38;
    const n = parseInt(document.getElementById("soilN").value) || 190;

    fetch("/api/simulator/soil", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ph, ec, oc, nitrogen: n })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("rxItem1").innerText = data.prescription[0];
        document.getElementById("rxItem2").innerText = data.prescription[1];
        document.getElementById("rxItem3").innerText = data.prescription[2];
        const statusEl = document.getElementById("rxStatus");
        statusEl.innerText = data.status;
        statusEl.style.color = data.status_color;
    })
    .catch(err => console.error(err));
}
