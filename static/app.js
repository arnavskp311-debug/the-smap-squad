// Punjab Farm Water Watch - Client Application
let currentDistrict = "Bathinda";
let currentLang = "en";
let map = null;
let geojsonLayer = null;
let marker = null;
let forecastChart = null;
let lastTelemetryData = null;

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
    initLanguage();
    initDrawer();
    initTabs();
    initMap();
    initNasaStatus();
    initNetworkMonitor();
    initServiceWorker();
    initAuth();
    populateHotspotDistricts("Punjab", currentDistrict || "Bathinda");
    setupEventListeners();
    initPanchayatLeaderboard();
    loadDistrictData(currentDistrict);
});

// 2G & Live Network Connectivity Monitor
function initNetworkMonitor() {
    const pill = document.getElementById("networkPill");
    const text = document.getElementById("networkText");

    function updateStatus() {
        if (!pill || !text) return;
        const isOnline = navigator.onLine;
        const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        const effectiveType = conn ? conn.effectiveType : null;
        const is2G = effectiveType === "2g" || effectiveType === "slow-2g";

        pill.classList.remove("network-online", "network-2g", "network-offline");

        if (!isOnline) {
            pill.classList.add("network-offline");
            text.innerText = currentLang === "pa" ? "ਆਫਲਾਈਨ (ਕੈਸ਼)" : (currentLang === "hi" ? "ऑफ़लाइन (कैश)" : "Offline (Cached)");
            pill.title = "Offline Mode: Telemetry rendered from local cached storage.";
        } else if (is2G) {
            pill.classList.add("network-2g");
            text.innerText = currentLang === "pa" ? "2G ਮੋਡ (ਸੇਵ)" : (currentLang === "hi" ? "2G मोड (डेटा बचत)" : "2G Mode (Data Saved)");
            pill.title = "2G Network Detected: Ultra-compressed instant satellite telemetry loaded.";
        } else {
            pill.classList.add("network-online");
            text.innerText = currentLang === "pa" ? "ਲਾਈਵ ਸਿੰਕ" : (currentLang === "hi" ? "लाइव सिंक" : "Live Synced");
            pill.title = "NASA Earthdata Satellite Telemetry Live Synced.";
        }
    }

    window.addEventListener("online", updateStatus);
    window.addEventListener("offline", updateStatus);
    if (navigator.connection) {
        navigator.connection.addEventListener("change", updateStatus);
    }
    updateStatus();
}

// Offline PWA Service Worker Registration
function initServiceWorker() {
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/sw.js").then(reg => {
                console.log("[PWW SW] Active with scope:", reg.scope);
            }).catch(err => {
                console.warn("[PWW SW] Registration failed:", err);
            });
        });
    }
}

// NASA API Key & Live Status
function initNasaStatus() {
    fetch("/api/nasa/status")
        .then(res => {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .catch(async () => {
            const r = await fetch("data/nasa_status.json");
            return await r.json();
        })
        .then(data => {
            const pillText = document.getElementById("nasaPillText");
            const pill = document.getElementById("nasaPill");
            if (pillText && data.authenticated) {
                pillText.innerText = "NASA API Live";
                if (pill) {
                    pill.title = `NASA api.nasa.gov Key: ${data.api_key_masked} · Authenticated & Rate Limit: ${data.rate_limit_limit} reqs/day`;
                }
            }
        })
        .catch(err => console.warn("NASA status fetch error:", err));
}

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
            switchTab(target);
            closeDrawer();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });
}

// 5 Global Hotspots & Expanding Sub-Districts System
const HOTSPOT_DISTRICTS = {
    "Punjab": [
        { value: "Bathinda", label: "Punjab - Bathinda" },
        { value: "Amritsar", label: "Punjab - Amritsar" },
        { value: "Barnala", label: "Punjab - Barnala" },
        { value: "Faridkot", label: "Punjab - Faridkot" },
        { value: "Fatehgarh Sahib", label: "Punjab - Fatehgarh Sahib" },
        { value: "Fazilka", label: "Punjab - Fazilka" },
        { value: "Ferozepur", label: "Punjab - Ferozepur" },
        { value: "Gurdaspur", label: "Punjab - Gurdaspur" },
        { value: "Hoshiarpur", label: "Punjab - Hoshiarpur" },
        { value: "Jalandhar", label: "Punjab - Jalandhar" },
        { value: "Kapurthala", label: "Punjab - Kapurthala" },
        { value: "Ludhiana", label: "Punjab - Ludhiana" },
        { value: "Mansa", label: "Punjab - Mansa" },
        { value: "Moga", label: "Punjab - Moga" },
        { value: "Pathankot", label: "Punjab - Pathankot" },
        { value: "Patiala", label: "Punjab - Patiala" },
        { value: "Rupnagar", label: "Punjab - Rupnagar" },
        { value: "S.A.S. Nagar", label: "Punjab - S.A.S. Nagar (Mohali)" },
        { value: "Sangrur", label: "Punjab - Sangrur" },
        { value: "Shahid Bhagat Singh Nagar", label: "Punjab - SBS Nagar" },
        { value: "Sri Muktsar Sahib", label: "Punjab - Sri Muktsar Sahib" },
        { value: "Tarn Taran", label: "Punjab - Tarn Taran" }
    ],
    "Central Valley": [
        { value: "Central Valley - Fresno County (USA)", label: "Fresno County (USA - Red Zone)" },
        { value: "Central Valley - Kern County (USA)", label: "Kern County / Bakersfield (USA - Red Zone)" },
        { value: "Central Valley - Tulare County (USA)", label: "Tulare County (USA - Red Zone)" },
        { value: "Central Valley - San Joaquin (USA)", label: "San Joaquin County (USA - Yellow Zone)" },
        { value: "Central Valley - Sacramento (USA)", label: "Sacramento County (USA - Green Zone)" },
        { value: "Central Valley (California, USA)", label: "Central Valley Regional Basin Overview" }
    ],
    "Nile Delta": [
        { value: "Nile Delta - Kafr El-Sheikh (Egypt)", label: "Kafr El-Sheikh (Egypt - Red Zone)" },
        { value: "Nile Delta - Beheira (Egypt)", label: "Beheira Governorate (Egypt - Red Zone)" },
        { value: "Nile Delta - Dakahlia (Egypt)", label: "Dakahlia Governorate (Egypt - Yellow Zone)" },
        { value: "Nile Delta - Gharbia (Egypt)", label: "Gharbia Governorate (Egypt - Green Zone)" },
        { value: "Nile Delta (Egypt)", label: "Nile Delta Regional Basin Overview" }
    ],
    "Murray-Darling": [
        { value: "Murray-Darling - Riverina (Australia)", label: "Riverina (Australia - Red Zone)" },
        { value: "Murray-Darling - Sunraysia (Australia)", label: "Sunraysia (Australia - Red Zone)" },
        { value: "Murray-Darling - Murrumbidgee (Australia)", label: "Murrumbidgee (Australia - Yellow Zone)" },
        { value: "Murray-Darling - Goulburn Valley (Australia)", label: "Goulburn Valley (Australia - Green Zone)" },
        { value: "Murray-Darling Basin (Australia)", label: "Murray-Darling Regional Basin Overview" }
    ],
    "Indo-Gangetic": [
        { value: "Bathinda", label: "Upper Indus Basin - Punjab" },
        { value: "Sangrur", label: "Central Malwa Depletion Zone" },
        { value: "Patiala", label: "Ghaggar River Aquifer Sub-basin" }
    ]
};

const DISTRICT_NAMES_LOCALIZED = {
    "Bathinda": { pa: "ਬਠਿੰਡਾ", hi: "बठिंडा", en: "Bathinda" },
    "Amritsar": { pa: "ਅੰਮ੍ਰਿਤਸਰ", hi: "अमृतसर", en: "Amritsar" },
    "Barnala": { pa: "ਬਰਨਾਲਾ", hi: "बरनाला", en: "Barnala" },
    "Faridkot": { pa: "ਫ਼ਰੀਦਕੋਟ", hi: "फरीदकोट", en: "Faridkot" },
    "Fatehgarh Sahib": { pa: "ਫ਼ਤਹਿਗੜ੍ਹ ਸਾਹਿਬ", hi: "फतेहगढ़ साहिब", en: "Fatehgarh Sahib" },
    "Fazilka": { pa: "ਫ਼ਾਜ਼ਿਲਕਾ", hi: "फाजिल्का", en: "Fazilka" },
    "Ferozepur": { pa: "ਫ਼ਿਰੋਜ਼ਪੁਰ", hi: "फिरोजपुर", en: "Ferozepur" },
    "Gurdaspur": { pa: "ਗੁਰਦਾਸਪੁਰ", hi: "गुरदासपुर", en: "Gurdaspur" },
    "Hoshiarpur": { pa: "ਹੁਸ਼ਿਆਰਪੁਰ", hi: "होशियारपुर", en: "Hoshiarpur" },
    "Jalandhar": { pa: "ਜਲੰਧਰ", hi: "जालंधर", en: "Jalandhar" },
    "Kapurthala": { pa: "ਕਪੂਰਥਲਾ", hi: "कपूरथला", en: "Kapurthala" },
    "Ludhiana": { pa: "ਲੁਧਿਆਣਾ", hi: "लुधियाना", en: "Ludhiana" },
    "Mansa": { pa: "ਮਾਨਸਾ", hi: "मानसा", en: "Mansa" },
    "Moga": { pa: "ਮੋਗਾ", hi: "मोगा", en: "Moga" },
    "Pathankot": { pa: "ਪਠਾਨਕੋਟ", hi: "पठानकोट", en: "Pathankot" },
    "Patiala": { pa: "ਪਟਿਆਲਾ", hi: "पटियाला", en: "Patiala" },
    "Rupnagar": { pa: "ਰੂਪਨਗਰ", hi: "रूपनगर", en: "Rupnagar" },
    "S.A.S. Nagar": { pa: "ਐੱਸ.ਏ.ਐੱਸ. ਨਗਰ (ਮੋਹਾਲੀ)", hi: "एस.ए.एस. नगर (मोहाली)", en: "S.A.S. Nagar (Mohali)" },
    "Sangrur": { pa: "ਸੰਗਰੂਰ", hi: "संगरूर", en: "Sangrur" },
    "Shahid Bhagat Singh Nagar": { pa: "ਸ਼ਹੀਦ ਭਗਤ ਸਿੰਘ ਨਗਰ", hi: "शहीद भगत सिंह नगर", en: "SBS Nagar" },
    "Sri Muktsar Sahib": { pa: "ਸ੍ਰੀ ਮੁਕਤਸਰ ਸਾਹਿਬ", hi: "श्री मुक्तसर साहिब", en: "Sri Muktsar Sahib" },
    "Tarn Taran": { pa: "ਤਰਨ ਤਾਰਨ", hi: "तरन तारण", en: "Tarn Taran" }
};

function getLocalizedDistrictName(district, lang) {
    if (DISTRICT_NAMES_LOCALIZED[district] && DISTRICT_NAMES_LOCALIZED[district][lang]) {
        return DISTRICT_NAMES_LOCALIZED[district][lang];
    }
    return district;
}

function getZoneBadgeText(zone, lang) {
    if (lang === "pa") {
        if (zone === "Red") return "ਲਾਲ ਜੋਖਮ ਜ਼ੋਨ";
        if (zone === "Yellow") return "ਪੀਲਾ ਦਰਮਿਆਨਾ ਜ਼ੋਨ";
        return "ਹਰਾ ਸੁਰੱਖਿਅਤ ਜ਼ੋਨ";
    }
    if (lang === "hi") {
        if (zone === "Red") return "लाल जोखिम क्षेत्र";
        if (zone === "Yellow") return "पीला मध्यम क्षेत्र";
        return "हरा सुरक्षित क्षेत्र";
    }
    if (zone === "Red") return "Red Risk Zone";
    if (zone === "Yellow") return "Yellow Warning Zone";
    return "Green Safe Zone";
}

function updateThemeButtonText() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const themeIcon = document.getElementById("themeIcon");
    const themeText = document.getElementById("themeText");
    if (!themeIcon || !themeText) return;
    if (current === "light") {
        themeIcon.innerText = "🌙";
        themeText.innerText = currentLang === "pa" ? "ਡਾਰਕ" : (currentLang === "hi" ? "डार्क" : "Dark");
    } else {
        themeIcon.innerText = "☀️";
        themeText.innerText = currentLang === "pa" ? "ਲਾਈਟ" : (currentLang === "hi" ? "लाइट" : "Light");
    }
}

function populateHotspotDistricts(hotspotKey, selectedDistrict = null) {
    const districtSelect = document.getElementById("districtSelect");
    if (!districtSelect) return;
    const list = HOTSPOT_DISTRICTS[hotspotKey] || HOTSPOT_DISTRICTS["Punjab"];
    districtSelect.innerHTML = "";
    list.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.value;
        if (hotspotKey === "Punjab") {
            const locName = getLocalizedDistrictName(item.value, currentLang);
            if (currentLang === "pa") {
                opt.textContent = `ਪੰਜਾਬ - ${locName}`;
            } else if (currentLang === "hi") {
                opt.textContent = `पंजाब - ${locName}`;
            } else {
                opt.textContent = item.label;
            }
        } else {
            opt.textContent = item.label;
        }
        if (selectedDistrict && opt.value === selectedDistrict) {
            opt.selected = true;
        }
        districtSelect.appendChild(opt);
    });
    if (!selectedDistrict && districtSelect.options.length > 0) {
        districtSelect.selectedIndex = 0;
    }
}

// Global Tab Switcher Function
function switchTab(target) {
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
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

    // Keep drawer active state synced
    document.querySelectorAll(".drawer-nav-btn").forEach(b => {
        if (b.getAttribute("data-tab") === target) {
            b.classList.add("active");
        } else {
            b.classList.remove("active");
        }
    });

    // Keep mobile bottom nav active state synced
    document.querySelectorAll(".mobile-nav-btn").forEach(b => {
        if (b.getAttribute("data-tab") === target) {
            b.classList.add("active");
        } else {
            b.classList.remove("active");
        }
    });
}

// Theme Management (Dark / Light Mode)
function initTheme() {
    // Migration: default to Light mode on load
    if (localStorage.getItem("pww_theme_v2") !== "light_default_v2") {
        localStorage.setItem("pww_theme", "light");
        localStorage.setItem("pww_theme_v2", "light_default_v2");
    }

    const savedTheme = localStorage.getItem("pww_theme") || "light";
    applyTheme(savedTheme);

    const toggleBtn = document.getElementById("themeToggleBtn");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = current === "light" ? "dark" : "light";
            applyTheme(newTheme);
        });
    }
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("pww_theme", theme);

    updateThemeButtonText();

    // Immediately re-render forecast chart with theme-aligned colors
    if (lastTelemetryData && lastTelemetryData.chart_data) {
        renderForecastChart(lastTelemetryData.chart_data);
    }
}

