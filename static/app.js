// Punjab Farm Water Watch - Client Application
let currentDistrict = "Bathinda";
let currentLang = "en";
let map = null;
let geojsonLayer = null;
let marker = null;
let forecastChart = null;

// Dashboard Charts Instances
let dashMoistureChart = null;
let dashRainChart = null;
let dashVigorChart = null;
let dashEtLstChart = null;
let dashStressDonutChart = null;
let dashBenchmarkChart = null;
let dashScenarioChart = null;

// Initialize when DOM loads
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initDrawer();
    initTabs();
    initMap();
    setupEventListeners();
    loadDistrictData(currentDistrict);
});

// Hamburger Menu & Side Drawer Navigation
function initDrawer() {
    const hamburgerBtn = document.getElementById("hamburgerBtn");
    const navDrawer = document.getElementById("navDrawer");
    const drawerOverlay = document.getElementById("drawerOverlay");
    const drawerCloseBtn = document.getElementById("drawerCloseBtn");

    function openDrawer() {
        if (navDrawer && drawerOverlay) {
            navDrawer.classList.add("open");
            drawerOverlay.classList.add("active");
            if (hamburgerBtn) hamburgerBtn.classList.add("is-active");
            document.body.style.overflow = "hidden";
        }
    }

    function closeDrawer() {
        if (navDrawer && drawerOverlay) {
            navDrawer.classList.remove("open");
            drawerOverlay.classList.remove("active");
            if (hamburgerBtn) hamburgerBtn.classList.remove("is-active");
            document.body.style.overflow = "";
        }
    }

    if (hamburgerBtn) hamburgerBtn.addEventListener("click", openDrawer);
    if (drawerCloseBtn) drawerCloseBtn.addEventListener("click", closeDrawer);
    if (drawerOverlay) drawerOverlay.addEventListener("click", closeDrawer);

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && navDrawer && navDrawer.classList.contains("open")) {
            closeDrawer();
        }
    });

    // Drawer Navigation Buttons
    document.querySelectorAll(".drawer-nav-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            const topTabBtn = document.querySelector(`.tab-btn[data-tab="${target}"]`);
            if (topTabBtn) {
                topTabBtn.click();
            }
            document.querySelectorAll(".drawer-nav-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            closeDrawer();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });

    // Sync Drawer District Selector with Main District Selector
    const mainSelect = document.getElementById("districtSelect");
    const drawerSelect = document.getElementById("drawerDistrictSelect");
    if (mainSelect && drawerSelect) {
        drawerSelect.innerHTML = mainSelect.innerHTML;
        drawerSelect.value = mainSelect.value;

        drawerSelect.addEventListener("change", (e) => {
            mainSelect.value = e.target.value;
            loadDistrictData(e.target.value);
            closeDrawer();
        });

        mainSelect.addEventListener("change", (e) => {
            drawerSelect.value = e.target.value;
        });
    }

    // Keep drawer active tab synced when top tab changes
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            document.querySelectorAll(".drawer-nav-btn").forEach(b => {
                if (b.getAttribute("data-tab") === target) {
                    b.classList.add("active");
                } else {
                    b.classList.remove("active");
                }
            });
        });
    });
}

