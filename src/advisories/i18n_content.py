"""
Trilingual Localization Strings (English, Hindi, Punjabi) for Punjab Farm Water Watch.
Ensures zero language barrier for local agricultural producers across Punjab.
"""

I18N = {
    "en": {
        "title": "Punjab Farm Water Watch",
        "subtitle": "Water Scarcity & Soil-Quality Early Warning System powered by NASA Earth Observations",
        "team_credit": "NASA Space Apps Challenge 2026 · Team The SMAP Squad",
        "district_select": "Select Monitoring District",
        "pin_drop_title": "Interactive Pin-Drop Field Query",
        "pin_drop_instruct": "Click anywhere on the satellite map to query field-specific soil moisture & water stress.",
        "kpi_stress_score": "Water Stress Score",
        "kpi_smap_moisture": "SMAP Rootzone Soil Moisture",
        "kpi_30d_rain": "30-Day Cumulative Rain",
        "kpi_et_loss": "MODIS Evapotranspiration",
        "kpi_soil_health": "Soil Quality Diagnostics",
        "zone_green": "Low Water Stress (Safe)",
        "zone_yellow": "Moderate Stress (Conserve)",
        "zone_red": "High Scarcity (Urgent Action)",
        "anomaly_alert": "Hidden Soil-Quality Alert",
        "anomaly_normal": "Optimal Soil & Water Balance",
        "advisory_header": "Field-Level Actionable Advisories",
        "forecast_header": "7-Day Machine Learning Predictive Forecast",
        "history_slider": "30-Day Multi-Satellite Observation Timeline",
        "data_provenance": "NASA Data Stack & Provenance",
        "advisories": {
            "SAFE": [
                "Water reserves are currently sufficient for crop demand.",
                "Avoid unnecessary over-irrigation to conserve regional groundwater.",
                "Ensure proper field drainage to prevent root-zone hypoxia in low-lying patches."
            ],
            "CAUTION": [
                "Moderate moisture deficit detected in the rootzone.",
                "Delay flood irrigation by 2-3 days if light rain is forecast.",
                "Adopt straw mulching to curb high surface evapotranspiration losses.",
                "Inspect tubewell electricity schedules to optimize pump run-time."
            ],
            "CRITICAL": [
                "Severe moisture deficit! Immediate water conservation protocols required.",
                "Adopt Direct Seeded Rice (DSR) or alternate wetting and drying (AWD) immediately.",
                "Prioritize evening irrigation to reduce midday evaporative loss.",
                "Apply paddy straw mulching at 2-3 tonnes/acre to preserve remaining subsoil water."
            ]
        }
    },
    "hi": {
        "title": "पंजाब फार्म वाटर वॉच (Punjab Farm Water Watch)",
        "subtitle": "नासा (NASA) उपग्रह डेटा द्वारा संचालित जल संकट एवं मृदा-गुणवत्ता पूर्व चेतावनी प्रणाली",
        "team_credit": "नासा स्पेस ऐप्स चैलेंज 2026 · टीम द स्मैप स्क्वाड (The SMAP Squad)",
        "district_select": "निगरानी जिला चुनें",
        "pin_drop_title": "इंटरएक्टिव पिन-ड्रॉप खेत जांच (Pin-Drop)",
        "pin_drop_instruct": "खेत की नमी और जल संकट की जांच के लिए उपग्रह मानचित्र पर कहीं भी क्लिक करें।",
        "kpi_stress_score": "जल तनाव स्कोर (0-100)",
        "kpi_smap_moisture": "स्मैप (SMAP) जड़-क्षेत्र मृदा नमी",
        "kpi_30d_rain": "30-दिनों की कुल बारिश",
        "kpi_et_loss": "फसल वाष्पीकरण दर (ET)",
        "kpi_soil_health": "मृदा गुणवत्ता स्थिति",
        "zone_green": "सामान्य / सुरक्षित जल स्तर",
        "zone_yellow": "मध्यम जल संकट (सावधानी)",
        "zone_red": "गंभीर जल संकट (तत्काल कार्रवाई)",
        "anomaly_alert": "छिपी हुई मिट्टी की खराबी का अलर्ट",
        "anomaly_normal": "संतुलित मिट्टी और जल स्वास्थ्य",
        "advisory_header": "किसानों के लिए जरूरी सलाह",
        "forecast_header": "7-दिवसीय मशीन लर्निंग पूर्वानुमान",
        "history_slider": "30-दिनों का उपग्रह अवलोकन इतिहास",
        "data_provenance": "नासा डेटा स्रोत एवं प्रमाणिकता",
        "advisories": {
            "SAFE": [
                "फसल की मांग के लिए पानी पर्याप्त है।",
                "भूजल बचाने के लिए अतिरिक्त सिंचाई से बचें।",
                "निचले खेतों में जलभराव रोकने के लिए जल निकासी की व्यवस्था रखें।"
            ],
            "CAUTION": [
                "जड़-क्षेत्र में नमी की मध्यम कमी देखी गई है।",
                "यदि बारिश की संभावना हो तो सिंचाई 2-3 दिन टालें।",
                "वाष्पीकरण रोकने के लिए खेत में पुआल की मल्चिंग (Mulching) करें।",
                "बिजली शेड्यूल के अनुसार ही ट्यूबवेल चलाएं।"
            ],
            "CRITICAL": [
                "किसान भाई, 3 दिन पानी रोक दो ('Kisan bhai, 3 din paani rok do') - यदि हल्की बारिश या नहर का पानी आने वाला हो।",
                "धान में सीधी बिजाई (DSR) या बारी-बारी सुखाने व सींचने की विधि अपनाएं, जिससे 25% पानी बचता है।",
                "दोपहर के बजाय शाम को सिंचाई करें ताकि पानी भाप बनकर न उड़े।",
                "मिट्टी की नमी बचाने के लिए 2-3 टन प्रति एकड़ पुआल/फसल अवशेष की मल्चिंग (Mulching) करें।"
            ]
        }
    },
    "pa": {
        "title": "ਪੰਜਾਬ ਫਾਰਮ ਵਾਟਰ ਵਾਚ (Punjab Farm Water Watch)",
        "subtitle": "ਨਾਸਾ (NASA) ਉਪਗ੍ਰਹਿ ਡਾਟੇ 'ਤੇ ਅਧਾਰਤ ਪਾਣੀ ਦੀ ਘਾਟ ਅਤੇ ਮਿੱਟੀ ਦੀ ਪਰਖ ਪ੍ਰਣਾਲੀ",
        "team_credit": "ਨਾਸਾ ਸਪੇਸ ਐਪਸ ਚੈਲੇਂਜ 2026 · ਟੀਮ ਦ ਸਮੈਪ ਸਕੁਐਡ (The SMAP Squad)",
        "district_select": "ਜ਼ਿਲ੍ਹਾ ਚੁਣੋ",
        "pin_drop_title": "ਪਿੰਨ-ਡ੍ਰੌਪ ਖੇਤ ਪਰਖ (Pin-Drop Query)",
        "pin_drop_instruct": "ਖੇਤ ਵਿੱਚ ਨਮੀ ਅਤੇ ਪਾਣੀ ਦੇ ਤਣਾਅ ਦੀ ਜਾਂਚ ਲਈ ਨਕਸ਼ੇ 'ਤੇ ਕਿਤੇ ਵੀ ਕਲਿੱਕ ਕਰੋ।",
        "kpi_stress_score": "ਪਾਣੀ ਦੀ ਘਾਟ ਦਾ ਸਕੋਰ (0-100)",
        "kpi_smap_moisture": "SMAP ਜੜ੍ਹ-ਖੇਤਰ ਮਿੱਟੀ ਨਮੀ",
        "kpi_30d_rain": "30 ਦਿਨਾਂ ਦੀ ਕੁੱਲ ਬਾਰਿਸ਼",
        "kpi_et_loss": "ਫਸਲ ਦਾ ਪਾਣੀ ਵਾਸ਼ਪੀਕਰਨ (ET)",
        "kpi_soil_health": "ਮਿੱਟੀ ਦੀ ਗੁਣਵੱਤਾ ਸਥਿਤੀ",
        "zone_green": "ਸੁਰੱਖਿਅਤ / ਪਾਣੀ ਦੀ ਕੋਈ ਘਾਟ ਨਹੀਂ",
        "zone_yellow": "ਦਰਮਿਆਨੀ ਘਾਟ (ਪਾਣੀ ਬਚਾਓ)",
        "zone_red": "ਗੰਭੀਰ ਪਾਣੀ ਸੰਕਟ (ਤੁਰੰਤ ਕਦਮ ਚੁੱਕੋ)",
        "anomaly_alert": "ਮਿੱਟੀ ਦੀ ਖ਼ਰਾਬੀ ਦਾ ਗੁਪਤ ਅਲਰਟ",
        "anomaly_normal": "ਮਿੱਟੀ ਅਤੇ ਪਾਣੀ ਦੀ ਵਧੀਆ ਸਥਿਤੀ",
        "advisory_header": "ਕਿਸਾਨਾਂ ਲਈ ਜ਼ਰੂਰੀ ਸਲਾਹ",
        "forecast_header": "7 ਦਿਨਾਂ ਦਾ ਮਸ਼ੀਨ ਲਰਨਿੰਗ ਭਵਿੱਖਬਾਣੀ ਅੰਦਾਜ਼ਾ",
        "history_slider": "30 ਦਿਨਾਂ ਦਾ ਉਪਗ੍ਰਹਿ ਨਿਰੀਖਣ ਰਿਕਾਰਡ",
        "data_provenance": "ਨਾਸਾ ਡਾਟਾ ਸਰੋਤ ਅਤੇ ਪਾਰਦਰਸ਼ਤਾ",
        "advisories": {
            "SAFE": [
                "ਫਸਲ ਲਈ ਮਿੱਟੀ ਵਿੱਚ ਪਾਣੀ ਕਾਫੀ ਹੈ।",
                "ਜ਼ਮੀਨੀ ਪਾਣੀ ਬਚਾਉਣ ਲਈ ਬੇਲੋੜੀ ਸਿੰਚਾਈ ਨਾ ਕਰੋ।",
                "ਨੀਵੇਂ ਖੇਤਾਂ ਵਿੱਚ ਪਾਣੀ ਖੜ੍ਹਨ ਤੋਂ ਰੋਕਣ ਲਈ ਨਿਕਾਸੀ ਦਾ ਪ੍ਰਬੰਧ ਰੱਖੋ।"
            ],
            "CAUTION": [
                "ਜੜ੍ਹਾਂ ਵਿੱਚ ਨਮੀ ਦੀ ਕਮੀ ਦੇਖੀ ਗਈ ਹੈ।",
                "ਜੇਕਰ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਹੋਵੇ ਤਾਂ ਪਾਣੀ ਲਾਉਣਾ 2-3 ਦਿਨ ਟਾਲੋ।",
                "ਵਾਸ਼ਪੀਕਰਨ ਘਟਾਉਣ ਲਈ ਖੇਤ ਵਿੱਚ ਪਰਾਲੀ ਦੀ ਮਲਚਿੰਗ (Mulching) ਕਰੋ।"
            ],
            "CRITICAL": [
                "ਪਾਣੀ ਦੀ ਭਾਰੀ ਕਿੱਲਤ! ਤੁਰੰਤ ਪਾਣੀ ਬਚਾਉਣ ਦੇ ਤਰੀਕੇ ਅਪਣਾਓ।",
                "ਝੋਨੇ ਦੀ ਸਿੱਧੀ ਬਿਜਾਈ (DSR) ਜਾਂ ਤਰ-ਵੱਤਰ ਵਿਧੀ ਦੀ ਵਰਤੋਂ ਕਰੋ।",
                "ਸਿੰਚਾਈ ਹਮੇਸ਼ਾ ਸ਼ਾਮ ਵੇਲੇ ਕਰੋ ਤਾਂ ਜੋ ਪਾਣੀ ਉੱਡ ਨਾ ਜਾਵੇ।",
                "ਜ਼ਮੀਨ ਵਿੱਚ ਸਿੱਲ੍ਹ ਬਚਾਉਣ ਲਈ 2-3 ਟਨ ਪ੍ਰਤੀ ਏਕੜ ਪਰਾਲੀ ਵਿਛਾਓ।"
            ]
        }
    }
}