// Multilingual i18n Dictionary (English, Hindi, Punjabi)
const I18N_DICTIONARY = {
    "en": {
        "nav_guide": "User Guide",
        "nav_panchayat": "Panchayat Leaderboard",
        "nav_mission": "Mission Control",
        "nav_dashboard": "Dashboard",
        "nav_forecast": "7-Day Forecast",
        "nav_agrisense": "AgriSense",
        "nav_report": "Farmer Identity Card",
        "nav_team": "Team",
        "nav_about": "About",
        "nav_signin": "Sign In",
        "lbl_platform_tools": "Platform Tools",
        "lbl_basemap": "🛰️ Basemap Layer:",
        "layer_dark_matter": "🗺️ Dark Matter",
        "layer_satellite": "🌍 Satellite (Esri)",
        "layer_nasa_gibs": "🛰️ NASA GIBS Live",
        "layer_black_marble": "🌌 NASA Black Marble",
        "lbl_water_stress_score": "Water Stress Score",
        "lbl_comp_water_stress": "Composite Water Stress Index (0–100)",
        "lbl_soil_quality_status": "Soil Quality Status",
        "lbl_smap_landsat_corr": "SMAP vs Landsat NDVI/SAVI Correlation",
        "lbl_farmer_advisory": "Farmer Advisory & Action",
        "btn_whatsapp": "💬 WhatsApp",
        "btn_listen_voice": "🔊 Listen Voice",
        "lbl_delta_sm": "SMAP Rootzone Soil Moisture",
        "lbl_delta_ndvi": "Landsat 8/9 Canopy NDVI",
        "lbl_delta_score": "Water Stress Index (0–100)",
        "lbl_30d_ago": "30d Ago",
        "zone_red": "Red Risk Zone",
        "zone_yellow": "Yellow Warning Zone",
        "zone_green": "Green Safe Zone",
        "badge_optimal": "Optimal",
        "badge_critical": "Critical",
        "soil_optimal_text": "Optimal Soil Health & Carbon Balance",
        "soil_critical_text": "Alert: Low Organic Carbon & Alkaline",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "pre_lang_title": "🌐 Choose Your Language / भाषा चुनें / ਭਾਸ਼ਾ ਚੁਣੋ:",
        "auth_title": "Mandatory Farmer & Sentinel Access",
        "auth_subtitle": "Access to Punjab's live NASA SMAP telemetry, GIS spatial maps, and groundwater advisories requires verified farmer registration or direct sign-in.",
        "tab_register_auth": "📝 New Farmer Registration",
        "tab_login_auth": "🔑 Direct Sign-In",
        "auth_lbl_name": "Full Name *",
        "auth_lbl_email": "Email Address *",
        "auth_lbl_pass": "Create Account Password *",
        "auth_lbl_phone": "Mobile / WhatsApp No. (For Daily Telemetry Alerts) *",
        "auth_lbl_acres": "Farm Holding (Acres) *",
        "auth_lbl_crop": "Primary Cropping Cycle *",
        "auth_lbl_source": "Tubewell / Irrigation Type *",
        "auth_lbl_district": "Farm Location / District *",
        "auth_lbl_photo": "Profile Photo (From Device)",
        "auth_btn_register": "Register Account &amp; Unlock Water Pass",
        "auth_note": "🔒 All farm information is securely cataloged into Punjab Ag-Stack for authentic telemetry.",
        "login_lbl_email": "Registered Email Address *",
        "login_lbl_pass": "Account Password *",
        "login_btn_submit": "Direct Sign-In to Farm Account",
        "login_no_acc_text": "Don't have an account yet?",
        "login_switch_register": "Register Your Farm Here",
        "guide_hero_title": "📘 Punjab Farm Water Watch · User Guide",
        "guide_hero_subtitle": "Complete operational manual for farmers, agricultural officers, and water stewards to monitor groundwater, plan precision irrigation, and save power using NASA satellite data.",
        "guide_nav_1": "🛰️ Satellite Map",
        "guide_nav_2": "⚠️ Stress Index",
        "guide_nav_3": "📅 7-Day Plan",
        "guide_nav_4": "💡 Simulator",
        "guide_nav_5": "🪪 Water Pass",
        "guide_c1_title": "🛰️ NASA SMAP Satellite &amp; GIS Map",
        "guide_c1_desc": "Explore high-resolution district-level soil moisture and irrigation hotspots across Punjab and major global food-basket aquifer basins.",
        "guide_c1_f1": "<b>Hotspot Selector:</b> Toggle between Punjab, Central Valley, Nile Delta, and Murray-Darling.",
        "guide_c1_f2": "<b>District Dropdown:</b> Select any of Punjab's 22 districts (e.g. Bathinda, Sangrur, Ludhiana).",
        "guide_c1_f3": "<b>Satellite Basemaps:</b> Switch between Dark Matter, Esri High-Res Satellite, NASA GIBS Live TrueColor, and Black Marble.",
        "guide_c1_tip": "💡 <b>Tip:</b> Click any district boundary directly on the map to inspect live water metrics!",
        "guide_c2_title": "⚠️ Water Stress Score &amp; Soil Diagnosis",
        "guide_c2_desc": "Understand composite aquifer stress scores combining NASA SMAP, GPM Precipitation, Landsat LST, and MODIS ET.",
        "guide_c2_f1": "<b>Green (0–39):</b> Safe moisture levels; no immediate pumping needed.",
        "guide_c2_f2": "<b>Yellow (40–69):</b> Moderate stress; schedule light, precision morning irrigation.",
        "guide_c2_f3": "<b>Red (70–100):</b> Critical over-extraction risk; follow strict tubewell runtime limits.",
        "guide_c2_f4": "<b>Dual Soil Diagnosis:</b> Detects soil moisture salinity, hardpan compaction, or low organic carbon.",
        "guide_c2_tip": "💡 <b>Action:</b> Read the Soil Testing &amp; Remedy Guide under the AgriSense tab for laboratory correction steps.",
        "guide_c3_title": "📅 7-Day Forecast &amp; Irrigation Calendar",
        "guide_c3_desc": "AI-powered autoregressive moisture forecaster plans daily irrigation and avoids pumping before rain events.",
        "guide_c3_f1": "<b>7-Day Trend Chart:</b> Visualizes forecasted rootzone volumetric soil moisture (m³/m³).",
        "guide_c3_f2": "<b>Tubewell Pumping Hours:</b> Recommended motor operation (e.g. 2.0 hrs/day instead of 8 hrs).",
        "guide_c3_f3": "<b>Voice Broadcast:</b> Click 'Broadcast Audio Advisory' to hear your farm's advisory in Hindi/Punjabi!",
        "guide_c3_f4": "<b>WhatsApp Alert:</b> Instant one-click dispatch to share farm guidance with local village groups.",
        "guide_c3_tip": "💡 <b>Tip:</b> Rain predicted days display zero irrigation hours to conserve groundwater.",
        "guide_c4_title": "💡 Crop Budget &amp; Power Simulator",
        "guide_c4_desc": "Simulate direct financial and environmental savings by adopting water-conserving agronomic practices.",
        "guide_c4_f1": "<b>Farm Size Slider:</b> Adjust your land acreage (1 to 50 acres) to dynamically calculate savings.",
        "guide_c4_f2": "<b>Practice Comparison:</b> Compare Direct Seeded Rice (DSR), Alternate Wetting &amp; Drying (AWD), and Drip.",
        "guide_c4_f3": "<b>Energy Savings:</b> View tubewell electricity units (kWh) and carbon emissions saved.",
        "guide_c4_tip": "💡 <b>Benefit:</b> Qualifying farms earn water stewardship points reflected on their Water Pass!",
        "guide_c5_title": "🪪 Digital Farmer Water Pass",
        "guide_c5_desc": "Your official Punjab Agri-Hydrology digital identity verifying water-saving stewardship and farm credentials.",
        "guide_c5_f1": "<b>Member ID &amp; Serial:</b> Official identification number tied to your district and farm profile.",
        "guide_c5_f2": "<b>Cumulative Metrics:</b> Total groundwater liters and power saved tracked live.",
        "guide_c5_f3": "<b>Print / Download:</b> Export your high-contrast Water Pass for official subsidy and canal credit applications.",
        "guide_c5_tip": "💡 <b>Access:</b> Click your profile avatar in the top-right corner anytime to view or print your pass.",
        "guide_c6_title": "🌐 Language &amp; Theme Customization",
        "guide_c6_desc": "Customize your viewing experience for outdoor field use or desktop research.",
        "guide_c6_f1": "<b>Language Selector:</b> Choose English (EN), हिन्दी (HI), or ਪੰਜਾਬੀ (PA) before or after sign-in.",
        "guide_c6_f2": "<b>Light / Dark Mode:</b> High-contrast light mode for bright sunlight; dark mode for mission control.",
        "guide_c6_f3": "<b>Persistence:</b> Your language and theme preferences are automatically saved on your device.",
        "guide_c6_tip": "💡 <b>Tip:</b> Use the top navbar buttons to toggle language or theme with a single click.",
        "mob_nav_map": "Mission",
        "mob_nav_dash": "Analytics",
        "mob_nav_plan": "7-Day",
        "mob_nav_soil": "AgriSense",
        "mob_nav_pass": "Water Pass"
    },
    "hi": {
        "nav_guide": "यूज़र गाइड",
        "nav_panchayat": "पंचायत लीडरबोर्ड",
        "nav_mission": "मिशन कंट्रोल",
        "nav_dashboard": "डैशबोर्ड",
        "nav_forecast": "7-दिवसीय पूर्वानुमान",
        "nav_agrisense": "एग्रीसेंस",
        "nav_report": "किसान पहचान पत्र",
        "nav_team": "टीम",
        "nav_about": "परिचय",
        "nav_signin": "साइन इन",
        "lbl_platform_tools": "प्लेटफ़ॉर्म टूल्स",
        "lbl_basemap": "🛰️ बेसमैप परत:",
        "layer_dark_matter": "🗺️ डार्क मैटर",
        "layer_satellite": "🌍 सैटेलाइट (एजरी)",
        "layer_nasa_gibs": "🛰️ नासा गिब्स लाइव",
        "layer_black_marble": "🌌 नासा ब्लैक मार्बल",
        "lbl_water_stress_score": "जल तनाव स्कोर",
        "lbl_comp_water_stress": "संयुक्त जल तनाव सूचकांक (0–100)",
        "lbl_soil_quality_status": "मिट्टी की गुणवत्ता स्थिति",
        "lbl_smap_landsat_corr": "SMAP बनाम लैंडसैट NDVI/SAVI सहसंबंध",
        "lbl_farmer_advisory": "किसान सलाह एवं कार्रवाई",
        "btn_whatsapp": "💬 व्हाट्सएप",
        "btn_listen_voice": "🔊 आवाज सुनें",
        "lbl_delta_sm": "SMAP रूटज़ोन मिट्टी की नमी",
        "lbl_delta_ndvi": "लैंडसैट 8/9 कैनोपी NDVI",
        "lbl_delta_score": "जल तनाव सूचकांक (0–100)",
        "lbl_30d_ago": "30 दिन पूर्व",
        "zone_red": "लाल जोखिम क्षेत्र",
        "zone_yellow": "पीला मध्यम क्षेत्र",
        "zone_green": "हरा सुरक्षित क्षेत्र",
        "badge_optimal": "उत्कृष्ट",
        "badge_critical": "गंभीर",
        "soil_optimal_text": "उत्कृष्ट मिट्टी स्वास्थ्य एवं कार्बन संतुलन",
        "soil_critical_text": "चेतावनी: कम जैविक कार्बन एवं क्षारीयता",
        "theme_light": "लाइट",
        "theme_dark": "डार्क",
        "pre_lang_title": "🌐 अपनी पसंदीदा भाषा चुनें / Choose Language:",
        "auth_title": "किसान एवं प्रहरी आधिकारिक पोर्टल",
        "auth_subtitle": "पंजाब की लाइव नासा SMAP टेलीमेट्री, उपग्रह नक्शे और सटीक भूजल सलाहकारों तक पहुंच के लिए किसान पंजीकरण या सीधा साइन-इन अनिवार्य है।",
        "tab_register_auth": "📝 नया किसान पंजीकरण",
        "tab_login_auth": "🔑 सीधा साइन-इन",
        "auth_lbl_name": "पूरा नाम *",
        "auth_lbl_email": "ईमेल पता *",
        "auth_lbl_pass": "खाता पासवर्ड बनाएं *",
        "auth_lbl_phone": "मोबाइल / व्हाट्सएप नं. (दैनिक अलर्ट हेतु) *",
        "auth_lbl_acres": "खेत का आकार (एकड़) *",
        "auth_lbl_crop": "मुख्य फसल चक्र *",
        "auth_lbl_source": "ट्यूबवेल / सिंचाई का साधन *",
        "auth_lbl_district": "खेत का स्थान / जिला *",
        "auth_lbl_photo": "प्रोफाइल फोटो (डिवाइस से)",
        "auth_btn_register": "खाता पंजीकृत करें व वाटर पास प्राप्त करें",
        "auth_note": "🔒 सभी कृषि जानकारी प्रामाणिक टेलीमेट्री हेतु पंजाब एग-स्टैक में सुरक्षित दर्ज की जाती है।",
        "login_lbl_email": "पंजीकृत ईमेल पता *",
        "login_lbl_pass": "खाता पासवर्ड *",
        "login_btn_submit": "खेत खाते में सीधा साइन-इन करें",
        "login_no_acc_text": "क्या अभी तक खाता नहीं है?",
        "login_switch_register": "यहाँ अपना खेत पंजीकृत करें",
        "guide_hero_title": "📘 पंजाब फार्म वाटर वॉच · उपयोगकर्ता मार्गदर्शिका",
        "guide_hero_subtitle": "नासा उपग्रह डेटा का उपयोग करके भूजल की निगरानी, सटीक सिंचाई योजना और बिजली बचाने के लिए किसानों और कृषि अधिकारियों हेतु संपूर्ण मार्गदर्शिका।",
        "guide_nav_1": "🛰️ उपग्रह नक्शा",
        "guide_nav_2": "⚠️ तनाव स्कोर",
        "guide_nav_3": "📅 7-दिवसीय योजना",
        "guide_nav_4": "💡 कैलकुलेटर",
        "guide_nav_5": "🪪 वाटर पास",
        "guide_c1_title": "🛰️ नासा SMAP उपग्रह एवं भूजल नक्शा",
        "guide_c1_desc": "पंजाब के सभी 22 जिलों और वैश्विक जल-संकट क्षेत्रों की उच्च-सटीक उपग्रह नमी और भूमि स्थिति का निरीक्षण करें।",
        "guide_c1_f1": "<b>हॉटस्पॉट चयन:</b> पंजाब, सेंट्रल वैली (USA), नील डेल्टा और मरे-डार्लिंग के बीच स्विच करें।",
        "guide_c1_f2": "<b>जिला ड्रॉपडाउन:</b> बठिंडा, संगरूर, लुधियाना सहित पंजाब का कोई भी जिला चुनें।",
        "guide_c1_f3": "<b>सैटेलाइट बेस-मैप:</b> डार्क मैटर, एज़री हाई-रेज़ोल्यूशन सैटेलाइट, नासा GIBS लाइव और ब्लैक मार्बल चुनें।",
        "guide_c1_tip": "💡 <b>टिप:</b> लाइव डेटा देखने के लिए नक्शे पर किसी भी जिले की सीमा पर सीधे क्लिक करें!",
        "guide_c2_title": "⚠️ जल तनाव स्कोर व मिट्टी की सेहत",
        "guide_c2_desc": "नासा SMAP नमी, वर्षा, लैंडसैट तापमान और MODIS वाष्पोत्सर्जन के संयुक्त स्कोर को समझें।",
        "guide_c2_f1": "<b>हरा (0–39):</b> सुरक्षित नमी स्तर; तुरंत सिंचाई की आवश्यकता नहीं।",
        "guide_c2_f2": "<b>पीला (40–69):</b> मध्यम तनाव; सुबह के समय हल्की व सटीक सिंचाई करें।",
        "guide_c2_f3": "<b>लाल (70–100):</b> गंभीर भूजल संकट; ट्यूबवेल चलने के समय पर सख्त नियंत्रण रखें।",
        "guide_c2_f4": "<b>दोहरी मिट्टी जांच:</b> खारेपन, कड़ेपन (Hardpan) और कम जैविक कार्बन की पहचान करता है।",
        "guide_c2_tip": "💡 <b>सलाह:</b> प्रयोगशाला उपचार के लिए 'एग्रीसेंस' टैब में 'मृदा परीक्षण गाइड' देखें।",
        "guide_c3_title": "📅 7-दिवसीय पूर्वानुमान व 30-दिवसीय सिंचाई कैलेंडर",
        "guide_c3_desc": "AI नमी पूर्वानुमानकर्ता दैनिक सिंचाई की योजना बनाता है और बारिश से पहले व्यर्थ ट्यूबवेल चलाने से रोकता है।",
        "guide_c3_f1": "<b>7-दिवसीय चार्ट:</b> आने वाले 7 दिनों की जड़-क्षेत्रीय नमी का सटीक रुझान।",
        "guide_c3_f2": "<b>ट्यूबवेल संचालन घंटे:</b> प्रतिदिन मोटर चलाने का अनुशंसित समय (उदा. 8 घंटे के बजाय केवल 2 घंटे)।",
        "guide_c3_f3": "<b>ध्वनि प्रसारण:</b> अपने जिले की कृषि सलाह हिंदी या पंजाबी में सुनने के लिए 'ऑडियो प्रसारण' पर क्लिक करें।",
        "guide_c3_f4": "<b>व्हाट्सएप अलर्ट:</b> एक क्लिक में गांव के किसान समूहों के साथ दैनिक सलाह साझा करें।",
        "guide_c3_tip": "💡 <b>टिप:</b> वर्षा पूर्वानुमान वाले दिनों में स्वतः 0 घंटे की सिफारिश होती है ताकि पानी बच सके।",
        "guide_c4_title": "💡 फसल बजट व सौर/ट्यूबवेल बचत कैलकुलेटर",
        "guide_c4_desc": "पानी की बचत करने वाली आधुनिक कृषि पद्धतियों को अपनाकर आर्थिक व बिजली की बचत का आंकलन करें।",
        "guide_c4_f1": "<b>खेत का आकार:</b> एकड़ (1 से 50) स्लाइडर को हिलाकर तुरंत बचत देखें।",
        "guide_c4_f2": "<b>पद्धति तुलना:</b> सीधी बिजाई (DSR), अल्टरनेट वेटिंग (AWD) और ड्रिप की तुलना करें।",
        "guide_c4_f3": "<b>ऊर्जा बचत:</b> बचाई गई बिजली यूनिट्स (kWh) और कम हुए कार्बन उत्सर्जन को जानें।",
        "guide_c4_tip": "💡 <b>लाभ:</b> पानी बचाने वाले किसानों को वाटर पास पर विशेष स्टार रेटिंग मिलती है!",
        "guide_c5_title": "🪪 डिजिटल किसान वाटर पास",
        "guide_c5_desc": "पंजाब कृषि-जलविज्ञान द्वारा प्रमाणित आपकी आधिकारिक डिजिटल पहचान, जो जल संरक्षण योगदान प्रमाणित करती है।",
        "guide_c5_f1": "<b>सदस्य आईडी व सीरियल:</b> आपके जिले और खेत से जुड़ी विशिष्ट पहचान संख्या।",
        "guide_c5_f2": "<b>कुल संचयी बचत:</b> आपके द्वारा बचाए गए लाखों लीटर भूजल और बिजली का लाइव रिकॉर्ड।",
        "guide_c5_f3": "<b>प्रिंट / डाउनलोड:</b> सरकारी सब्सिडी और सोलर ट्यूबवेल योजनाओं के लिए वाटर पास डाउनलोड करें।",
        "guide_c5_tip": "💡 <b>खोलने का तरीका:</b> अपना पास देखने या प्रिंट करने के लिए ऊपर दाईं ओर अपनी प्रोफ़ाइल पर क्लिक करें।",
        "guide_c6_title": "🌐 भाषा चयन व डार्क/लाइट मोड",
        "guide_c6_desc": "धूप में खेत में उपयोग के लिए या घर पर अनुसंधान के लिए स्क्रीन को अनुकूलित करें।",
        "guide_c6_f1": "<b>भाषा चयन:</b> साइन-इन से पहले या बाद में कभी भी अंग्रेजी, हिन्दी या पंजाबी चुनें।",
        "guide_c6_f2": "<b>लाइट / डार्क मोड:</b> तेज़ धूप के लिए उच्च-कंट्रास्ट लाइट मोड और रात के लिए डार्क मोड।",
        "guide_c6_f3": "<b>सुरक्षित चयन:</b> आपकी चुनी हुई भाषा और थीम आपके ब्राउज़र में सुरक्षित रूप से याद रखी जाती है।",
        "guide_c6_tip": "💡 <b>टिप:</b> ऊपर नेविगेशन बार में दिए गए बटनों से एक क्लिक में भाषा या थीम बदलें।",
        "mob_nav_map": "मिशन",
        "mob_nav_dash": "विश्लेषण",
        "mob_nav_plan": "7-दिन",
        "mob_nav_soil": "मृदा टेस्ट",
        "mob_nav_pass": "जल पास"
    },
    "pa": {
        "nav_guide": "ਯੂਜ਼ਰ ਗਾਈਡ",
        "nav_panchayat": "ਪੰਚਾਇਤ ਲੀਡਰਬੋਰਡ",
        "nav_mission": "ਮਿਸ਼ਨ ਕੰਟਰੋਲ",
        "nav_dashboard": "ਡੈਸ਼ਬੋਰਡ",
        "nav_forecast": "7-ਦਿਨਾਂ ਭਵਿੱਖਬਾਣੀ",
        "nav_agrisense": "ਐਗਰੀਸੈਂਸ",
        "nav_report": "ਕਿਸਾਨ ਪਛਾਣ ਪੱਤਰ",
        "nav_team": "ਟੀਮ",
        "nav_about": "ਬਾਰੇ",
        "nav_signin": "ਸਾਈਨ ਇਨ",
        "lbl_platform_tools": "ਪਲੇਟਫਾਰਮ ਟੂਲਜ਼",
        "lbl_basemap": "🛰️ ਬੇਸਮੈਪ ਪਰਤ:",
        "layer_dark_matter": "🗺️ ਡਾਰਕ ਮੈਟਰ",
        "layer_satellite": "🌍 ਸੈਟੇਲਾਈਟ (ਐਸਰੀ)",
        "layer_nasa_gibs": "🛰️ ਨਾਸਾ ਜਿਬਸ ਲਾਈਵ",
        "layer_black_marble": "🌌 ਨਾਸਾ ਬਲੈਕ ਮਾਰਬਲ",
        "lbl_water_stress_score": "ਵਾਟਰ ਸਟ੍ਰੈਸ ਸਕੋਰ",
        "lbl_comp_water_stress": "ਸੰਯੁਕਤ ਵਾਟਰ ਸਟ੍ਰੈਸ ਇੰਡੈਕਸ (0–100)",
        "lbl_soil_quality_status": "ਮਿੱਟੀ ਦੀ ਗੁਣਵੱਤਾ ਦੀ ਸਥਿਤੀ",
        "lbl_smap_landsat_corr": "SMAP ਬਨਾਮ ਲੈਂਡਸੈਟ NDVI/SAVI ਸਹਿ-ਸੰਬੰਧ",
        "lbl_farmer_advisory": "ਕਿਸਾਨ ਸਲਾਹ ਅਤੇ ਕਾਰਵਾਈ",
        "btn_whatsapp": "💬 ਵਟਸਐਪ",
        "btn_listen_voice": "🔊 ਆਵਾਜ਼ ਸੁਣੋ",
        "lbl_delta_sm": "SMAP ਰੂਟਜ਼ੋਨ ਮਿੱਟੀ ਦੀ ਨਮੀ",
        "lbl_delta_ndvi": "ਲੈਂਡਸੈਟ 8/9 ਕੈਨੋਪੀ NDVI",
        "lbl_delta_score": "ਵਾਟਰ ਸਟ੍ਰੈਸ ਇੰਡੈਕਸ (0–100)",
        "lbl_30d_ago": "30 ਦਿਨ ਪਹਿਲਾਂ",
        "zone_red": "ਲਾਲ ਜੋਖਮ ਜ਼ੋਨ",
        "zone_yellow": "ਪੀਲਾ ਦਰਮਿਆਨਾ ਜ਼ੋਨ",
        "zone_green": "ਹਰਾ ਸੁਰੱਖਿਅਤ ਜ਼ੋਨ",
        "badge_optimal": "ਸਰਵੋਤਮ",
        "badge_critical": "ਗੰਭੀਰ",
        "soil_optimal_text": "ਸਰਵੋਤਮ ਮਿੱਟੀ ਸਿਹਤ ਅਤੇ ਕਾਰਬਨ ਸੰਤੁਲਨ",
        "soil_critical_text": "ਚੇਤਾਵਨੀ: ਘੱਟ ਜੈਵਿਕ ਕਾਰਬਨ ਅਤੇ ਖਾਰੀਤਾ",
        "theme_light": "ਲਾਈਟ",
        "theme_dark": "ਡਾਰਕ",
        "pre_lang_title": "🌐 ਆਪਣੀ ਪਸੰਦੀਦਾ ਭਾਸ਼ਾ ਚੁਣੋ / Choose Language:",
        "auth_title": "ਕਿਸਾਨ ਅਤੇ ਪਹਿਰੇਦਾਰ ਅਧਿਕਾਰਤ ਪੋਰਟਲ",
        "auth_subtitle": "ਪੰਜਾਬ ਦੀ ਲਾਈਵ ਨਾਸਾ SMAP ਟੈਲੀਮੈਟਰੀ, ਉਪਗ੍ਰਹਿ ਨਕਸ਼ੇ ਅਤੇ ਧਰਤੀ ਹੇਠਲੇ ਪਾਣੀ ਦੀਆਂ ਸਲਾਹਾਂ ਲਈ ਕਿਸਾਨ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਜਾਂ ਸਿੱਧਾ ਸਾਈਨ-ਇਨ ਲਾਜ਼ਮੀ ਹੈ।",
        "tab_register_auth": "📝 ਨਵਾਂ ਕਿਸਾਨ ਰਜਿਸਟ੍ਰੇਸ਼ਨ",
        "tab_login_auth": "🔑 ਸਿੱਧਾ ਸਾਈਨ-ਇਨ",
        "auth_lbl_name": "ਪੂਰਾ ਨਾਮ *",
        "auth_lbl_email": "ਈਮੇਲ ਪਤਾ *",
        "auth_lbl_pass": "ਖਾਤਾ ਪਾਸਵਰਡ ਬਣਾਓ *",
        "auth_lbl_phone": "ਮੋਬਾਈਲ / ਵਟਸਐਪ ਨੰਬਰ (ਰੋਜ਼ਾਨਾ ਅਲਰਟ ਲਈ) *",
        "auth_lbl_acres": "ਖੇਤ ਦਾ ਆਕਾਰ (ਏਕੜ) *",
        "auth_lbl_crop": "ਮੁੱਖ ਫਸਲ ਚੱਕਰ *",
        "auth_lbl_source": "ਟਿਊਬਵੈੱਲ / ਸਿੰਚਾਈ ਦਾ ਸਾਧਨ *",
        "auth_lbl_district": "ਖੇਤ ਦਾ ਸਥਾਨ / ਜ਼ਿਲ੍ਹਾ *",
        "auth_lbl_photo": "ਪ੍ਰੋਫਾਈਲ ਫੋਟੋ (ਡਿਵਾਈਸ ਤੋਂ)",
        "auth_btn_register": "ਖਾਤਾ ਰਜਿਸਟਰ ਕਰੋ ਅਤੇ ਵਾਟਰ ਪਾਸ ਪ੍ਰਾਪਤ ਕਰੋ",
        "auth_note": "🔒 ਸਾਰੀ ਖੇਤੀ ਜਾਣਕਾਰੀ ਪ੍ਰਮਾਣਿਕ ਟੈਲੀਮੈਟਰੀ ਲਈ ਪੰਜਾਬ ਐਗ-ਸਟੈਕ ਵਿੱਚ ਸੁਰੱਖਿਅਤ ਦਰਜ ਕੀਤੀ ਜਾਂਦੀ ਹੈ।",
        "login_lbl_email": "ਰਜਿਸਟਰਡ ਈਮੇਲ ਪਤਾ *",
        "login_lbl_pass": "ਖਾਤਾ ਪਾਸਵਰਡ *",
        "login_btn_submit": "ਖੇਤ ਖਾਤੇ ਵਿੱਚ ਸਿੱਧਾ ਸਾਈਨ-ਇਨ ਕਰੋ",
        "login_no_acc_text": "ਕੀ ਅਜੇ ਤੱਕ ਖਾਤਾ ਨਹੀਂ ਹੈ?",
        "login_switch_register": "ਇੱਥੇ ਆਪਣਾ ਖੇਤ ਰਜਿਸਟਰ ਕਰੋ",
        "guide_hero_title": "📘 ਪੰਜਾਬ ਫਾਰਮ ਵਾਟਰ ਵਾਚ · ਯੂਜ਼ਰ ਗਾਈਡ",
        "guide_hero_subtitle": "ਨਾਸਾ ਉਪਗ੍ਰਹਿ ਡੇਟਾ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਧਰਤੀ ਹੇਠਲੇ ਪਾਣੀ ਦੀ ਨਿਗਰਾਨੀ, ਸਹੀ ਸਿੰਚਾਈ ਯੋਜਨਾ ਅਤੇ ਬਿਜਲੀ ਬਚਾਉਣ ਲਈ ਕਿਸਾਨਾਂ ਅਤੇ ਖੇਤੀਬਾੜੀ ਅਧਿਕਾਰੀਆਂ ਲਈ ਸੰਪੂਰਨ ਗਾਈਡ।",
        "guide_nav_1": "🛰️ ਉਪਗ੍ਰਹਿ ਨਕਸ਼ਾ",
        "guide_nav_2": "⚠️ ਪਾਣੀ ਤਣਾਅ",
        "guide_nav_3": "📅 7-ਦਿਨਾਂ ਯੋਜਨਾ",
        "guide_nav_4": "💡 ਕੈਲਕੁਲੇਟਰ",
        "guide_nav_5": "🪪 ਵਾਟਰ ਪਾਸ",
        "guide_c1_title": "🛰️ ਨਾਸਾ SMAP ਉਪਗ੍ਰਹਿ ਤੇ ਜ਼ਮੀਨੀ ਨਕਸ਼ਾ",
        "guide_c1_desc": "ਪੰਜਾਬ ਦੇ ਸਾਰੇ 22 ਜ਼ਿਲ੍ਹਿਆਂ ਅਤੇ ਵਿਸ਼ਵ ਦੇ ਮੁੱਖ ਖੇਤੀਬਾੜੀ ਖੇਤਰਾਂ ਦੀ ਉਪਗ੍ਰਹਿ ਨਮੀ ਅਤੇ ਜ਼ਮੀਨੀ ਸਥਿਤੀ ਦੇਖੋ।",
        "guide_c1_f1": "<b>ਹਾਟਸਪਾਟ ਚੋਣ:</b> ਪੰਜਾਬ, ਸੈਂਟਰਲ ਵੈਲੀ (USA), ਨੀਲ ਡੈਲਟਾ ਅਤੇ ਮਰੇ-ਡਾਰਲਿੰਗ ਵਿਚਕਾਰ ਬਦਲੋ।",
        "guide_c1_f2": "<b>ਜ਼ਿਲ੍ਹਾ ਡ੍ਰੌਪਡਾਊਨ:</b> ਬਠਿੰਡਾ, ਸੰਗਰੂਰ, ਲੁਧਿਆਣਾ ਸਮੇਤ ਪੰਜਾਬ ਦਾ ਕੋਈ ਵੀ ਜ਼ਿਲ੍ਹਾ ਚੁਣੋ।",
        "guide_c1_f3": "<b>ਸੈਟੇਲਾਈਟ ਬੇਸ-ਮੈਪ:</b> ਡਾਰਕ ਮੈਟਰ, ਐਸਰੀ ਹਾਈ-ਰੈਜ਼ੋਲਿਊਸ਼ਨ ਸੈਟੇਲਾਈਟ, ਨਾਸਾ GIBS ਲਾਈਵ ਅਤੇ ਬਲੈਕ ਮਾਰਬਲ ਚੁਣੋ।",
        "guide_c1_tip": "💡 <b>ਸੁਝਾਅ:</b> ਲਾਈਵ ਅੰਕੜੇ ਦੇਖਣ ਲਈ ਨਕਸ਼ੇ 'ਤੇ ਕਿਸੇ ਵੀ ਜ਼ਿਲ੍ਹੇ ਦੀ ਸੀਮਾ 'ਤੇ ਸਿੱਧਾ ਕਲਿੱਕ ਕਰੋ!",
        "guide_c2_title": "⚠️ ਪਾਣੀ ਤਣਾਅ ਸਕੋਰ ਤੇ ਮਿੱਟੀ ਦੀ ਪਰਖ",
        "guide_c2_desc": "ਨਾਸਾ SMAP ਨਮੀ, ਵਰਖਾ, ਲੈਂਡਸੈੱਟ ਤਾਪਮਾਨ ਅਤੇ MODIS ਵਾਸ਼ਪੀਕਰਨ ਦੇ ਸਾਂਝੇ ਸਕੋਰ ਨੂੰ ਸਮਝੋ।",
        "guide_c2_f1": "<b>ਹਰਾ (0–39):</b> ਸੁਰੱਖਿਅਤ ਨਮੀ ਪੱਧਰ; ਤੁਰੰਤ ਟਿਊਬਵੈੱਲ ਚਲਾਉਣ ਦੀ ਲੋੜ ਨਹੀਂ।",
        "guide_c2_f2": "<b>ਪੀਲਾ (40–69):</b> ਦਰਮਿਆਨਾ ਤਣਾਅ; ਸਵੇਰ ਵੇਲੇ ਹਲਕੀ ਤੇ ਸੰਕੋਚਵੀਂ ਸਿੰਚਾਈ ਕਰੋ।",
        "guide_c2_f3": "<b>ਲਾਲ (70–100):</b> ਗੰਭੀਰ ਪਾਣੀ ਸੰਕਟ; ਟਿਊਬਵੈੱਲ ਚਲਾਉਣ ਦੇ ਸਮੇਂ 'ਤੇ ਸਖ਼ਤ ਕੰਟਰੋਲ ਰੱਖੋ।",
        "guide_c2_f4": "<b>ਦੋਹਰੀ ਮਿੱਟੀ ਪਰਖ:</b> ਖਾਰੇਪਣ, ਸਖ਼ਤਪਣ (Hardpan) ਅਤੇ ਘੱਟ ਜੈਵਿਕ ਕਾਰਬਨ ਦੀ ਪਛਾਣ ਕਰਦਾ ਹੈ।",
        "guide_c2_tip": "💡 <b>ਕਾਰਵਾਈ:</b> ਲੈਬਾਰਟਰੀ ਇਲਾਜ ਲਈ 'ਐਗਰੀਸੈਂਸ' ਟੈਬ ਵਿੱਚ 'ਮਿੱਟੀ ਪਰਖ ਗਾਈਡ' ਪੜ੍ਹੋ।",
        "guide_c3_title": "📅 7-ਦਿਨਾਂ ਭਵਿੱਖਬਾਣੀ ਤੇ 30-ਦਿਨਾਂ ਸਿੰਚਾਈ ਕੈਲੰਡਰ",
        "guide_c3_desc": "AI ਨਮੀ ਭਵਿੱਖਬਾਣੀ ਕਰਤਾ ਰੋਜ਼ਾਨਾ ਸਿੰਚਾਈ ਦੀ ਯੋਜਨਾ ਬਣਾਉਂਦਾ ਹੈ ਅਤੇ ਮੀਂਹ ਤੋਂ ਪਹਿਲਾਂ ਟਿਊਬਵੈੱਲ ਚਲਾਉਣ ਤੋਂ ਰੋਕਦਾ ਹੈ।",
        "guide_c3_f1": "<b>7-ਦਿਨਾਂ ਚਾਰਟ:</b> ਆਉਣ ਵਾਲੇ 7 ਦਿਨਾਂ ਦੀ ਜੜ੍ਹ-ਖੇਤਰੀ ਨਮੀ ਦਾ ਸਹੀ ਰੁਝਾਨ।",
        "guide_c3_f2": "<b>ਟਿਊਬਵੈੱਲ ਚਲਾਉਣ ਦੇ ਘੰਟੇ:</b> ਰੋਜ਼ਾਨਾ ਮੋਟਰ ਚਲਾਉਣ ਦਾ ਸਿਫਾਰਸ਼ੀ ਸਮਾਂ (ਜਿਵੇਂ 8 ਘੰਟਿਆਂ ਦੀ ਬਜਾਏ ਸਿਰਫ 2 ਘੰਟੇ)।",
        "guide_c3_f3": "<b>ਆਵਾਜ਼ ਪ੍ਰਸਾਰਣ:</b> ਆਪਣੇ ਖੇਤ ਦੀ ਸਲਾਹ ਪੰਜਾਬੀ ਜਾਂ ਹਿੰਦੀ ਵਿੱਚ ਸੁਣਨ ਲਈ 'ਆਡੀਓ ਪ੍ਰਸਾਰਣ' 'ਤੇ ਕਲਿੱਕ ਕਰੋ।",
        "guide_c3_f4": "<b>ਵਟਸਐਪ ਅਲਰਟ:</b> ਇੱਕ ਕਲਿੱਕ ਵਿੱਚ ਪਿੰਡ ਦੇ ਕਿਸਾਨ ਗਰੁੱਪਾਂ ਨਾਲ ਖੇਤੀ ਸਲਾਹ ਸਾਂਝੀ ਕਰੋ।",
        "guide_c3_tip": "💡 <b>ਸੁਝਾਅ:</b> ਮੀਂਹ ਵਾਲੇ ਦਿਨਾਂ ਵਿੱਚ ਜ਼ੀਰੋ ਘੰਟੇ ਦੀ ਸਿਫਾਰਸ਼ ਹੁੰਦੀ ਹੈ ਤਾਂ ਜੋ ਧਰਤੀ ਹੇਠਲਾ ਪਾਣੀ ਬਚ ਸਕੇ।",
        "guide_c4_title": "💡 ਫਸਲ ਬਜਟ ਤੇ ਸੌਰ/ਟਿਊਬਵੈੱਲ ਬੱਚਤ ਕੈਲਕੁਲੇਟਰ",
        "guide_c4_desc": "ਪਾਣੀ ਬਚਾਉਣ ਵਾਲੀਆਂ ਨਵੀਆਂ ਖੇਤੀ ਤਕਨੀਕਾਂ ਅਪਣਾ ਕੇ ਵਿੱਤੀ ਅਤੇ ਬਿਜਲੀ ਬੱਚਤ ਦਾ ਅੰਦਾਜ਼ਾ ਲਗਾਓ।",
        "guide_c4_f1": "<b>ਖੇਤ ਦਾ ਆਕਾਰ:</b> ਏਕੜ (1 ਤੋਂ 50) ਸਲਾਈਡਰ ਹਿਲਾ ਕੇ ਤੁਰੰਤ ਬੱਚਤ ਦੇਖੋ।",
        "guide_c4_f2": "<b>ਤਕਨੀਕ ਤੁਲਨਾ:</b> ਝੋਨੇ ਦੀ ਸਿੱਧੀ ਬਿਜਾਈ (DSR), ਔਲਟਰਨੇਟ ਵੈਟਿੰਗ (AWD) ਅਤੇ ਤੁਪਕਾ ਸਿੰਚਾਈ ਦੀ ਤੁਲਨਾ ਕਰੋ।",
        "guide_c4_f3": "<b>ਊਰਜਾ ਬੱਚਤ:</b> ਬਚਾਈਆਂ ਗਈਆਂ ਬਿਜਲੀ ਯੂਨਿਟਾਂ (kWh) ਅਤੇ ਘਟੇ ਕਾਰਬਨ ਪ੍ਰਦੂਸ਼ਣ ਬਾਰੇ ਜਾਣੋ।",
        "guide_c4_tip": "💡 <b>ਲਾਭ:</b> ਪਾਣੀ ਬਚਾਉਣ ਵਾਲੇ ਕਿਸਾਨਾਂ ਨੂੰ ਵਾਟਰ ਪਾਸ 'ਤੇ ਵਿਸ਼ੇਸ਼ ਸਟਾਰ ਰੇਟਿੰਗ ਮਿਲਦੀ ਹੈ!",
        "guide_c5_title": "🪪 ਡਿਜੀਟਲ ਕਿਸਾਨ ਵਾਟਰ ਪਾਸ",
        "guide_c5_desc": "ਪੰਜਾਬ ਖੇਤੀ-ਜਲਵਿਗਿਆਨ ਦੁਆਰਾ ਪ੍ਰਮਾਣਿਤ ਤੁਹਾਡੀ ਅਧਿਕਾਰਤ ਡਿਜੀਟਲ ਪਛਾਣ, ਜੋ ਪਾਣੀ ਸੰਭਾਲ ਯੋਗਦਾਨ ਦਰਸਾਉਂਦੀ ਹੈ।",
        "guide_c5_f1": "<b>ਮੈਂਬਰ ਆਈਡੀ ਤੇ ਸੀਰੀਅਲ:</b> ਤੁਹਾਡੇ ਜ਼ਿਲ੍ਹੇ ਅਤੇ ਖੇਤ ਨਾਲ ਜੁੜਿਆ ਖਾਸ ਪਛਾਣ ਨੰਬਰ।",
        "guide_c5_f2": "<b>ਕੁੱਲ ਬੱਚਤ:</b> ਤੁਹਾਡੇ ਵੱਲੋਂ ਬਚਾਏ ਗਏ ਲੱਖਾਂ ਲੀਟਰ ਪਾਣੀ ਅਤੇ ਬਿਜਲੀ ਦਾ ਲਾਈਵ ਰਿਕਾਰਡ।",
        "guide_c5_f3": "<b>ਪ੍ਰਿੰਟ / ਡਾਊਨਲੋਡ:</b> ਸਰਕਾਰੀ ਸਬਸਿਡੀਆਂ ਅਤੇ ਸੋਲਰ ਟਿਊਬਵੈੱਲ ਸਕੀਮਾਂ ਲਈ ਵਾਟਰ ਪਾਸ ਡਾਊਨਲੋਡ ਕਰੋ।",
        "guide_c5_tip": "💡 <b>ਖੋਲ੍ਹਣ ਦਾ ਤਰੀਕਾ:</b> ਆਪਣਾ ਪਾਸ ਦੇਖਣ ਜਾਂ ਪ੍ਰਿੰਟ ਕਰਨ ਲਈ ਉੱਪਰ ਸੱਜੇ ਪਾਸੇ ਆਪਣੀ ਪ੍ਰੋਫਾਈਲ 'ਤੇ ਕਲਿੱਕ ਕਰੋ।",
        "guide_c6_title": "🌐 ਭਾਸ਼ਾ ਚੋਣ ਤੇ ਡਾਰਕ/ਲਾਈਟ ਮੋਡ",
        "guide_c6_desc": "ਖੇਤ ਵਿੱਚ ਧੁੱਪ ਵੇਲੇ ਜਾਂ ਦਫ਼ਤਰ ਵਿੱਚ ਵਰਤੋਂ ਲਈ ਸਕ੍ਰੀਨ ਨੂੰ ਆਪਣੀ ਮਰਜ਼ੀ ਅਨੁਸਾਰ ਸੈੱਟ ਕਰੋ।",
        "guide_c6_f1": "<b>ਭਾਸ਼ਾ ਚੋਣ:</b> ਸਾਈਨ-ਇਨ ਤੋਂ ਪਹਿਲਾਂ ਜਾਂ ਬਾਅਦ ਵਿੱਚ ਕਦੇ ਵੀ ਅੰਗਰੇਜ਼ੀ, ਹਿੰਦੀ ਜਾਂ ਪੰਜਾਬੀ ਚੁਣੋ।",
        "guide_c6_f2": "<b>ਲਾਈਟ / ਡਾਰਕ ਮੋਡ:</b> ਤੇਜ਼ ਧੁੱਪ ਲਈ ਹਾਈ-ਕੰਟ੍ਰਾਸਟ ਲਾਈਟ ਮੋਡ ਅਤੇ ਰਾਤ ਲਈ ਡਾਰਕ ਮੋਡ।",
        "guide_c6_f3": "<b>ਸੁਰੱਖਿਅਤ ਪਸੰਦ:</b> ਤੁਹਾਡੀ ਚੁਣੀ ਗਈ ਭਾਸ਼ਾ ਅਤੇ ਥੀਮ ਤੁਹਾਡੇ ਮੋਬਾਈਲ/ਕੰਪਿਊਟਰ 'ਤੇ ਹਮੇਸ਼ਾ ਯਾਦ ਰਹਿੰਦੀ ਹੈ।",
        "guide_c6_tip": "💡 <b>ਸੁਝਾਅ:</b> ਉੱਪਰਲੇ ਨੈਵੀਗੇਸ਼ਨ ਬਾਰ ਵਿੱਚ ਦਿੱਤੇ ਬਟਨਾਂ ਤੋਂ ਇੱਕ ਕਲਿੱਕ ਵਿੱਚ ਭਾਸ਼ਾ ਜਾਂ ਥੀਮ ਬਦਲੋ।",
        "mob_nav_map": "ਮਿਸ਼ਨ",
        "mob_nav_dash": "ਵਿਸ਼ਲੇਸ਼ਣ",
        "mob_nav_plan": "7-ਦਿਨ",
        "mob_nav_soil": "ਮਿੱਟੀ ਟੈਸਟ",
        "mob_nav_pass": "ਜਲ ਪਾਸ"
    }
};