// Theme Management (Dark / Light Mode)
function initTheme() {
    const savedTheme = localStorage.getItem("pww_theme") || "dark";
    applyTheme(savedTheme);

    const toggleBtn = document.getElementById("themeToggleBtn");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") || "dark";
            const newTheme = current === "dark" ? "light" : "dark";
            applyTheme(newTheme);
        });
    }
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("pww_theme", theme);

    const themeIcon = document.getElementById("themeIcon");
    const themeText = document.getElementById("themeText");
    if (themeIcon && themeText) {
        if (theme === "light") {
            themeIcon.innerText = "🌙";
            themeText.innerText = "Dark";
        } else {
            themeIcon.innerText = "☀️";
            themeText.innerText = "Light";
        }
    }
}

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
                if (target === "tab-dashboard") {
                    setTimeout(() => {
                        [dashMoistureChart, dashRainChart, dashVigorChart, dashEtLstChart, dashStressDonutChart, dashBenchmarkChart, dashScenarioChart].forEach(c => {
                            if (c) c.resize();
                        });
                    }, 100);
                }
            }
        });
    });

    // Support footer navigation links
    document.querySelectorAll(".footer-nav").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const target = link.getAttribute("data-tab");
            const btn = document.querySelector(`.tab-btn[data-tab="${target}"]`);
            if (btn) {
                btn.click();
                window.scrollTo({ top: 0, behavior: "smooth" });
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
        maxZoom: 15
    });

    // Base Layers
    const esriSatellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
        attribution: 'Tiles &copy; Esri & NASA',
        maxZoom: 18
    }).addTo(map);

    const darkMatter = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; CartoDB & OpenStreetMap',
        maxZoom: 19
    });

    // Layer control
    L.control.layers({
        "🌍 High-Res Satellite (Esri)": esriSatellite,
        "🗺️ Dark Matter": darkMatter
    }, null, { position: "topright" }).addTo(map);

    // Initial marker with custom styling
    marker = L.marker([30.2110, 74.9455]).addTo(map);

    // Load authentic GeoJSON district boundaries
    fetch("/api/geojson")
        .then(res => res.json())
        .then(data => {
            geojsonLayer = L.geoJSON(data, {
                style: feature => {
                    const color = feature.properties.color || "#10B981";
                    return {
                        fillColor: color,
                        weight: 1.6,
                        opacity: 0.85,
                        color: "#38BDF8", // Clean cyan administrative border
                        fillOpacity: 0.35, // Balanced opacity so real agricultural fields are visible
                        dashArray: ""
                    };
                },
                onEachFeature: (feature, layer) => {
                    const props = feature.properties;
                    const zoneBadgeClass = props.zone === "Red" ? "badge-critical" : (props.zone === "Yellow" ? "badge-warning" : "badge-safe");

                    layer.bindTooltip(`
                        <div class="map-tooltip-box">
                            <div class="tooltip-header">${props.name}</div>
                            <div class="tooltip-sub"><span class="badge ${zoneBadgeClass}">${props.zone} Risk · ${props.stress_score}/100</span></div>
                            <div class="tooltip-detail">🌱 Crop: ${props.primary_crop || 'Paddy / Wheat'}</div>
                            <div class="tooltip-detail">🧪 Soil: ${props.soil_type || 'Alluvial Loam'}</div>
                        </div>
                    `, {
                        sticky: true,
                        direction: "top",
                        className: "custom-gis-tooltip",
                        opacity: 0.98
                    });

                    layer.on({
                        mouseover: (e) => {
                            const l = e.target;
                            l.setStyle({
                                weight: 2.8,
                                color: "#F59E0B", // Warm amber highlight
                                fillOpacity: 0.60
                            });
                            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                                l.bringToFront();
                            }
                        },
                        mouseout: (e) => {
                            geojsonLayer.resetStyle(e.target);
                        },
                        click: () => {
                            selectDistrict(props.name);
                        }
                    });
                }
            }).addTo(map);
        })
        .catch(err => console.error("Error loading GeoJSON:", err));
}

// Select district from map or UI
function selectDistrict(name) {
    const select = document.getElementById("districtSelect");
    const drawerSelect = document.getElementById("drawerDistrictSelect");
    let found = false;
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].value === name) {
            select.selectedIndex = i;
            found = true;
            break;
        }
    }
    if (!found) {
        const optGroup = select.querySelector('optgroup[label="Punjab Districts"]') || select;
        const newOpt = document.createElement("option");
        newOpt.value = name;
        newOpt.text = `Punjab - ${name}`;
        newOpt.selected = true;
        optGroup.appendChild(newOpt);
    }
    if (drawerSelect) {
        drawerSelect.innerHTML = select.innerHTML;
        drawerSelect.value = name;
    }
    loadDistrictData(name);
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
        map.flyTo([data.lat, data.lon], data.is_hotspot ? 6 : 8, { duration: 0.8 });
        marker.setLatLng([data.lat, data.lon]);
        marker.bindPopup(`
            <div class="marker-popup-card">
                <div style="font-weight:700; color:#F59E0B; font-size:1rem; margin-bottom:4px;">📍 ${data.district}</div>
                <div style="font-size:0.85rem; color:#E2E8F0; margin-bottom:4px;">Stress Score: <b>${data.stress.score}/100</b></div>
                <div><span class="badge ${data.stress.zone === 'Red' ? 'badge-critical' : (data.stress.zone === 'Yellow' ? 'badge-warning' : 'badge-safe')}">${data.stress.zone} Risk Zone</span></div>
                <div style="font-size:0.75rem; color:#94A3B8; margin-top:6px;">Centroid: ${data.lat.toFixed(4)}°N, ${data.lon.toFixed(4)}°E</div>
            </div>
        `);
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

    // 6. Forecast Chart & Dashboard Analytics
    renderForecastChart(data.chart_data);
    renderDashboardKPIs(data);
    renderDashboardCharts(data);

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