function initLanguage() {
    const savedLang = localStorage.getItem("pww_lang") || "en";
    applyLanguage(savedLang);
}

function applyLanguage(lang) {
    if (!lang || !I18N_DICTIONARY[lang]) lang = "en";
    currentLang = lang;
    localStorage.setItem("pww_lang", lang);

    // Sync navbar language toggle
    document.querySelectorAll(".lang-btn").forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-lang") === lang);
    });

    // Sync pre-auth language buttons
    document.querySelectorAll(".pre-lang-btn").forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-lang") === lang);
    });

    // Apply translations to all data-i18n elements
    const dict = I18N_DICTIONARY[lang];
    if (dict) {
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (dict[key]) {
                el.innerHTML = dict[key];
            }
        });
    }

    // Translate Hotspot dropdown options
    const hotspotSelect = document.getElementById("hotspotSelect");
    if (hotspotSelect) {
        const hotspotTranslations = {
            "en": {
                "Punjab": "🌾 Punjab (India)",
                "Central Valley": "🏜️ Central Valley (USA)",
                "Nile Delta": "🌊 Nile Delta (Egypt)",
                "Murray-Darling": "🚜 Murray-Darling (Australia)",
                "Indo-Gangetic": "🏔️ Indo-Gangetic Basin (South Asia)"
            },
            "hi": {
                "Punjab": "🌾 पंजाब (भारत)",
                "Central Valley": "🏜️ सेंट्रल वैली (USA)",
                "Nile Delta": "🌊 नील डेल्टा (मिस्र)",
                "Murray-Darling": "🚜 मरे-डार्लिंग (ऑस्ट्रेलिया)",
                "Indo-Gangetic": "🏔️ सिंधु-गंगा बेसिन (दक्षिण एशिया)"
            },
            "pa": {
                "Punjab": "🌾 ਪੰਜਾਬ (ਭਾਰਤ)",
                "Central Valley": "🏜️ ਸੈਂਟਰਲ ਵੈਲੀ (USA)",
                "Nile Delta": "🌊 ਨੀਲ ਡੈਲਟਾ (ਮਿਸਰ)",
                "Murray-Darling": "🚜 ਮਰੇ-ਡਾਰਲਿੰਗ (ਆਸਟ੍ਰੇਲੀਆ)",
                "Indo-Gangetic": "🏔️ ਸਿੰਧੂ-ਗੰਗਾ ਬੇਸਿਨ (ਦੱਖਣੀ ਏਸ਼ੀਆ)"
            }
        };
        const ht = hotspotTranslations[lang] || hotspotTranslations["en"];
        Array.from(hotspotSelect.options).forEach(opt => {
            if (ht[opt.value]) opt.textContent = ht[opt.value];
        });
    }

    // Refresh district dropdown with translated names
    const currentHotspot = hotspotSelect ? hotspotSelect.value : "Punjab";
    populateHotspotDistricts(currentHotspot, currentDistrict);

    // Refresh theme text in selected language
    updateThemeButtonText();

    // Re-render current telemetry in memory if available
    if (lastTelemetryData) {
        renderTelemetry(lastTelemetryData);
    }

    // Dynamically re-translate active auth modal feedback if visible
    const regFeedback = document.getElementById("registerFeedback");
    if (regFeedback && regFeedback.style.display !== "none") {
        const email = regFeedback.getAttribute("data-email") || (document.getElementById("authEmail") ? document.getElementById("authEmail").value.trim() : "");
        if (email) {
            const fb = getRegistrationFeedbackHTML(email, lang);
            regFeedback.innerHTML = `
                <div class="feedback-title">${fb.title}</div>
                <div class="feedback-desc">${fb.desc}</div>
                <div style="margin-top:14px; text-align:center;">
                    <button type="button" class="btn-auth-primary" id="btnGoToLoginAfterReg" style="display:inline-block; width:auto; padding:10px 22px; font-size:0.88rem; background:linear-gradient(135deg, #0284C7, #0369A1); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:700;">
                        ${fb.btnText}
                    </button>
                </div>
            `;
            const btnGo = document.getElementById("btnGoToLoginAfterReg");
            if (btnGo) {
                btnGo.addEventListener("click", () => {
                    const tabLoginAuth = document.getElementById("tabLoginAuth");
                    const loginEmail = document.getElementById("loginEmail");
                    const loginPassword = document.getElementById("loginPassword");
                    const loginFeedback = document.getElementById("loginFeedback");
                    if (tabLoginAuth) tabLoginAuth.click();
                    if (loginEmail) loginEmail.value = email;
                    if (loginPassword) loginPassword.value = "";
                    if (loginFeedback) {
                        loginFeedback.style.display = "block";
                        loginFeedback.className = "auth-feedback auth-feedback-warning";
                        loginFeedback.setAttribute("data-feedback-state", "unverified");
                        loginFeedback.setAttribute("data-email", email);
                        const errs = getLoginErrorMessages(email, lang);
                        loginFeedback.innerHTML = `
                            <div class="feedback-title">${errs.unverifiedTitle}</div>
                            <div class="feedback-desc">${errs.unverifiedDesc}</div>
                        `;
                    }
                });
            }
        }
    }

    const loginFeedback = document.getElementById("loginFeedback");
    if (loginFeedback && loginFeedback.style.display !== "none") {
        const state = loginFeedback.getAttribute("data-feedback-state");
        const email = loginFeedback.getAttribute("data-email") || (document.getElementById("loginEmail") ? document.getElementById("loginEmail").value.trim() : "");
        if (state === "activated") {
            const okTitle = lang === "pa" 
                ? "✅ ਖਾਤਾ ਸਫਲਤਾਪੂਰਵਕ ਐਕਟੀਵੇਟ ਹੋ ਗਿਆ!" 
                : (lang === "hi" 
                    ? "✅ खाता सफलतापूर्वक सक्रिय (Activated) हुआ!" 
                    : "✅ Account Successfully Activated!");
            const okDesc = lang === "pa" 
                ? `ਤੁਹਾਡਾ ਕਿਸਾਨ ਖਾਤਾ <b>${email}</b> ਹੁਣ ਐਕਟੀਵੇਟ ਹੋ ਗਿਆ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਹੇਠਾਂ ਆਪਣਾ ਪਾਸਵਰਡ ਦਰਜ ਕਰਕੇ ਲੌਗਇਨ ਕਰੋ।` 
                : (lang === "hi" 
                    ? `आपका किसान खाता <b>${email}</b> अब सक्रिय हो चुका है। कृपया नीचे अपना सही पासवर्ड दर्ज करके लॉगिन करें।` 
                    : `Your farmer account <b>${email}</b> is now verified and active. Please enter your password below to sign in.`);
            loginFeedback.innerHTML = `
                <div class="feedback-title">${okTitle}</div>
                <div class="feedback-desc">${okDesc}</div>
            `;
        } else if (state) {
            const errs = getLoginErrorMessages(email, lang);
            if (state === "unverified") {
                loginFeedback.innerHTML = `
                    <div class="feedback-title">${errs.unverifiedTitle}</div>
                    <div class="feedback-desc">${errs.unverifiedDesc}</div>
                `;
            } else if (state === "invalid_pass") {
                loginFeedback.innerHTML = `
                    <div class="feedback-title">${errs.invalidPassTitle}</div>
                    <div class="feedback-desc">${errs.invalidPassDesc}</div>
                `;
            } else if (state === "not_found") {
                loginFeedback.innerHTML = `
                    <div class="feedback-title">${errs.notFoundTitle}</div>
                    <div class="feedback-desc">${errs.notFoundDesc}</div>
                `;
            }
        }
    }

    // Refresh telemetry in new language
    if (currentDistrict) {
        loadDistrictData(currentDistrict);
    }
}