// ==========================================================================
// VISUAL ANALYTICS & GRAPHS DASHBOARD FUNCTIONS
// ==========================================================================

function renderDashboardKPIs(data) {
    const dName = document.getElementById("dashDistrictName");
    if (dName) dName.innerText = data.district;

    const kpiStress = document.getElementById("dashKpiStress");
    if (kpiStress) {
        kpiStress.innerText = `${data.stress.score}/100`;
        kpiStress.style.color = data.stress.zone === "Red" ? "#DC2626" : (data.stress.zone === "Yellow" ? "#F59E0B" : "#16A34A");
    }

    const kpiSm = document.getElementById("dashKpiSm");
    if (kpiSm) kpiSm.innerText = `${data.latest.smap_rootzone_sm}`;

    const kpiRain = document.getElementById("dashKpiRain");
    if (kpiRain) kpiRain.innerText = `${data.latest.gpm_rain_30d}`;

    const kpiNdvi = document.getElementById("dashKpiNdvi");
    if (kpiNdvi) kpiNdvi.innerText = `${data.latest.landsat_ndvi}`;

    const kpiLst = document.getElementById("dashKpiLst");
    if (kpiLst) kpiLst.innerText = `${data.latest.landsat_lst_c}`;
}

function renderDashboardCharts(data) {
    const cd = data.chart_data;
    if (!cd) return;

    renderDashMoistureChart(cd);
    renderDashRainChart(cd);
    renderDashVigorChart(cd);
    renderDashEtLstChart(cd);
    renderDashStressDonut(cd.stress_components);
    renderDashBenchmark(cd.district_benchmarks);
    renderDashScenario();
}

function renderDashMoistureChart(cd) {
    const ctx = document.getElementById("dashMoistureChart");
    if (!ctx) return;
    if (dashMoistureChart) dashMoistureChart.destroy();

    const labels = [...cd.history_dates, ...cd.forecast_dates];
    const rzPoints = [...cd.history_sm];
    while (rzPoints.length < labels.length) rzPoints.push(null);

    const surfPoints = [...(cd.history_surface_sm || cd.history_sm)];
    while (surfPoints.length < labels.length) surfPoints.push(null);

    const fcPoints = new Array(cd.history_dates.length - 1).fill(null);
    fcPoints.push(cd.history_sm[cd.history_sm.length - 1]);
    cd.forecast_sm.forEach(v => fcPoints.push(v));

    dashMoistureChart = new Chart(ctx.getContext("2d"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Rootzone SM (0–100cm)",
                    data: rzPoints,
                    borderColor: "#0284C7",
                    borderWidth: 2.5,
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    label: "Surface SM (0–5cm)",
                    data: surfPoints,
                    borderColor: "#0D9488",
                    borderWidth: 1.8,
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    label: "7-Day RF Outlook",
                    data: fcPoints,
                    borderColor: "#F59E0B",
                    borderDash: [5, 5],
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: "#F59E0B",
                    tension: 0.2
                },
                {
                    label: "Field Capacity (0.36)",
                    data: new Array(labels.length).fill(0.36),
                    borderColor: "rgba(16, 185, 129, 0.6)",
                    borderDash: [3, 3],
                    borderWidth: 1.5,
                    pointRadius: 0
                },
                {
                    label: "Wilting Point (0.10)",
                    data: new Array(labels.length).fill(0.10),
                    borderColor: "rgba(239, 68, 68, 0.6)",
                    borderDash: [3, 3],
                    borderWidth: 1.5,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { color: "#94A3B8", font: { size: 10 } } } },
            scales: {
                x: { grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8", maxTicksLimit: 7 } },
                y: { min: 0.05, max: 0.42, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8" }, title: { display: true, text: "m³/m³", color: "#94A3B8" } }
            }
        }
    });
}