// Tab navigation
function initTabs() {
    // Support footer navigation links
    document.querySelectorAll(".footer-nav").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const target = link.getAttribute("data-tab");
            switchTab(target);
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });

    // Mobile Bottom Nav buttons
    document.querySelectorAll(".mobile-nav-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            if (target) {
                switchTab(target);
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    });

    // Top Navbar Guide Button
    const navGuideBtn = document.getElementById("navGuideBtn");
    if (navGuideBtn) {
        navGuideBtn.addEventListener("click", () => {
            switchTab("tab-guide");
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Top Navbar Panchayat Leaderboard Button
    const navPanchayatBtn = document.getElementById("navPanchayatBtn");
    if (navPanchayatBtn) {
        navPanchayatBtn.addEventListener("click", () => {
            switchTab("tab-panchayat");
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }
}

// Leaflet Map setup
function initMap() {
    map = L.map("map", {
        center: [30.2110, 74.9455],
        zoom: 7,
        minZoom: 5,
        maxZoom: 18
    });

    // Base Layers
    // 1. Dark Matter (Esri World Dark Gray Canvas + City/Road Reference Labels - 100% Free, No Watermark)
    const darkMatterBase = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
        attribution: 'Tiles &copy; Esri, DeLorme, NAVTEQ',
        maxNativeZoom: 16,
        maxZoom: 18
    });
    const darkMatterRef = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", {
        attribution: 'Tiles &copy; Esri',
        maxNativeZoom: 16,
        maxZoom: 18
    });
    const darkMatter = L.layerGroup([darkMatterBase, darkMatterRef]);

    // 2. High-Res Satellite (Esri World Imagery)
    const esriSatellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
        attribution: 'Tiles &copy; Esri & NASA',
        maxNativeZoom: 18,
        maxZoom: 18
    });

    // 3. NASA GIBS Live WMTS (Suomi NPP VIIRS TrueColor Daily - Wide Swath Seamless)
    const nasaGibs = L.tileLayer("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/2024-05-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg", {
        attribution: 'NASA GIBS / Suomi NPP VIIRS',
        maxNativeZoom: 9,
        maxZoom: 18
    });

    // 4. NASA Black Marble (Earth at Night / VIIRS Night Lights)
    const nasaBlackMarble = L.tileLayer("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png", {
        attribution: 'NASA Earth Observatory / VIIRS',
        maxNativeZoom: 8,
        maxZoom: 18
    });

    // Default active layer is Dark Matter
    darkMatter.addTo(map);

    const layerMap = {
        "darkMatter": darkMatter,
        "esriSatellite": esriSatellite,
        "nasaGibs": nasaGibs,
        "nasaBlackMarble": nasaBlackMarble
    };

    // Layer control for corner
    L.control.layers({
        "🗺️ Dark Matter": darkMatter,
        "🌍 Satellite (Esri)": esriSatellite,
        "🛰️ NASA GIBS Live": nasaGibs,
        "🌌 NASA Black Marble": nasaBlackMarble
    }, null, { position: "topright" }).addTo(map);

    // Sync Toolbar Pills with Map Layer
    function switchMapBasemap(targetId) {
        Object.keys(layerMap).forEach(id => {
            if (map.hasLayer(layerMap[id])) {
                map.removeLayer(layerMap[id]);
            }
        });
        if (layerMap[targetId]) {
            layerMap[targetId].addTo(map);
        }
        document.querySelectorAll(".layer-pill-btn").forEach(btn => {
            btn.classList.toggle("active", btn.getAttribute("data-layer-id") === targetId);
        });
    }

    // Attach click events to pills
    document.querySelectorAll(".layer-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const layerId = btn.getAttribute("data-layer-id");
            switchMapBasemap(layerId);
        });
    });

    // Keep pills in sync if user changes via Leaflet native control
    map.on("baselayerchange", (e) => {
        for (const [id, lyr] of Object.entries(layerMap)) {
            if (e.layer === lyr) {
                document.querySelectorAll(".layer-pill-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.getAttribute("data-layer-id") === id);
                });
                break;
            }
        }
    });

    // Initial marker with custom styling
    marker = L.marker([30.2110, 74.9455]).addTo(map);

    // Load authentic GeoJSON district boundaries
    fetch("/api/geojson")
        .then(res => {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .catch(async () => {
            console.warn("API geojson fetch error, trying static fallback");
            const r = await fetch("data/geojson.json");
            return await r.json();
        })
        .then(data => {
            geojsonLayer = L.geoJSON(data, {
                style: feature => {
                    const color = feature.properties.color || "#10B981";
                    const isHotspot = feature.properties.name && (
                        feature.properties.name.includes("Central Valley") || 
                        feature.properties.name.includes("Nile Delta") || 
                        feature.properties.name.includes("Murray-Darling")
                    );
                    return {
                        fillColor: color,
                        weight: isHotspot ? 2.0 : 1.6,
                        opacity: 0.9,
                        color: isHotspot ? color : "#38BDF8", // Clean boundary outline matching risk tone
                        fillOpacity: isHotspot ? 0.20 : 0.35, // Natural transparency so satellite agricultural fields are crisp
                        dashArray: isHotspot ? "4, 4" : "",
                        smoothFactor: 1.2
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
    const hotspotSelect = document.getElementById("hotspotSelect");
    const districtSelect = document.getElementById("districtSelect");

    // Identify which hotspot basin owns this district
    let targetHotspot = "Punjab";
    for (const [hKey, distList] of Object.entries(HOTSPOT_DISTRICTS)) {
        if (distList.some(d => d.value === name)) {
            targetHotspot = hKey;
            break;
        }
    }

    if (hotspotSelect) {
        hotspotSelect.value = targetHotspot;
    }
    populateHotspotDistricts(targetHotspot, name);
    loadDistrictData(name);
}

// Event Listeners
function setupEventListeners() {
    // Hotspot Basin Select & Dynamic District Expansion
    const hotspotSelect = document.getElementById("hotspotSelect");
    const districtSelect = document.getElementById("districtSelect");

    if (hotspotSelect) {
        hotspotSelect.addEventListener("change", (e) => {
            const hkey = e.target.value;
            populateHotspotDistricts(hkey);
            if (districtSelect && districtSelect.value) {
                loadDistrictData(districtSelect.value);
            }
        });
    }

    if (districtSelect) {
        districtSelect.addEventListener("change", (e) => {
            loadDistrictData(e.target.value);
        });
    }

    // Language Toggle (Navbar & Pre-Auth Modal)
    document.querySelectorAll(".lang-btn, .pre-lang-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const lang = btn.getAttribute("data-lang");
            applyLanguage(lang);
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
            utter.lang = currentLang === "pa" ? "pa-IN" : (currentLang === "hi" ? "hi-IN" : "en-US");
            utter.rate = 0.95;
            window.speechSynthesis.speak(utter);
        } else {
            alert("Web Speech API not supported in this browser.");
        }
    });
}

// Static Telemetry Dataset Cache per Language
window._telemetryCacheByLang = window._telemetryCacheByLang || {};

// Load District Telemetry with Instant 2G/Offline Cache
async function loadDistrictData(district) {
    currentDistrict = district;
    const lang = (currentLang === "hi" || currentLang === "pa") ? currentLang : "en";
    let loaded = false;

    // Helper to find clean key in dataset
    function findDistrictInDataset(ds, dName) {
        if (!ds) return null;
        let clean = dName || "Bathinda";
        if (!ds[clean] && clean.includes(" - ")) {
            clean = clean.split(" - ").pop().trim();
        }
        return ds[clean] || ds[dName] || ds["Bathinda"] || Object.values(ds)[0] || null;
    }

    // 0. Zero-Latency Instant Render from Local Cache (Crucial for 2G / Offline speed)
    const localCacheKey = `pww_telemetry_${lang}`;
    try {
        if (!window._telemetryCacheByLang[lang]) {
            const raw = localStorage.getItem(localCacheKey);
            if (raw) {
                window._telemetryCacheByLang[lang] = JSON.parse(raw);
            }
        }
        if (window._telemetryCacheByLang[lang]) {
            const instantData = findDistrictInDataset(window._telemetryCacheByLang[lang], district);
            if (instantData) {
                lastTelemetryData = instantData;
                renderTelemetry(instantData);
                loaded = true;
            }
        }
    } catch (e) {}

    // 1. Background Network Sync with 5-second AbortController (prevents 2G hanging)
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
            try {
                const res = await fetch(`/api/telemetry?district=${encodeURIComponent(district)}&lang=${lang}`, { signal: controller.signal });
                if (res.ok) {
                    const data = await res.json();
                    clearTimeout(timeoutId);
                    lastTelemetryData = data;
                    renderTelemetry(data);
                    return;
                }
            } catch (apiErr) {}
        }

        // Fetch compressed static telemetry dataset
        const r = await fetch(`/data/telemetry_${lang}.json`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (r.ok) {
            const dataset = await r.json();
            window._telemetryCacheByLang[lang] = dataset;
            try {
                localStorage.setItem(localCacheKey, JSON.stringify(dataset));
            } catch (stErr) {}

            const freshData = findDistrictInDataset(dataset, district);
            if (freshData) {
                lastTelemetryData = freshData;
                renderTelemetry(freshData);
                loaded = true;
            }
        }
    } catch (netErr) {
        console.log("[PWW 2G Network Sync] Rendered from persistent offline storage.");
    }
}

// Render Telemetry Data into DOM
function renderTelemetry(data) {
    if (!data) return;
    const lang = (currentLang === "hi" || currentLang === "pa") ? currentLang : "en";

    // 1. Map Updates & Marker Popup
    if (map && marker) {
        map.flyTo([data.lat, data.lon], data.is_hotspot ? 6 : 8, { duration: 0.8 });
        marker.setLatLng([data.lat, data.lon]);
        
        const locDistrict = getLocalizedDistrictName(data.district, lang);
        const scoreLabel = lang === "pa" ? "ਤਣਾਅ ਸਕੋਰ" : (lang === "hi" ? "तनाव स्कोर" : "Stress Score");
        const centroidLabel = lang === "pa" ? "ਕੇਂਦਰ ਬਿੰਦੂ" : (lang === "hi" ? "केन्द्रक" : "Centroid");
        const zoneBadge = getZoneBadgeText(data.stress.zone, lang);

        marker.bindPopup(`
            <div class="marker-popup-card">
                <div style="font-weight:700; color:#F59E0B; font-size:1rem; margin-bottom:4px;">📍 ${locDistrict}</div>
                <div style="font-size:0.85rem; color:#E2E8F0; margin-bottom:4px;">${scoreLabel}: <b>${data.stress.score}/100</b></div>
                <div><span class="badge ${data.stress.zone === 'Red' ? 'badge-critical' : (data.stress.zone === 'Yellow' ? 'badge-warning' : 'badge-safe')}">${zoneBadge}</span></div>
                <div style="font-size:0.75rem; color:#94A3B8; margin-top:6px;">${centroidLabel}: ${data.lat.toFixed(4)}°N, ${data.lon.toFixed(4)}°E</div>
            </div>
        `);
    }

    // 2. Stress Card
    const stressScoreVal = document.getElementById("stressScoreVal");
    const stressBadge = document.getElementById("stressBadge");
    if (stressScoreVal) stressScoreVal.innerText = `${data.stress.score}/100`;
    if (stressBadge) {
        stressBadge.innerText = getZoneBadgeText(data.stress.zone, lang);
        stressBadge.className = `badge ${data.stress.zone === "Red" ? "badge-critical" : (data.stress.zone === "Yellow" ? "badge-warning" : "badge-safe")}`;
    }

    // 3. Soil Status
    const soilBadge = document.getElementById("soilBadge");
    const soilStatusText = document.getElementById("soilStatusText");
    const isAlert = Boolean(data.soil_diagnosis && data.soil_diagnosis.alert_triggered);
    if (soilBadge) {
        if (isAlert) {
            soilBadge.innerText = lang === "pa" ? "ਗੰਭੀਰ" : (lang === "hi" ? "गंभीर" : "Critical");
            soilBadge.className = "badge badge-critical";
        } else {
            soilBadge.innerText = lang === "pa" ? "ਸਰਵੋਤਮ" : (lang === "hi" ? "उत्कृष्ट" : "Optimal");
            soilBadge.className = "badge badge-safe";
        }
    }
    if (soilStatusText) {
        if (isAlert) {
            soilStatusText.innerText = lang === "pa" ? "ਚੇਤਾਵਨੀ: ਘੱਟ ਜੈਵਿਕ ਕਾਰਬਨ ਅਤੇ ਖਾਰੀਤਾ" : (lang === "hi" ? "चेतावनी: कम जैविक कार्बन एवं क्षारीयता" : "Alert: Low Organic Carbon & Alkaline");
        } else {
            soilStatusText.innerText = lang === "pa" ? "ਸਰਵੋਤਮ ਮਿੱਟੀ ਸਿਹਤ ਅਤੇ ਕਾਰਬਨ ਸੰਤੁਲਨ" : (lang === "hi" ? "उत्कृष्ट मिट्टी स्वास्थ्य एवं कार्बन संतुलन" : "Optimal Soil Health & Carbon Balance");
        }
    }

    // 4. Advisory & WhatsApp
    const advBox = document.querySelector(".advisory-box");
    if (advBox) {
        advBox.style.borderTopColor = data.stress.zone === "Red" ? "var(--critical-red)" : (data.stress.zone === "Yellow" ? "var(--accent-amber)" : "var(--safe-green)");
    }
    const advLine1 = document.getElementById("advLine1");
    const advLine2 = document.getElementById("advLine2");
    if (advLine1 && advLine2 && data.advisory) {
        advLine1.innerText = `• ${data.advisory.line1}`;
        advLine2.innerText = `• ${data.advisory.line2}`;
    }

    const waPrefix = lang === "pa" ? "🌾 ਪੰਜਾਬ ਫਾਰਮ ਵਾਟਰ ਵਾਚ ਅਲਰਟ" : (lang === "hi" ? "🌾 पंजाब फार्म वाटर वॉच अलर्ट" : "🌾 Punjab Farm Water Watch Alert");
    const waStressLabel = lang === "pa" ? "ਵਾਟਰ ਸਟ੍ਰੈਸ" : (lang === "hi" ? "जल तनाव" : "Water Stress");
    const waVerified = lang === "pa" ? "ਨਾਸਾ ਲਾਈਵ ਪ੍ਰਮਾਣਿਤ।" : (lang === "hi" ? "नासा लाइव प्रमाणित।" : "NASA Live Verified.");
    const locDistrictName = getLocalizedDistrictName(data.district, lang);
    const waMsg = `${waPrefix} - ${locDistrictName}\n${waStressLabel}: ${data.stress.score}/100 (${data.stress.zone})\n1. ${data.advisory.line1}\n2. ${data.advisory.line2}\n${waVerified}`;
    const btnWhatsApp = document.getElementById("btnWhatsApp");
    if (btnWhatsApp) {
        btnWhatsApp.href = `https://wa.me/?text=${encodeURIComponent(waMsg)}`;
    }

    // 5. Delta Cards
    const d = data.deltas;
    const agoLabel = lang === "pa" ? "30 ਦਿਨ ਪਹਿਲਾਂ" : (lang === "hi" ? "30 दिन पूर्व" : "30d Ago");
    const ptsUnit = lang === "pa" ? "ਅੰਕ" : (lang === "hi" ? "अंक" : "pts");
    const deltaSmNow = document.getElementById("deltaSmNow");
    const deltaSmSub = document.getElementById("deltaSmSub");
    if (deltaSmNow) deltaSmNow.innerHTML = `${d.sm_now} <span style="font-size:0.82rem; color:#94A3B8;">m³/m³</span>`;
    if (deltaSmSub) deltaSmSub.innerHTML = `${agoLabel}: ${d.sm_old} | <b style="color:${d.sm_diff < -0.02 ? '#DC2626' : '#16A34A'};">${d.sm_diff > 0 ? '+' : ''}${d.sm_diff}</b>`;

    const deltaNdviNow = document.getElementById("deltaNdviNow");
    const deltaNdviSub = document.getElementById("deltaNdviSub");
    if (deltaNdviNow) deltaNdviNow.innerText = d.ndvi_now;
    if (deltaNdviSub) deltaNdviSub.innerHTML = `${agoLabel}: ${d.ndvi_old} | <b style="color:${d.ndvi_diff < -0.04 ? '#DC2626' : '#16A34A'};">${d.ndvi_diff > 0 ? '+' : ''}${d.ndvi_diff}</b>`;

    const deltaScoreNow = document.getElementById("deltaScoreNow");
    const deltaScoreSub = document.getElementById("deltaScoreSub");
    if (deltaScoreNow) deltaScoreNow.innerHTML = `${d.score_now} <span style="font-size:0.82rem; color:#94A3B8;">/ 100</span>`;
    if (deltaScoreSub) deltaScoreSub.innerHTML = `${agoLabel}: ${d.score_old} | <b style="color:${d.score_diff > 5 ? '#DC2626' : '#16A34A'};">${d.score_diff > 0 ? '+' : ''}${d.score_diff} ${ptsUnit}</b>`;

    // 6. Forecast Chart & Dashboard Analytics
    renderForecastChart(data.chart_data);
    renderDashboardKPIs(data);
    renderDashboardCharts(data);

    // 7. Calendar
    renderCalendar(data.calendar_days);

    // 8. Download Dossier Button
    const btnDownload = document.getElementById("btnDownloadReport");
    if (btnDownload) {
        btnDownload.addEventListener("click", (e) => {
            e.preventDefault();
            window.print();
        });
    }

    updateCalculator();
    updateCropSimulator();
}

// Chart.js Forecast Line Chart
function renderForecastChart(chartData) {
    const canvas = document.getElementById("forecastChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (forecastChart) {
        forecastChart.destroy();
    }

    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    const textColor = isLight ? "#0F172A" : "#F1F5F9";
    const mutedColor = isLight ? "#475569" : "#94A3B8";
    const gridColor = isLight ? "rgba(0, 0, 0, 0.06)" : "rgba(255, 255, 255, 0.08)";
    const smapBorder = isLight ? "#0284C7" : "#38BDF8";
    const smapFill = isLight ? "rgba(2, 132, 199, 0.12)" : "rgba(56, 189, 248, 0.12)";
    const fcBorder = isLight ? "#D97706" : "#F59E0B";

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
                    borderColor: smapBorder,
                    backgroundColor: smapFill,
                    borderWidth: 2.5,
                    pointRadius: 0,
                    tension: 0.25,
                    fill: true
                },
                {
                    label: "7-Day Random Forest Forecast",
                    data: fcPoints,
                    borderColor: fcBorder,
                    borderWidth: 2.5,
                    borderDash: [5, 5],
                    pointRadius: 3.5,
                    pointBackgroundColor: fcBorder,
                    tension: 0.25
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: {
                        color: textColor,
                        font: { weight: "700", size: 12 },
                        boxWidth: 14,
                        padding: 12
                    }
                },
                tooltip: {
                    backgroundColor: isLight ? "rgba(255, 255, 255, 0.96)" : "rgba(7, 25, 36, 0.95)",
                    titleColor: isLight ? "#0F172A" : "#F8FAFC",
                    bodyColor: isLight ? "#334155" : "#E2E8F0",
                    borderColor: isLight ? "#CBD5E1" : "rgba(56, 189, 248, 0.3)",
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: mutedColor, maxTicksLimit: 7, font: { size: 11 } }
                },
                y: {
                    min: 0.0,
                    max: 0.65,
                    grid: { color: gridColor },
                    ticks: { color: mutedColor, font: { size: 11 } },
                    title: { display: true, text: "Soil Moisture (m³/m³)", color: mutedColor, font: { weight: "600", size: 11 } }
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
                <div style="display:flex; justify-content:space-between; margin-bottom:6px; align-items:center;">
                    <b class="calendar-title">${d.day_label}: ${d.title}</b>
                    <span class="badge" style="border:1.5px solid ${d.badge_color}; color:${d.badge_color}; background:rgba(0,0,0,0.04); font-weight:700; padding:3px 8px; border-radius:12px;">${d.badge}</span>
                </div>
                <div class="calendar-action">${d.action}</div>
                <div class="calendar-meta">Projected: <b style="color:var(--text-main);">${d.projected_sm.toFixed(3)} m³/m³</b> · Zone: <b style="color:${d.badge_color};">${d.risk_zone}</b></div>
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

// ==========================================================================
// FARMER AUTHENTICATION & DIGITAL PASS STATE MANAGEMENT
// ==========================================================================
let currentUser = null;

function initAuth() {
    try {
        const stored = localStorage.getItem("pww_user");
        if (stored) {
            currentUser = JSON.parse(stored);
        } else {
            currentUser = null; // No default hardcoded user; forces manual registration or login
        }
    } catch (e) {
        console.warn("Storage load error:", e);
        currentUser = null;
    }

    updateUserUI(currentUser);
    setupAuthListeners();

    // MANDATORY GATE: If user is not authenticated, lock the entire platform immediately
    if (!currentUser || !currentUser.email) {
        enforceAuthGate();
    } else {
        unlockAuthGate();
    }

    // Check for email verification URL parameters: ?verify_email=... and ?token=...
    const urlParams = new URLSearchParams(window.location.search);
    const verifyEmail = urlParams.get("verify_email") || (urlParams.get("verified") === "true" ? urlParams.get("email") : null);
    const token = urlParams.get("token");

    if (verifyEmail && token) {
        let isTokenValid = false;
        // STRICT PRIVACY & SECURITY: Activate ONLY if token matches the user's secret verification_token
        try {
            const localUsers = JSON.parse(localStorage.getItem("pww_local_users") || "{}");
            const lowerEmail = verifyEmail.toLowerCase();
            if (localUsers[lowerEmail] && localUsers[lowerEmail].verification_token === token) {
                localUsers[lowerEmail].is_active = true;
                localUsers[lowerEmail].email_verified = true;
                localStorage.setItem("pww_local_users", JSON.stringify(localUsers));
                isTokenValid = true;
            }
        } catch(e) {}

        // ALWAYS remove sensitive tokens from the browser URL address bar immediately
        window.history.replaceState({}, document.title, window.location.pathname);

        if (isTokenValid) {
            // Also notify backend if online
            fetch(`/api/auth/verify?email=${encodeURIComponent(verifyEmail)}&token=${encodeURIComponent(token)}`).catch(() => {});

            setTimeout(() => {
                const tabLoginAuth = document.getElementById("tabLoginAuth");
                const loginFeedback = document.getElementById("loginFeedback");
                const loginEmail = document.getElementById("loginEmail");
                const loginPassword = document.getElementById("loginPassword");

                if (tabLoginAuth) tabLoginAuth.click();
                if (loginEmail) loginEmail.value = verifyEmail;
                if (loginPassword) loginPassword.value = "";
                if (loginFeedback) {
                    loginFeedback.style.display = "block";
                    loginFeedback.className = "auth-feedback auth-feedback-success";
                    loginFeedback.setAttribute("data-feedback-state", "activated");
                    loginFeedback.setAttribute("data-email", verifyEmail);
                    const l = currentLang || "en";
                    const okTitle = l === "pa" 
                        ? "✅ ਖਾਤਾ ਸਫਲਤਾਪੂਰਵਕ ਐਕਟੀਵੇਟ ਹੋ ਗਿਆ!" 
                        : (l === "hi" 
                            ? "✅ खाता सफलतापूर्वक सक्रिय (Activated) हुआ!" 
                            : "✅ Account Successfully Activated!");
                    const okDesc = l === "pa" 
                        ? `ਤੁਹਾਡਾ ਕਿਸਾਨ ਖਾਤਾ <b>${verifyEmail}</b> ਹੁਣ ਐਕਟੀਵੇਟ ਹੋ ਗਿਆ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਹੇਠਾਂ ਆਪਣਾ ਪਾਸਵਰਡ ਦਰਜ ਕਰਕੇ ਲੌਗਇਨ ਕਰੋ।` 
                        : (l === "hi" 
                            ? `आपका किसान खाता <b>${verifyEmail}</b> अब सक्रिय हो चुका है। कृपया नीचे अपना सही पासवर्ड दर्ज करके लॉगिन करें।` 
                            : `Your farmer account <b>${verifyEmail}</b> is now verified and active. Please enter your password below to sign in.`);
                    loginFeedback.innerHTML = `
                        <div class="feedback-title">${okTitle}</div>
                        <div class="feedback-desc">${okDesc}</div>
                    `;
                }
            }, 350);
        }
    } else if (verifyEmail) {
        // Strip invalid or dangling URL parameters without activating
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

function updateUserUI(user) {
    const navAvatar = document.getElementById("navAvatar");
    const navText = document.getElementById("navProfileText");

    const drawerAvatar = document.getElementById("drawerAvatar");
    const drawerUserName = document.getElementById("drawerUserName");
    const drawerUserRole = document.getElementById("drawerUserRole");
    const drawerPassBadge = document.getElementById("drawerPassBadge");
    const drawerAuthBtnLabel = document.getElementById("drawerAuthBtnLabel");

    // Custom Avatar if uploaded, otherwise fallback to default avatar
    const userAvatarSrc = (user && user.avatar) ? user.avatar : "/default_avatar.png";

    if (user && user.email) {
        if (navAvatar) navAvatar.innerHTML = `<img src="${userAvatarSrc}" alt="Profile" class="avatar-img" style="object-fit:cover; width:100%; height:100%; border-radius:50%;">`;
        if (navText) navText.innerText = user.name || "Farmer Profile";

        if (drawerAvatar) drawerAvatar.innerHTML = `<img src="${userAvatarSrc}" alt="Profile" class="avatar-img" style="object-fit:cover; width:100%; height:100%; border-radius:50%;">`;
        if (drawerUserName) drawerUserName.innerText = user.name || "Lead Farmer";
        if (drawerUserRole) drawerUserRole.innerText = `${user.role || "Sentinel"} · ${user.district || "Punjab"}`;
        if (drawerPassBadge) {
            drawerPassBadge.innerHTML = `
                <span class="pass-chip">🛡️ Active Sentinel</span>
                <span class="pass-id" id="drawerPassId">${user.member_id || "PWW-2026-PB-0482"}</span>
            `;
        }
        if (drawerAuthBtnLabel) drawerAuthBtnLabel.innerText = "View Digital Water Pass";

        // Update Pass modal fields
        const passAvatar = document.getElementById("passAvatar");
        const passMemberId = document.getElementById("passMemberId");
        const passName = document.getElementById("passName");
        const passRole = document.getElementById("passRole");
        const passDistrict = document.getElementById("passDistrict");
        const passAcres = document.getElementById("passAcres");
        const passCrop = document.getElementById("passCrop");
        const passAuthType = document.getElementById("passAuthType");
        const passWaterSaved = document.getElementById("passWaterSaved");
        const passPowerSaved = document.getElementById("passPowerSaved");
        const passSoilGrade = document.getElementById("passSoilGrade");

        if (passAvatar) passAvatar.innerHTML = `<img src="${userAvatarSrc}" alt="Profile" class="avatar-img" style="object-fit:cover; width:100%; height:100%; border-radius:50%;">`;
        if (passMemberId) passMemberId.innerText = user.member_id || "PWW-2026-PB-0482";
        if (passName) passName.innerText = user.name;
        if (passRole) passRole.innerText = user.role || "Registered Farmer & Water Sentinel";
        if (passDistrict) passDistrict.innerText = user.district || "Bathinda";
        if (passAcres) passAcres.innerText = `${user.farm_acres} Acres`;
        if (passCrop) passCrop.innerText = user.primary_crop || "Wheat & Rice";
        if (passAuthType) passAuthType.innerText = `Punjab Ag-Stack Verified · ${user.irrigation_source || "Tubewell"}`;

        const savedMillions = ((user.water_saved_litres || 1800000) / 1000000).toFixed(2);
        if (passWaterSaved) passWaterSaved.innerText = `${savedMillions}M L`;
        if (passPowerSaved) passPowerSaved.innerText = `${(user.electricity_saved_kwh || 1420).toLocaleString()} kWh`;
        if (passSoilGrade) passSoilGrade.innerText = user.soil_health_grade || "Grade A";

        // Generate Real Scannable High-Res QR Code for Farm Verification
        const passQrImg = document.getElementById("passQrImg");
        let qrDataUrl = "/logo.png";
        if (passQrImg) {
            const memberId = user.member_id || "PWW-2026-PB-0482";
            const farmerName = user.name || "Punjab Water Sentinel";
            const district = user.district || "Bathinda";
            const waterSaved = `${savedMillions}M L`;
            const baseOrigin = window.location.origin.includes("localhost") 
                ? "https://punjab-farm-water-watch.netlify.app" 
                : window.location.origin;
            const qrData = `${baseOrigin}/verify.html?member_id=${encodeURIComponent(memberId)}&farmer=${encodeURIComponent(farmerName)}&district=${encodeURIComponent(district)}&water_saved=${encodeURIComponent(waterSaved)}&power_saved=${encodeURIComponent((user.electricity_saved_kwh || 1420) + " kWh")}&soil_grade=${encodeURIComponent(user.soil_health_grade || "Grade A")}&crop=${encodeURIComponent(user.primary_crop || "Wheat & Rice")}`;
            qrDataUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=4&data=${encodeURIComponent(qrData)}`;
            passQrImg.src = qrDataUrl;
        }

        // Also sync dedicated Farmer Identity Card Tab fields
        const tabPassAvatar = document.getElementById("tabPassAvatar");
        const tabPassMemberId = document.getElementById("tabPassMemberId");
        const tabPassName = document.getElementById("tabPassName");
        const tabPassRole = document.getElementById("tabPassRole");
        const tabPassDistrict = document.getElementById("tabPassDistrict");
        const tabPassAcres = document.getElementById("tabPassAcres");
        const tabPassCrop = document.getElementById("tabPassCrop");
        const tabPassAuthType = document.getElementById("tabPassAuthType");
        const tabPassWaterSaved = document.getElementById("tabPassWaterSaved");
        const tabPassPowerSaved = document.getElementById("tabPassPowerSaved");
        const tabPassSoilGrade = document.getElementById("tabPassSoilGrade");
        const tabPassQrImg = document.getElementById("tabPassQrImg");

        if (tabPassAvatar) tabPassAvatar.innerHTML = `<img src="${userAvatarSrc}" alt="Profile" class="avatar-img" style="object-fit:cover; width:100%; height:100%; border-radius:50%;">`;
        if (tabPassMemberId) tabPassMemberId.innerText = user.member_id || "PWW-2026-PB-0482";
        if (tabPassName) tabPassName.innerText = user.name;
        if (tabPassRole) tabPassRole.innerText = user.role || "Registered Farmer & Water Sentinel";
        if (tabPassDistrict) tabPassDistrict.innerText = user.district || "Bathinda";
        if (tabPassAcres) tabPassAcres.innerText = `${user.farm_acres} Acres`;
        if (tabPassCrop) tabPassCrop.innerText = user.primary_crop || "Wheat & Rice";
        if (tabPassAuthType) tabPassAuthType.innerText = `Punjab Ag-Stack Verified · ${user.irrigation_source || "Tubewell"}`;
        if (tabPassWaterSaved) tabPassWaterSaved.innerText = `${savedMillions}M L`;
        if (tabPassPowerSaved) tabPassPowerSaved.innerText = `${(user.electricity_saved_kwh || 1420).toLocaleString()} kWh`;
        if (tabPassSoilGrade) tabPassSoilGrade.innerText = user.soil_health_grade || "Grade A";
        if (tabPassQrImg) tabPassQrImg.src = qrDataUrl;
    } else {
        if (navAvatar) navAvatar.innerHTML = `<img src="/default_avatar.png" alt="Profile" class="avatar-img">`;
        if (navText) navText.innerText = "Sign In";

        if (drawerAvatar) drawerAvatar.innerHTML = `<img src="/default_avatar.png" alt="Profile" class="avatar-img">`;
        if (drawerUserName) drawerUserName.innerText = "Guest Farmer";
        if (drawerUserRole) drawerUserRole.innerText = "Register to unlock dossier";
        if (drawerPassBadge) {
            drawerPassBadge.innerHTML = `
                <span class="pass-chip" style="background:rgba(245,158,11,0.15); color:var(--accent-amber);">🔒 Not Registered</span>
                <span class="pass-id" id="drawerPassId">UNREGISTERED</span>
            `;
        }
        if (drawerAuthBtnLabel) drawerAuthBtnLabel.innerText = "Register / Sign In";

        // Tab card guest defaults
        const tabPassName = document.getElementById("tabPassName");
        if (tabPassName) tabPassName.innerText = "Guest Farmer (Unregistered)";
        const tabPassRole = document.getElementById("tabPassRole");
        if (tabPassRole) tabPassRole.innerText = "Register Farm to Activate Official Pass";
        const tabPassMemberId = document.getElementById("tabPassMemberId");
        if (tabPassMemberId) tabPassMemberId.innerText = "PENDING-REGISTRATION";
    }
}

// Trilingual Registration Feedback Message Builder
function getRegistrationFeedbackHTML(email, lang) {
    const l = lang || currentLang || "en";
    if (l === "pa") {
        return {
            title: "✉️ ਸੁਰੱਖਿਆ ਤਸਦੀਕ ਈਮੇਲ ਭੇਜੀ ਗਈ!",
            desc: `ਸੁਰੱਖਿਅਤ ਖਾਤਾ ਐਕਟੀਵੇਸ਼ਨ ਲਿੰਕ ਤੁਹਾਡੇ ਅਧਿਕਾਰਤ ਈਮੇਲ <b>${email}</b> 'ਤੇ ਭੇਜ ਦਿੱਤਾ ਗਿਆ ਹੈ।<br><br>🔒 <b>ਗੋਪਨੀਯਤਾ ਅਤੇ ਸੁਰੱਖਿਆ ਨਿਯਮ:</b> ਤੁਹਾਡੇ ਡੇਟਾ ਦੀ ਸੁਰੱਖਿਆ ਲਈ, ਖਾਤਾ ਕੇਵਲ ਤੁਹਾਡੀ ਨਿੱਜੀ ਈਮੇਲ ਇਨਬਾਕਸ ਵਿੱਚ ਭੇਜੇ ਗਏ ਲਿੰਕ ਤੋਂ ਹੀ ਐਕਟੀਵੇਟ ਕੀਤਾ ਜਾ ਸਕਦਾ ਹੈ।<br><br>ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ <b>ਈਮੇਲ ਇਨਬਾਕਸ</b> (ਜਾਂ ਸਪੈਮ ਫੋਲਡਰ) ਖੋਲ੍ਹੋ ਅਤੇ ਲਿੰਕ 'ਤੇ ਕਲਿੱਕ ਕਰਕੇ ਖਾਤਾ ਚਾਲੂ ਕਰੋ। ਪੁਸ਼ਟੀ ਤੋਂ ਬਾਅਦ <b>Direct Sign-In</b> ਤੋਂ ਲੌਗਇਨ ਕਰੋ।`,
            btnText: "🔑 Direct Sign-In 'ਤੇ ਜਾਓ (Go to Sign-In)"
        };
    }
    if (l === "hi") {
        return {
            title: "✉️ सुरक्षा सत्यापन ईमेल भेजा गया!",
            desc: `सत्यापन लिंक आपके आधिकारिक ईमेल <b>${email}</b> पर सफलतापूर्वक भेज दिया गया है।<br><br>🔒 <b>गोपनीयता व सुरक्षा निर्देश:</b> आपकी सुरक्षा और डेटा अखंडता के लिए, खाता केवल आपकी व्यक्तिगत ईमेल इनबॉक्स में भेजे गए सुरक्षित लिंक से ही सक्रिय किया जा सकता है।<br><br>कृपया अपना <b>ईमेल इनबॉक्स</b> (या स्पैम/जंक फ़ोल्डर) खोलें और लिंक पर क्लिक करके खाता सक्रिय करें। पुष्टि के पश्चात <b>Direct Sign-In</b> से लॉगिन करें।`,
            btnText: "🔑 Direct Sign-In पर जाएं (Go to Sign-In)"
        };
    }
    return {
        title: "✉️ Security Verification Email Dispatched!",
        desc: `A secure account activation link has been sent to your official email <b>${email}</b>.<br><br>🔒 <b>Security & Privacy Policy:</b> To protect your data and prevent unauthorized registrations, your account can only be activated by clicking the link sent directly to your private email inbox.<br><br>Please check your <b>Email Inbox</b> (or Spam folder) and click the activation link. Once verified, log in using <b>Direct Sign-In</b>.`,
        btnText: "🔑 Proceed to Direct Sign-In"
    };
}

// Trilingual Login Error Messages
function getLoginErrorMessages(email, lang) {
    const l = lang || currentLang || "en";
    if (l === "pa") {
        return {
            unverifiedTitle: "⚠️ ਖਾਤਾ ਅਜੇ ਐਕਟੀਵੇਟ ਨਹੀਂ ਹੈ (Activation Required)",
            unverifiedDesc: `ਤੁਹਾਡਾ ਕਿਸਾਨ ਖਾਤਾ ਰਜਿਸਟਰਡ ਹੈ ਪਰ ਅਜੇ ਐਕਟੀਵੇਟ ਨਹੀਂ ਹੋਇਆ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਈਮੇਲ ਇਨਬਾਕਸ (<b>${email}</b>) ਵਿੱਚ ਭੇਜੇ ਗਏ ਲਿੰਕ 'ਤੇ ਕਲਿੱਕ ਕਰਕੇ ਖਾਤਾ ਐਕਟੀਵੇਟ ਕਰੋ।`,
            invalidPassTitle: "❌ ਗਲਤ ਪਾਸਵਰਡ (Invalid Password)",
            invalidPassDesc: "ਦਰਜ ਕੀਤਾ ਗਿਆ ਪਾਸਵਰਡ ਗਲਤ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਸਹੀ ਪਾਸਵਰਡ ਦਰਜ ਕਰੋ।",
            notFoundTitle: "❌ ਖਾਤਾ ਨਹੀਂ ਮਿਲਿਆ (User Not Found)",
            notFoundDesc: `ਈਮੇਲ '<b>${email}</b>' ਰਜਿਸਟਰਡ ਨਹੀਂ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ 'New Farmer Registration' ਟੈਬ ਵਿੱਚ ਜਾ ਕੇ ਰਜਿਸਟਰ ਕਰੋ।`
        };
    }
    if (l === "hi") {
        return {
            unverifiedTitle: "⚠️ खाता अभी सक्रिय नहीं है (Activation Required)",
            unverifiedDesc: `आपका किसान खाता पंजीकृत है लेकिन अभी सक्रिय नहीं हुआ है। कृपया अपने ईमेल इनबॉक्स (<b>${email}</b>) में भेजे गए लिंक पर क्लिक करके खाता सक्रिय करें।`,
            invalidPassTitle: "❌ गलत पासवर्ड (Invalid Password)",
            invalidPassDesc: "दर्ज किया गया पासवर्ड गलत है। कृपया सही पासवर्ड प्रविष्ट करें।",
            notFoundTitle: "❌ खाता नहीं मिला (User Not Found)",
            notFoundDesc: `ईमेल '<b>${email}</b>' पंजीकृत नहीं है। कृपया पहले 'New Farmer Registration' टैब से पंजीकरण करें।`
        };
    }
    return {
        unverifiedTitle: "⚠️ Account Not Activated Yet (Activation Required)",
        unverifiedDesc: `Your farmer account is registered but pending activation. Please check your email inbox at <b>${email}</b> and click the verification link sent there before signing in.`,
        invalidPassTitle: "❌ Invalid Password",
        invalidPassDesc: "The password you entered is incorrect. Please enter the correct password.",
        notFoundTitle: "❌ Account Not Found",
        notFoundDesc: `Email '<b>${email}</b>' is not registered. Please register your farm first under 'New Farmer Registration'.`
    };
}

// Client-Side Transactional Verification Email Dispatch via EmailJS
async function sendClientVerificationEmail(email, name, verifyUrl) {
    try {
        const userLang = currentLang || "en";
        let emailMsg = "";
        if (userLang === "pa") {
            emailMsg = `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ${name || 'ਕਿਸਾਨ ਸਾਥੀ'},\n\nਪੰਜਾਬ ਫਾਰਮ ਵਾਟਰ ਵਾਚ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ।\n\nਆਪਣੇ ਖਾਤੇ ਨੂੰ ਸੁਰੱਖਿਅਤ ਢੰਗ ਨਾਲ ਐਕਟੀਵੇਟ ਕਰਨ ਲਈ ਹੇਠਾਂ ਦਿੱਤੇ ਲਿੰਕ 'ਤੇ ਕਲਿੱਕ ਕਰੋ:\n${verifyUrl}\n\nਧੰਨਵਾਦ,\nਟੀਮ ਪੰਜਾਬ ਫਾਰਮ ਵਾਟਰ ਵਾਚ`;
        } else if (userLang === "hi") {
            emailMsg = `नमस्ते ${name || 'किसान साथी'},\n\nपंजाब फार्म वाटर वॉच में आपका स्वागत है।\n\nअपने खाते को सुरक्षित रूप से सक्रिय (Activate) करने के लिए नीचे दिए गए लिंक पर क्लिक करें:\n${verifyUrl}\n\nधन्यवाद,\nटीम पंजाब फार्म वाटर वॉच`;
        } else {
            emailMsg = `Hello ${name || 'Farmer'},\n\nWelcome to Punjab Farm Water Watch.\n\nTo securely activate your farmer account and unlock NASA SMAP satellite telemetry, please click the link below:\n${verifyUrl}\n\nBest regards,\nPunjab Farm Water Watch Team`;
        }

        const payload = {
            service_id: "service_vshdx6m",
            template_id: "template_70yzbhi",
            user_id: "7QVPtO4Sw7ckfLZKe",
            template_params: {
                name: name || "Farmer",
                to_name: name || "Farmer",
                user_name: name || "Farmer",
                farmer_name: name || "Farmer",
                email: email,
                to_email: email,
                user_email: email,
                to: email,
                reply_to: "support@punjabfarms.gov.in",
                from_name: "Punjab Farm Water Watch",
                verification_link: verifyUrl,
                verify_link: verifyUrl,
                verify_url: verifyUrl,
                activation_link: verifyUrl,
                link: verifyUrl,
                url: verifyUrl,
                message: emailMsg,
                user_message: `Activation Link: ${verifyUrl}`,
                content: `Activation Link: ${verifyUrl}`,
                body: `Activation Link: ${verifyUrl}`,
                description: `Activation Link: ${verifyUrl}`,
                html_message: `<p>Activate Account:</p><p><a href="${verifyUrl}">${verifyUrl}</a></p>`,
                html: `<p>Activate Account:</p><p><a href="${verifyUrl}">${verifyUrl}</a></p>`,
                code: verifyUrl,
                token: verifyUrl,
                otp: verifyUrl
            }
        };

        const res = await fetch("https://api.emailjs.com/api/v1.0/email/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        return res.ok;
    } catch (err) {
        console.warn("[EmailJS Client Dispatch]:", err);
        return false;
    }
}

function setupAuthListeners() {
    const userProfileBtn = document.getElementById("userProfileBtn");
    const drawerAuthActionBtn = document.getElementById("drawerAuthActionBtn");
    const closeAuthModalBtn = document.getElementById("closeAuthModalBtn");
    const closeProfileModalBtn = document.getElementById("closeProfileModalBtn");
    const tabRegisterAuth = document.getElementById("tabRegisterAuth");
    const tabLoginAuth = document.getElementById("tabLoginAuth");
    const panelRegisterAuth = document.getElementById("panelRegisterAuth");
    const panelLoginAuth = document.getElementById("panelLoginAuth");
    const linkSwitchToRegister = document.getElementById("linkSwitchToRegister");
    const btnClosePassBottomBtn = document.getElementById("btnClosePassBottomBtn");
    const btnPrintPassBtn = document.getElementById("btnPrintPassBtn");
    const btnSignOutBtn = document.getElementById("btnSignOutBtn");

    if (userProfileBtn) {
        userProfileBtn.addEventListener("click", () => {
            if (currentUser && currentUser.email) {
                openProfileModal();
            } else {
                openAuthModal();
            }
        });
    }

    if (drawerAuthActionBtn) {
        drawerAuthActionBtn.addEventListener("click", () => {
            const navDrawer = document.getElementById("navDrawer");
            const drawerOverlay = document.getElementById("drawerOverlay");
            if (navDrawer) navDrawer.classList.remove("open");
            if (drawerOverlay) drawerOverlay.classList.remove("active");
            document.body.style.overflow = "";

            if (currentUser && currentUser.email) {
                openProfileModal();
            } else {
                openAuthModal();
            }
        });
    }

    if (closeAuthModalBtn) closeAuthModalBtn.addEventListener("click", closeAuthModal);
    if (closeProfileModalBtn) closeProfileModalBtn.addEventListener("click", closeProfileModal);

    // Close on backdrop click (Only allow if user is already authenticated)
    const authModal = document.getElementById("authModal");
    const profileModal = document.getElementById("profileModal");
    if (authModal) {
        authModal.addEventListener("click", (e) => {
            if (e.target === authModal && currentUser && currentUser.email) {
                closeAuthModal();
            }
        });
    }
    if (profileModal) {
        profileModal.addEventListener("click", (e) => {
            if (e.target === profileModal) closeProfileModal();
        });
    }

    // Auth Modal Tabs
    function showRegisterTab() {
        if (tabRegisterAuth) tabRegisterAuth.classList.add("active");
        if (tabLoginAuth) tabLoginAuth.classList.remove("active");
        if (panelRegisterAuth) panelRegisterAuth.style.display = "block";
        if (panelLoginAuth) panelLoginAuth.style.display = "none";
    }

    function showLoginTab() {
        if (tabLoginAuth) tabLoginAuth.classList.add("active");
        if (tabRegisterAuth) tabRegisterAuth.classList.remove("active");
        if (panelLoginAuth) panelLoginAuth.style.display = "block";
        if (panelRegisterAuth) panelRegisterAuth.style.display = "none";
    }

    if (tabRegisterAuth) tabRegisterAuth.addEventListener("click", showRegisterTab);
    if (tabLoginAuth) tabLoginAuth.addEventListener("click", showLoginTab);
    if (linkSwitchToRegister) linkSwitchToRegister.addEventListener("click", showRegisterTab);

    // Registration Form Submit
    if (panelRegisterAuth) {
        panelRegisterAuth.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById("btnRegisterSubmit");
            const feedback = document.getElementById("registerFeedback");
            if (submitBtn) submitBtn.innerHTML = `<span>⏳ Registering &amp; Validating Farm...</span>`;
            if (feedback) feedback.style.display = "none";

            const name = document.getElementById("authName") ? document.getElementById("authName").value.trim() : "Farmer";
            const email = document.getElementById("authEmail") ? document.getElementById("authEmail").value.trim() : "";
            const password = document.getElementById("authPassword") ? document.getElementById("authPassword").value.trim() : "";
            const phone = document.getElementById("authPhone") ? document.getElementById("authPhone").value.trim() : "";
            const district = document.getElementById("authDistrict") ? document.getElementById("authDistrict").value : "Bathinda";
            const farm_acres = document.getElementById("authAcres") ? parseFloat(document.getElementById("authAcres").value) : 10;
            const primary_crop = document.getElementById("authCrop") ? document.getElementById("authCrop").value : "Wheat & Rice";
            const irrigation_source = document.getElementById("authSource") ? document.getElementById("authSource").value : "Submersible Tubewell";

            // Support user avatar picture from device
            let avatarDataUrl = null;
            const avatarFileInput = document.getElementById("authAvatarFile");
            if (avatarFileInput && avatarFileInput.files && avatarFileInput.files[0]) {
                try {
                    avatarDataUrl = await new Promise((resolve) => {
                        const reader = new FileReader();
                        reader.onload = (re) => resolve(re.target.result);
                        reader.onerror = () => resolve(null);
                        reader.readAsDataURL(avatarFileInput.files[0]);
                    });
                } catch(e) {
                    console.warn("Avatar read error:", e);
                }
            }

            try {
                const res = await fetch("/api/auth/signup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name,
                        email,
                        password,
                        phone,
                        district,
                        farm_acres,
                        primary_crop,
                        irrigation_source,
                        avatar: avatarDataUrl,
                        provider: "email",
                        role: "Registered Farmer & Water Sentinel"
                    })
                });
                if (!res.ok) {
                    throw new Error("HTTP_" + res.status);
                }
                const data = await res.json();
                if (data.status === "pending_verification") {
                    const authPasswordEl = document.getElementById("authPassword");
                    if (authPasswordEl) authPasswordEl.value = "";
                    const fb = getRegistrationFeedbackHTML(email, currentLang);
                    if (feedback) {
                        feedback.style.display = "block";
                        feedback.className = "auth-feedback auth-feedback-warning";
                        feedback.setAttribute("data-email", email);
                        feedback.innerHTML = `
                            <div class="feedback-title">${fb.title}</div>
                            <div class="feedback-desc">${fb.desc}</div>
                            <div style="margin-top:14px; text-align:center;">
                                <button type="button" class="btn-auth-primary" id="btnGoToLoginFastAPI" style="display:inline-block; width:auto; padding:10px 22px; font-size:0.88rem; background:linear-gradient(135deg, #0284C7, #0369A1); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:700;">
                                    ${fb.btnText}
                                </button>
                            </div>
                        `;
                        const btnGo = document.getElementById("btnGoToLoginFastAPI");
                        if (btnGo) {
                            btnGo.addEventListener("click", () => {
                                const tabLoginAuth = document.getElementById("tabLoginAuth");
                                const loginEmail = document.getElementById("loginEmail");
                                const loginPassword = document.getElementById("loginPassword");
                                const loginFeedback = document.getElementById("loginFeedback");
                                if (tabLoginAuth) tabLoginAuth.click();
                                if (loginEmail) loginEmail.value = email;
                                if (loginPassword) loginPassword.value = "";
                                if (loginFeedback) {
                                    loginFeedback.style.display = "block";
                                    loginFeedback.className = "auth-feedback auth-feedback-warning";
                                    loginFeedback.setAttribute("data-feedback-state", "unverified");
                                    loginFeedback.setAttribute("data-email", email);
                                    const errs = getLoginErrorMessages(email, currentLang);
                                    loginFeedback.innerHTML = `
                                        <div class="feedback-title">${errs.unverifiedTitle}</div>
                                        <div class="feedback-desc">${errs.unverifiedDesc}</div>
                                    `;
                                }
                            });
                        }
                    }
                } else if (data.status === "success" && data.user) {
                    currentUser = data.user;
                    localStorage.setItem("pww_user", JSON.stringify(currentUser));
                    updateUserUI(currentUser);
                    unlockAuthGate();
                    if (currentUser.district) {
                        const select = document.getElementById("districtSelect");
                        if (select) {
                            select.value = currentUser.district;
                            loadDistrictData(currentUser.district);
                        }
                    }
                    openProfileModal();
                } else {
                    if (feedback) {
                        feedback.style.display = "block";
                        feedback.className = "auth-feedback auth-feedback-error";
                        const errHead = currentLang === "pa" ? "❌ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਅਸਫਲ" : (currentLang === "en" ? "❌ Registration Error" : "❌ पंजीकरण विफल");
                        feedback.innerHTML = `
                            <div class="feedback-title">${errHead}</div>
                            <div class="feedback-desc">${data.message || (currentLang === "pa" ? "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਵੇਰਵੇ ਜਾਂਚੋ।" : (currentLang === "en" ? "Please check your entries." : "कृपया अपनी प्रविष्टियों की जाँच करें।"))}</div>
                        `;
                    }
                }
            } catch (err) {
                console.warn("API registration failed, checking Netlify fallback:", err);
                const isNetlify = window.location.hostname.includes("netlify.app") || err.message.includes("404") || err.name === "TypeError";
                if (isNetlify) {
                    // Netlify Cloud Client-Side Registration (STRICT: Pending Activation, NO DIRECT LOGIN)
                    const token = "tok_" + Math.random().toString(36).substring(2, 15);
                    const mockUser = {
                        name: name || "Farmer",
                        email: email,
                        phone: phone || "+91 98765 43210",
                        role: "Registered Farmer & Water Sentinel",
                        district: district,
                        farm_acres: farm_acres,
                        primary_crop: primary_crop,
                        irrigation_source: irrigation_source,
                        water_saved_litres: Math.round(farm_acres * 180000),
                        electricity_saved_kwh: Math.round(farm_acres * 142),
                        soil_health_grade: "A (Verified via NASA SMAP)",
                        member_id: `PWW-2026-PB-${Math.floor(1000 + Math.random() * 9000)}`,
                        provider: "email",
                        avatar_initials: (name || "Farmer").split(" ").map(p => p[0]).join("").toUpperCase().slice(0, 2),
                        avatar: avatarDataUrl,
                        is_active: false,
                        email_verified: false,
                        verification_token: token,
                        created_at: new Date().toISOString()
                    };
                    const localUsers = JSON.parse(localStorage.getItem("pww_local_users") || "{}");
                    localUsers[email.toLowerCase()] = { ...mockUser, password };
                    localStorage.setItem("pww_local_users", JSON.stringify(localUsers));

                    // Send Real Transactional Verification Email to Farmer Inbox via EmailJS
                    const verifyUrl = `${window.location.origin}/?verify_email=${encodeURIComponent(email)}&token=${token}`;
                    sendClientVerificationEmail(email, name, verifyUrl);

                    // Clear sensitive password field
                    const authPasswordEl = document.getElementById("authPassword");
                    if (authPasswordEl) authPasswordEl.value = "";

                    // Strict Privacy & Security Display: NEVER expose activation link on public web screen!
                    if (feedback) {
                        feedback.style.display = "block";
                        feedback.className = "auth-feedback auth-feedback-warning";
                        feedback.setAttribute("data-email", email);
                        const fb = getRegistrationFeedbackHTML(email, currentLang);
                        feedback.innerHTML = `
                            <div class="feedback-title">${fb.title}</div>
                            <div class="feedback-desc">${fb.desc}</div>
                            <div style="margin-top:14px; text-align:center;">
                                <button type="button" class="btn-auth-primary" id="btnGoToLoginAfterReg" style="display:inline-block; width:auto; padding:10px 22px; font-size:0.88rem; background:linear-gradient(135deg, #0284C7, #0369A1); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:700;">
                                    ${fb.btnText}
                                </button>
                            </div>
                        `;

                        const btnGo = document.getElementById("btnGoToLoginAfterReg");
                        if (btnGo) {
                            btnGo.addEventListener("click", () => {
                                const tabLoginAuth = document.getElementById("tabLoginAuth");
                                const loginEmail = document.getElementById("loginEmail");
                                const loginPassword = document.getElementById("loginPassword");
                                const loginFeedback = document.getElementById("loginFeedback");
                                if (tabLoginAuth) tabLoginAuth.click();
                                if (loginEmail) loginEmail.value = email;
                                if (loginPassword) loginPassword.value = "";
                                if (loginFeedback) {
                                    loginFeedback.style.display = "block";
                                    loginFeedback.className = "auth-feedback auth-feedback-warning";
                                    loginFeedback.setAttribute("data-feedback-state", "unverified");
                                    loginFeedback.setAttribute("data-email", email);
                                    const errs = getLoginErrorMessages(email, currentLang);
                                    loginFeedback.innerHTML = `
                                        <div class="feedback-title">${errs.unverifiedTitle}</div>
                                        <div class="feedback-desc">${errs.unverifiedDesc}</div>
                                    `;
                                }
                            });
                        }
                    }
                    return;
                }
                if (feedback) {
                    feedback.style.display = "block";
                    feedback.className = "auth-feedback auth-feedback-error";
                    const netTitle = currentLang === "pa" ? "❌ ਨੈੱਟਵਰਕ ਸਮੱਸਿਆ (Network Error)" : (currentLang === "hi" ? "❌ नेटवर्क समस्या (Network Error)" : "❌ Network Connection Error");
                    const netDesc = currentLang === "pa" ? "ਸਰਵਰ ਨਾਲ ਸੰਪਰਕ ਨਹੀਂ ਹੋ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਇੰਟਰਨੈਟ ਕਨੈਕਸ਼ਨ ਜਾਂਚੋ।" : (currentLang === "hi" ? "सर्वर से संपर्क नहीं हो पाया। कृपया अपना इंटरनेट कनेक्शन जाँचें।" : "Unable to reach server. Please check your internet connection.");
                    feedback.innerHTML = `
                        <div class="feedback-title">${netTitle}</div>
                        <div class="feedback-desc">${netDesc}</div>
                    `;
                }
            } finally {
                if (submitBtn) submitBtn.innerHTML = `<span>Register Account &amp; Unlock Water Pass</span>`;
            }
        });
    }

    // Direct Login Form Submit
    if (panelLoginAuth) {
        panelLoginAuth.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById("btnLoginSubmit");
            const feedback = document.getElementById("loginFeedback");
            const emailInput = document.getElementById("loginEmail");
            const passwordInput = document.getElementById("loginPassword");
            const email = emailInput ? emailInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value.trim() : "";

            if (submitBtn) submitBtn.innerHTML = `<span>⏳ Verifying Credentials...</span>`;
            if (feedback) feedback.style.display = "none";

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });
                if (!res.ok) {
                    throw new Error("HTTP_" + res.status);
                }
                const data = await res.json();
                if (data.status === "success" && data.user) {
                    currentUser = data.user;
                    localStorage.setItem("pww_user", JSON.stringify(currentUser));
                    updateUserUI(currentUser);
                    unlockAuthGate();
                    if (currentUser.district) {
                        const select = document.getElementById("districtSelect");
                        if (select) {
                            select.value = currentUser.district;
                            loadDistrictData(currentUser.district);
                        }
                    }
                    openProfileModal();
                } else if (data.status === "unverified") {
                    const errs = getLoginErrorMessages(email, currentLang);
                    if (feedback) {
                        feedback.style.display = "block";
                        feedback.className = "auth-feedback auth-feedback-warning";
                        feedback.setAttribute("data-feedback-state", "unverified");
                        feedback.setAttribute("data-email", email);
                        feedback.innerHTML = `
                            <div class="feedback-title">${errs.unverifiedTitle}</div>
                            <div class="feedback-desc">${errs.unverifiedDesc}</div>
                        `;
                    }
                } else {
                    const errs = getLoginErrorMessages(email, currentLang);
                    if (feedback) {
                        feedback.style.display = "block";
                        feedback.className = "auth-feedback auth-feedback-error";
                        feedback.setAttribute("data-feedback-state", "not_found");
                        feedback.setAttribute("data-email", email);
                        feedback.innerHTML = `
                            <div class="feedback-title">${errs.notFoundTitle}</div>
                            <div class="feedback-desc">${data.message || errs.invalidPassDesc}</div>
                        `;
                    }
                }
            } catch (err) {
                console.warn("API login failed, checking Netlify fallback:", err);
                const isNetlify = window.location.hostname.includes("netlify.app") || err.message.includes("404") || err.name === "TypeError";
                if (isNetlify) {
                    const localUsers = JSON.parse(localStorage.getItem("pww_local_users") || "{}");
                    const matched = localUsers[email.toLowerCase()];
                    if (matched) {
                        if (matched.password !== password) {
                            const errs = getLoginErrorMessages(email, currentLang);
                            if (feedback) {
                                feedback.style.display = "block";
                                feedback.className = "auth-feedback auth-feedback-error";
                                feedback.setAttribute("data-feedback-state", "invalid_pass");
                                feedback.setAttribute("data-email", email);
                                feedback.innerHTML = `
                                    <div class="feedback-title">${errs.invalidPassTitle}</div>
                                    <div class="feedback-desc">${errs.invalidPassDesc}</div>
                                `;
                            }
                            return;
                        }
                        if (!matched.email_verified) {
                            const errs = getLoginErrorMessages(email, currentLang);
                            if (feedback) {
                                feedback.style.display = "block";
                                feedback.className = "auth-feedback auth-feedback-warning";
                                feedback.setAttribute("data-feedback-state", "unverified");
                                feedback.setAttribute("data-email", email);
                                feedback.innerHTML = `
                                    <div class="feedback-title">${errs.unverifiedTitle}</div>
                                    <div class="feedback-desc">${errs.unverifiedDesc}</div>
                                `;
                            }
                            return;
                        }

                        currentUser = matched;
                        localStorage.setItem("pww_user", JSON.stringify(currentUser));
                        updateUserUI(currentUser);
                        unlockAuthGate();
                        if (currentUser.district) {
                            const select = document.getElementById("districtSelect");
                            if (select) {
                                select.value = currentUser.district;
                                loadDistrictData(currentUser.district);
                            }
                        }
                        openProfileModal();
                        return;
                    }

                    // Check if it's the verified official demo steward account
                    if (email.toLowerCase() === "arnav@punjabfarms.gov.in" && password === "arnav1234") {
                        const stewardUser = {
                            name: "Arnav Sharma",
                            email: "arnav@punjabfarms.gov.in",
                            phone: "+91 98765 43210",
                            role: "Lead Farmer & Water Steward",
                            district: "Bathinda",
                            farm_acres: 12.5,
                            primary_crop: "Wheat & Direct Seeded Rice (DSR)",
                            irrigation_source: "Solar-Assisted Submersible Tubewell",
                            water_saved_litres: 2250000,
                            electricity_saved_kwh: 1775,
                            soil_health_grade: "A (Optimized)",
                            member_id: "PWW-2026-PB-0482",
                            provider: "email",
                            avatar_initials: "AS",
                            is_active: true,
                            email_verified: true,
                            created_at: "2026-11-14T16:11:20.076868"
                        };
                        currentUser = stewardUser;
                        localStorage.setItem("pww_user", JSON.stringify(currentUser));
                        updateUserUI(currentUser);
                        unlockAuthGate();
                        if (currentUser.district) {
                            const select = document.getElementById("districtSelect");
                            if (select) {
                                select.value = currentUser.district;
                                loadDistrictData(currentUser.district);
                            }
                        }
                        openProfileModal();
                        return;
                    }

                    // Strict rejection: Random credentials or incorrect password NEVER log in!
                    const errs = getLoginErrorMessages(email, currentLang);
                    if (feedback) {
                        feedback.style.display = "block";
                        feedback.className = "auth-feedback auth-feedback-error";
                        feedback.setAttribute("data-feedback-state", "not_found");
                        feedback.setAttribute("data-email", email);
                        feedback.innerHTML = `
                            <div class="feedback-title">${errs.notFoundTitle}</div>
                            <div class="feedback-desc">${errs.notFoundDesc}</div>
                        `;
                    }
                    return;
                }
                if (feedback) {
                    feedback.style.display = "block";
                    feedback.className = "auth-feedback auth-feedback-error";
                    const netTitle = currentLang === "pa" ? "❌ ਨੈੱਟਵਰਕ ਸਮੱਸਿਆ (Network Error)" : (currentLang === "hi" ? "❌ नेटवर्क समस्या (Network Error)" : "❌ Network Connection Error");
                    const netDesc = currentLang === "pa" ? "ਸਰਵਰ ਨਾਲ ਸੰਪਰਕ ਨਹੀਂ ਹੋ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਇੰਟਰਨੈਟ ਕਨੈਕਸ਼ਨ ਜਾਂਚੋ।" : (currentLang === "hi" ? "सर्वर से संपर्क नहीं हो पाया। कृपया अपना इंटरनेट कनेक्शन जाँचें।" : "Unable to reach server. Please check your internet connection.");
                    feedback.innerHTML = `
                        <div class="feedback-title">${netTitle}</div>
                        <div class="feedback-desc">${netDesc}</div>
                    `;
                }
            } finally {
                if (submitBtn) submitBtn.innerHTML = `<span>Direct Sign-In to Farm Account</span>`;
            }
        });
    }

    // Close Pass to explore platform
    if (btnClosePassBottomBtn) {
        btnClosePassBottomBtn.addEventListener("click", () => {
            closeProfileModal();
        });
    }

    // Print / Download Pass
    if (btnPrintPassBtn) {
        btnPrintPassBtn.addEventListener("click", () => {
            window.print();
        });
    }

    const btnPrintTabPassBtn = document.getElementById("btnPrintTabPassBtn");
    if (btnPrintTabPassBtn) {
        btnPrintTabPassBtn.addEventListener("click", () => {
            window.print();
        });
    }

    const btnManageTabPassBtn = document.getElementById("btnManageTabPassBtn");
    if (btnManageTabPassBtn) {
        btnManageTabPassBtn.addEventListener("click", () => {
            if (currentUser && currentUser.email) {
                openManageProfileModal();
            } else {
                openAuthModal();
            }
        });
    }

    const btnEditProfileFromPass = document.getElementById("btnEditProfileFromPass");
    if (btnEditProfileFromPass) {
        btnEditProfileFromPass.addEventListener("click", () => {
            closeProfileModal();
            openManageProfileModal();
        });
    }

    const closeManageProfileModalBtn = document.getElementById("closeManageProfileModalBtn");
    const btnCancelManageProfile = document.getElementById("btnCancelManageProfile");
    const manageProfileModal = document.getElementById("manageProfileModal");

    if (closeManageProfileModalBtn) closeManageProfileModalBtn.addEventListener("click", closeManageProfileModal);
    if (btnCancelManageProfile) btnCancelManageProfile.addEventListener("click", closeManageProfileModal);
    if (manageProfileModal) {
        manageProfileModal.addEventListener("click", (e) => {
            if (e.target === manageProfileModal) closeManageProfileModal();
        });
    }

    const manageAvatarInput = document.getElementById("manageAvatarInput");
    const manageAvatarPreview = document.getElementById("manageAvatarPreview");
    const btnRemoveManageAvatar = document.getElementById("btnRemoveManageAvatar");

    if (manageAvatarInput && manageAvatarPreview) {
        manageAvatarInput.addEventListener("change", () => {
            if (manageAvatarInput.files && manageAvatarInput.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    manageAvatarPreview.src = e.target.result;
                    manageAvatarPreview.dataset.newAvatar = e.target.result;
                };
                reader.readAsDataURL(manageAvatarInput.files[0]);
            }
        });
    }

    if (btnRemoveManageAvatar && manageAvatarPreview) {
        btnRemoveManageAvatar.addEventListener("click", () => {
            manageAvatarPreview.src = "/default_avatar.png";
            manageAvatarPreview.dataset.newAvatar = "";
            if (manageAvatarInput) manageAvatarInput.value = "";
        });
    }

    const formManageProfile = document.getElementById("formManageProfile");
    if (formManageProfile) {
        formManageProfile.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!currentUser) return;

            const nameInput = document.getElementById("manageNameInput");
            const districtSelect = document.getElementById("manageDistrictSelect");
            const phoneInput = document.getElementById("managePhoneInput");
            const acresInput = document.getElementById("manageAcresInput");
            const cropSelect = document.getElementById("manageCropSelect");
            const sourceSelect = document.getElementById("manageSourceSelect");
            const preview = document.getElementById("manageAvatarPreview");
            const feedback = document.getElementById("manageProfileFeedback");

            if (nameInput) currentUser.name = nameInput.value.trim();
            if (districtSelect) currentUser.district = districtSelect.value;
            if (phoneInput) currentUser.phone = phoneInput.value.trim();
            if (acresInput) {
                const ac = parseFloat(acresInput.value) || 10;
                currentUser.farm_acres = ac;
                currentUser.water_saved_litres = Math.round(ac * 180000);
                currentUser.electricity_saved_kwh = Math.round(ac * 142);
            }
            if (cropSelect) currentUser.primary_crop = cropSelect.value;
            if (sourceSelect) currentUser.irrigation_source = sourceSelect.value;

            if (preview && preview.dataset.newAvatar !== undefined) {
                currentUser.avatar = preview.dataset.newAvatar || null;
            }

            // Save to localStorage
            localStorage.setItem("pww_user", JSON.stringify(currentUser));
            try {
                const localUsers = JSON.parse(localStorage.getItem("pww_local_users") || "{}");
                if (currentUser.email && localUsers[currentUser.email.toLowerCase()]) {
                    localUsers[currentUser.email.toLowerCase()] = {
                        ...localUsers[currentUser.email.toLowerCase()],
                        ...currentUser
                    };
                    localStorage.setItem("pww_local_users", JSON.stringify(localUsers));
                }
            } catch(err) {}

            // Update UI across all tabs, modals, and QR codes
            updateUserUI(currentUser);

            // Synchronize map telemetry if district was changed
            if (currentUser.district) {
                const mainDistrictSelect = document.getElementById("districtSelect");
                if (mainDistrictSelect) {
                    mainDistrictSelect.value = currentUser.district;
                    loadDistrictData(currentUser.district);
                }
            }

            if (feedback) {
                feedback.style.display = "block";
                feedback.className = "auth-feedback auth-feedback-success";
                feedback.innerHTML = `
                    <div class="feedback-title">✅ प्रोफाइल सफलतापूर्वक अपडेट हुई!</div>
                    <div class="feedback-desc">आपकी प्रोफाइल फोटो, स्थान और विवरण डिजिटल वाटर पास और सभी टैब्स में अपडेट कर दिए गए हैं।</div>
                `;
            }

            setTimeout(() => {
                closeManageProfileModal();
            }, 800);
        });
    }

    // Sign Out
    if (btnSignOutBtn) {
        btnSignOutBtn.addEventListener("click", () => {
            localStorage.removeItem("pww_user");
            currentUser = null;
            updateUserUI(null);
            closeProfileModal();
            enforceAuthGate(); // Immediately lock platform again!
        });
    }
}

function enforceAuthGate() {
    const modal = document.getElementById("authModal");
    const closeBtn = document.getElementById("closeAuthModalBtn");
    if (modal) {
        modal.classList.add("mandatory-lock");
        modal.style.display = "flex";
    }
    if (closeBtn) closeBtn.style.display = "none";
    document.body.classList.add("auth-locked");
}

function unlockAuthGate() {
    const modal = document.getElementById("authModal");
    const closeBtn = document.getElementById("closeAuthModalBtn");
    if (modal) {
        modal.classList.remove("mandatory-lock");
        modal.style.display = "none";
    }
    if (closeBtn) closeBtn.style.display = "";
    document.body.classList.remove("auth-locked");
}

function openAuthModal() {
    const modal = document.getElementById("authModal");
    if (modal) {
        if (!currentUser || !currentUser.email) {
            enforceAuthGate();
        } else {
            modal.style.display = "flex";
            const closeBtn = document.getElementById("closeAuthModalBtn");
            if (closeBtn) closeBtn.style.display = "";
        }
    }
}

function closeAuthModal() {
    if (!currentUser || !currentUser.email) {
        return; // Cannot dismiss without logging in!
    }
    unlockAuthGate();
}

function openProfileModal() {
    if (currentUser) updateUserUI(currentUser);
    const modal = document.getElementById("profileModal");
    if (modal) modal.style.display = "flex";
}