function renderDashRainChart(cd) {
    const ctx = document.getElementById("dashRainChart");
    if (!ctx) return;
    if (dashRainChart) dashRainChart.destroy();

    dashRainChart = new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: cd.history_dates,
            datasets: [
                {
                    label: "Daily Precipitation (mm)",
                    data: cd.history_rain,
                    backgroundColor: "rgba(56, 189, 248, 0.6)",
                    borderColor: "#38BDF8",
                    borderWidth: 1,
                    yAxisID: "y"
                },
                {
                    type: "line",
                    label: "30d Cumulative Rain (mm)",
                    data: cd.history_cum_rain,
                    borderColor: "#10B981",
                    borderWidth: 2.2,
                    pointRadius: 0,
                    tension: 0.1,
                    yAxisID: "y1"
                },
                {
                    type: "line",
                    label: "50mm Buffer Threshold",
                    data: new Array(cd.history_dates.length).fill(50),
                    borderColor: "rgba(239, 68, 68, 0.6)",
                    borderDash: [4, 4],
                    borderWidth: 1.5,
                    pointRadius: 0,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { color: "#94A3B8", font: { size: 10 } } } },
            scales: {
                x: { grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8", maxTicksLimit: 7 } },
                y: { type: "linear", position: "left", min: 0, max: 20, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8" }, title: { display: true, text: "Daily mm", color: "#94A3B8" } },
                y1: { type: "linear", position: "right", min: 0, max: 65, grid: { drawOnChartArea: false }, ticks: { color: "#10B981" }, title: { display: true, text: "Cumul mm", color: "#10B981" } }
            }
        }
    });
}