function closeProfileModal() {
    const modal = document.getElementById("profileModal");
    if (modal) modal.style.display = "none";
}

function openManageProfileModal() {
    if (!currentUser || !currentUser.email) {
        openAuthModal();
        return;
    }
    const modal = document.getElementById("manageProfileModal");
    if (!modal) return;

    const nameInput = document.getElementById("manageNameInput");
    const districtSelect = document.getElementById("manageDistrictSelect");
    const phoneInput = document.getElementById("managePhoneInput");
    const acresInput = document.getElementById("manageAcresInput");
    const cropSelect = document.getElementById("manageCropSelect");
    const sourceSelect = document.getElementById("manageSourceSelect");
    const preview = document.getElementById("manageAvatarPreview");
    const feedback = document.getElementById("manageProfileFeedback");

    if (nameInput) nameInput.value = currentUser.name || "";
    if (districtSelect) districtSelect.value = currentUser.district || "Bathinda";
    if (phoneInput) phoneInput.value = currentUser.phone || "";
    if (acresInput) acresInput.value = currentUser.farm_acres || 10;
    if (cropSelect) cropSelect.value = currentUser.primary_crop || "Wheat & Direct Seeded Rice (DSR)";
    if (sourceSelect) sourceSelect.value = currentUser.irrigation_source || "Deep Submersible Tubewell";
    if (preview) {
        preview.src = currentUser.avatar || "/default_avatar.png";
        preview.dataset.newAvatar = currentUser.avatar || "";
    }
    if (feedback) feedback.style.display = "none";

    modal.style.display = "flex";
}

function closeManageProfileModal() {
    const modal = document.getElementById("manageProfileModal");
    if (modal) modal.style.display = "none";
}

// ==========================================
// GRAM PANCHAYAT WATER CREDIT LEADERBOARD
// ==========================================

function filterAndSortPanchayatTable() {
    const districtSelect = document.getElementById("panchayatDistrictSelect");
    const sortSelect = document.getElementById("panchayatSortSelect");
    const searchInput = document.getElementById("panchayatSearchInput");
    const tbody = document.getElementById("panchayatTableBody");
    if (!tbody) return;

    const selectedDistrict = districtSelect ? districtSelect.value : "ALL";
    const sortKey = sortSelect ? sortSelect.value : "credits";
    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

    const rows = Array.from(tbody.querySelectorAll("tr:not(.empty-state-row)"));

    // Filter by district and search text
    rows.forEach(row => {
        const rowDistrict = row.getAttribute("data-district") || "";
        const rowText = row.innerText.toLowerCase();
        const matchesDistrict = (selectedDistrict === "ALL" || rowDistrict.toLowerCase() === selectedDistrict.toLowerCase());
        const matchesQuery = (!query || rowText.includes(query));

        if (matchesDistrict && matchesQuery) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });

    // Sort rows (both visible & hidden, maintaining overall relative ranking)
    rows.sort((a, b) => {
        const valA = parseFloat(a.getAttribute(`data-${sortKey}`) || 0);
        const valB = parseFloat(b.getAttribute(`data-${sortKey}`) || 0);
        return valB - valA; // Descending
    });

    // Re-append to tbody in sorted order
    rows.forEach(r => tbody.appendChild(r));

    // Dynamic rank badge assignment for visible rows
    const visibleRows = rows.filter(r => r.style.display !== "none");
    visibleRows.forEach((row, idx) => {
        const firstTd = row.querySelector("td");
        if (!firstTd) return;
        const rank = idx + 1;
        if (rank === 1) {
            firstTd.innerHTML = `<span class="rank-badge rank-1">🏆 #1</span>`;
        } else if (rank === 2) {
            firstTd.innerHTML = `<span class="rank-badge rank-2">🥇 #2</span>`;
        } else if (rank === 3) {
            firstTd.innerHTML = `<span class="rank-badge rank-3">🥈 #3</span>`;
        } else {
            firstTd.innerHTML = `<span class="rank-badge rank-other">#${rank}</span>`;
        }
    });

    // Handle Empty State
    let emptyRow = tbody.querySelector(".empty-state-row");
    if (visibleRows.length === 0) {
        if (!emptyRow) {
            emptyRow = document.createElement("tr");
            emptyRow.className = "empty-state-row";
            emptyRow.innerHTML = `<td colspan="8" style="text-align:center; padding:24px; color:var(--text-muted); font-size:0.88rem;">🔍 No Gram Panchayats found matching your search. Try selecting "All Punjab Districts" or clearing your search keywords.</td>`;
            tbody.appendChild(emptyRow);
        }
        emptyRow.style.display = "";
    } else if (emptyRow) {
        emptyRow.style.display = "none";
    }
}