function renderDashVigorChart(cd) {
    const ctx = document.getElementById("dashVigorChart");
    if (!ctx) return;
    if (dashVigorChart) dashVigorChart.destroy();

    dashVigorChart = new Chart(ctx.getContext("2d"), {
        type: "line",
        data: {
            labels: cd.history_dates,
            datasets: [
                {
                    label: "NDVI (Greenness)",
                    data: cd.history_ndvi,
                    borderColor: "#16A34A",
                    backgroundColor: "rgba(22, 163, 74, 0.1)",
                    fill: true,
                    borderWidth: 2.2,
                    pointRadius: 0,
                    tension: 0.25
                },
                {
                    label: "SAVI (Soil-Adjusted)",
                    data: cd.history_savi,
                    borderColor: "#84CC16",
                    borderWidth: 1.8,
                    pointRadius: 0,
                    tension: 0.25
                },
                {
                    label: "NDWI (Canopy Water)",
                    data: cd.history_ndwi,
                    borderColor: "#06B6D4",
                    borderWidth: 1.8,
                    pointRadius: 0,
                    tension: 0.25
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { color: "#94A3B8", font: { size: 10 } } } },
            scales: {
                x: { grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8", maxTicksLimit: 7 } },
                y: { min: 0.15, max: 0.65, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8" }, title: { display: true, text: "Spectral Index", color: "#94A3B8" } }
            }
        }
    });
}

function renderDashEtLstChart(cd) {
    const ctx = document.getElementById("dashEtLstChart");
    if (!ctx) return;
    if (dashEtLstChart) dashEtLstChart.destroy();

    dashEtLstChart = new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: cd.history_dates,
            datasets: [
                {
                    type: "bar",
                    label: "MODIS ET (mm/day)",
                    data: cd.history_et,
                    backgroundColor: "rgba(245, 158, 11, 0.45)",
                    borderColor: "#F59E0B",
                    borderWidth: 1,
                    yAxisID: "y"
                },
                {
                    type: "line",
                    label: "Landsat LST (°C)",
                    data: cd.history_lst,
                    borderColor: "#EF4444",
                    borderWidth: 2.2,
                    pointRadius: 1,
                    tension: 0.2,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { color: "#94A3B8", font: { size: 10 } } } },
            scales: {
                x: { grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8", maxTicksLimit: 7 } },
                y: { type: "linear", position: "left", min: 0, max: 8, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8" }, title: { display: true, text: "ET mm/day", color: "#94A3B8" } },
                y1: { type: "linear", position: "right", min: 20, max: 45, grid: { drawOnChartArea: false }, ticks: { color: "#EF4444" }, title: { display: true, text: "LST °C", color: "#EF4444" } }
            }
        }
    });
}

function renderDashStressDonut(sc) {
    const ctx = document.getElementById("dashStressDonutChart");
    if (!ctx) return;
    if (dashStressDonutChart) dashStressDonutChart.destroy();
    if (!sc) sc = { smap_contrib: 40, rain_contrib: 30, et_contrib: 20, lst_contrib: 10 };

    dashStressDonutChart = new Chart(ctx.getContext("2d"), {
        type: "doughnut",
        data: {
            labels: ["SMAP Moisture (40%)", "GPM Rain (30%)", "MODIS ET (20%)", "Landsat LST (10%)"],
            datasets: [{
                data: [sc.smap_contrib, sc.rain_contrib, sc.et_contrib, sc.lst_contrib],
                backgroundColor: ["#0284C7", "#38BDF8", "#F59E0B", "#EF4444"],
                borderColor: "#0C2933",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "62%",
            plugins: {
                legend: { position: "bottom", labels: { color: "#94A3B8", font: { size: 10 }, boxWidth: 10 } }
            }
        }
    });
}

function renderDashBenchmark(benchmarks) {
    const ctx = document.getElementById("dashBenchmarkChart");
    if (!ctx) return;
    if (dashBenchmarkChart) dashBenchmarkChart.destroy();
    if (!benchmarks || !benchmarks.length) return;

    dashBenchmarkChart = new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: benchmarks.map(b => b.district),
            datasets: [{
                label: "Stress Score",
                data: benchmarks.map(b => b.score),
                backgroundColor: benchmarks.map(b => b.color || (b.score > 60 ? "#DC2626" : (b.score > 30 ? "#F59E0B" : "#16A34A"))),
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { min: 0, max: 100, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94A3B8" } },
                y: { grid: { display: false }, ticks: { color: "#CBD5E1", font: { weight: "600" } } }
            }
        }
    });
}

function renderDashScenario() {
    const ctx = document.getElementById("dashScenarioChart");
    if (!ctx) return;
    if (dashScenarioChart) dashScenarioChart.destroy();

    dashScenarioChart = new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: ["Flood Paddy", "DSR", "3d Delay", "Crop Switch"],
            datasets: [
                {
                    label: "Water (M Litres)",
                    data: [9.0, 7.2, 7.65, 3.6],
                    backgroundColor: "rgba(56, 189, 248, 0.7)",
                    borderRadius: 4,
                    yAxisID: "y"
                },
                {
                    label: "Power Saved (kWh)",
                    data: [0, 1420, 1065, 4260],
                    backgroundColor: "rgba(245, 158, 11, 0.7)",
                    borderRadius: 4,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top", labels: { color: "#94A3B8", font: { size: 9 }, boxWidth: 10 } } },
            scales: {
                x: { grid: { display: false }, ticks: { color: "#CBD5E1", font: { size: 9 } } },
                y: { min: 0, max: 10, ticks: { color: "#38BDF8", font: { size: 9 } }, title: { display: true, text: "M Litres", color: "#38BDF8", font: { size: 9 } } },
                y1: { position: "right", min: 0, max: 5000, grid: { drawOnChartArea: false }, ticks: { color: "#F59E0B", font: { size: 9 } }, title: { display: true, text: "kWh", color: "#F59E0B", font: { size: 9 } } }
            }
        }
    });
}