function updatePanchayatSimulator() {
    const acresSlider = document.getElementById("panchayatSimAcres");
    const dsrSlider = document.getElementById("panchayatSimDsr");
    const acresVal = document.getElementById("panchayatSimAcresVal");
    const dsrVal = document.getElementById("panchayatSimDsrVal");
    const outWater = document.getElementById("simOutWater");
    const outCredits = document.getElementById("simOutCredits");
    const outGrant = document.getElementById("simOutGrant");
    const outDelta = document.getElementById("simOutDelta");

    if (!acresSlider || !dsrSlider) return;

    const acres = parseInt(acresSlider.value, 10) || 2500;
    const dsr = parseInt(dsrSlider.value, 10) || 65;

    if (acresVal) acresVal.innerText = acres.toLocaleString() + " Acres";
    if (dsrVal) dsrVal.innerText = dsr + "%";

    // Standardized conversion: 180,000 Litres saved per acre under Direct Seeded Rice (DSR)
    const effectiveAcres = acres * (dsr / 100);
    const waterSavedL = effectiveAcres * 180000;
    const pwcCredits = Math.round(waterSavedL / 100000); // 1 PWC = 100,000 L
    const waterSavedM = (waterSavedL / 1000000).toFixed(1) + "M L";

    // State Capital Grant Tiers under Punjab Rural Development Gram Nidhi
    let grant = "₹5.0 Lakhs";
    if (pwcCredits >= 3500) {
        grant = "₹15.0 Lakhs";
    } else if (pwcCredits >= 2500) {
        grant = "₹10.0 Lakhs";
    } else if (pwcCredits >= 1500) {
        grant = "₹6.5 Lakhs";
    }

    // Hydrologic aquifer water table recovery coefficient (cm/year)
    const delta = "+" + (effectiveAcres * 0.0054).toFixed(1) + " cm/yr";

    if (outWater) outWater.innerText = waterSavedM;
    if (outCredits) outCredits.innerText = pwcCredits.toLocaleString() + " PWC";
    if (outGrant) outGrant.innerText = grant;
    if (outDelta) outDelta.innerText = delta;
}

function initPanchayatLeaderboard() {
    const districtSelect = document.getElementById("panchayatDistrictSelect");
    const sortSelect = document.getElementById("panchayatSortSelect");
    const searchInput = document.getElementById("panchayatSearchInput");
    const acresSlider = document.getElementById("panchayatSimAcres");
    const dsrSlider = document.getElementById("panchayatSimDsr");

    if (districtSelect) districtSelect.addEventListener("change", filterAndSortPanchayatTable);
    if (sortSelect) sortSelect.addEventListener("change", filterAndSortPanchayatTable);
    if (searchInput) searchInput.addEventListener("input", filterAndSortPanchayatTable);

    if (acresSlider) acresSlider.addEventListener("input", updatePanchayatSimulator);
    if (dsrSlider) dsrSlider.addEventListener("input", updatePanchayatSimulator);

    filterAndSortPanchayatTable();
    updatePanchayatSimulator();
}
