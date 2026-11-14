"""
7-Day Smart Farm Action Calendar Generator for Punjab Farm Water Watch.
Translates RandomForest soil moisture projections and soil quality anomaly detection
into a day-by-day precision agronomic workflow across English, Hindi, and Punjabi.
"""

def generate_smart_calendar(forecast_results, soil_anomaly_res, lang="en"):
    """
    Generates a structured 7-day action calendar based on:
    1. Projected soil moisture & risk zone for each day.
    2. Soil quality degradation alerts (alkalinity/salinity/carbon).
    3. Trilingual localization (en, hi, pa).
    """
    calendar_days = []
    has_soil_alert = soil_anomaly_res.get("alert_triggered", False)

    for i, fc in enumerate(forecast_results):
        day_step = i + 1
        zone = fc.get("risk_zone", "Yellow")
        sm_val = fc.get("predicted_sm", 0.20)
        
        # --- DAY 1 & 2: IRRIGATION HOLD / WATER GATE DECISION ---
        if day_step in [1, 2]:
            if zone == "Red" or sm_val < 0.16:
                t_en = "Critical Water Gate: High Scarcity"
                t_hi = "जल संकट: आवश्यक सिंचाई निर्णय"
                t_pa = "ਪਾਣੀ ਦੀ ਘਾਟ: ਜ਼ਰੂਰੀ ਸਿੰਚਾਈ ਫੈਸਲਾ"
                
                a_en = "Soil moisture critically low. Apply light evening irrigation or Direct Seeded Rice (DSR) wetting."
                a_hi = "मिट्टी में नमी अत्यधिक कम है। शाम के समय हल्की सिंचाई करें या DSR नमी प्रबंधन अपनाएं।"
                a_pa = "ਮਿੱਟੀ ਵਿੱਚ ਨਮੀ ਬਹੁਤ ਘੱਟ ਹੈ। ਸ਼ਾਮ ਵੇਲੇ ਹਲਕਾ ਪਾਣੀ ਲਗਾਓ ਜਾਂ DSR ਤਰੀਕਾ ਅਪਣਾਓ।"
                badge = "Critical"
                color = "#DC2626"
                icon = "🚨"
            elif zone == "Yellow" or sm_val < 0.24:
                t_en = "Irrigation Gate: 3-Day Delay Hold"
                t_hi = "सिंचाई प्रबंधन: 3 दिन पानी रोकें"
                t_pa = "ਸਿੰਚਾਈ ਪ੍ਰਬੰਧਨ: 3 ਦਿਨ ਪਾਣੀ ਰੋਕੋ"
                
                a_en = "Adequate residual moisture in subsoil. Hold flood irrigation for 48-72 hours to stimulate deeper rooting."
                a_hi = "जड़-क्षेत्र में पर्याप्त नमी है। 48-72 घंटे सिंचाई रोकें ताकि जड़ें गहराई तक जा सकें।"
                a_pa = "ਜੜ੍ਹ ਖੇਤਰ ਵਿੱਚ ਲੋੜੀਂਦੀ ਨਮੀ ਹੈ। 48-72 ਘੰਟੇ ਪਾਣੀ ਰੋਕੋ ਤਾਂ ਜੋ ਜੜ੍ਹਾਂ ਡੂੰਘੀਆਂ ਜਾਣ।"
                badge = "Conserve"
                color = "#F59E0B"
                icon = "🛑"
            else:
                t_en = "Optimal Hydrological Balance"
                t_hi = "सुरक्षित जल स्तर: सिंचाई बंद रखें"
                t_pa = "ਸੁਰੱਖਿਅਤ ਪਾਣੀ ਪੱਧਰ: ਪਾਣੀ ਬੰਦ ਰੱਖੋ"
                
                a_en = "Soil moisture abundant. Zero irrigation needed; inspect drainage channels to prevent waterlogging."
                a_hi = "पानी पर्याप्त है। सिंचाई की कोई आवश्यकता नहीं; जलभराव रोकने के लिए नालियों की जांच करें।"
                a_pa = "ਪਾਣੀ ਪੂਰਾ ਹੈ। ਸਿੰਚਾਈ ਦੀ ਲੋੜ ਨਹੀਂ; ਪਾਣੀ ਖੜ੍ਹਨ ਤੋਂ ਰੋਕਣ ਲਈ ਖਾਲੀਆਂ ਸਾਫ਼ ਰੱਖੋ।"
                badge = "Safe"
                color = "#16A34A"
                icon = "💧"

        # --- DAY 3 & 4: SOIL SAMPLING & SURFACE AERATION ---
        elif day_step in [3, 4]:
            if has_soil_alert:
                t_en = "PAU 15 cm V-Cut Soil Sampling"
                t_hi = "पीएयू 15 सेमी मिट्टी नमूना जांच"
                t_pa = "PAU 15 ਸੈਂਟੀਮੀਟਰ ਮਿੱਟੀ ਦਾ ਨਮੂਨਾ"
                
                a_en = "Landsat detects vegetative growth gap. Dig 15 cm V-shaped pits across 5-6 spots; collect 500g composite sample for KVK lab."
                a_hi = "उपग्रह ने फसल विकास में रुकावट पकड़ी है। 5-6 स्थानों पर 15 सेमी गहरा गड्ढा खोदकर 500 ग्राम मिट्टी का नमूना KVK लैब भेजें।"
                a_pa = "ਉਪਗ੍ਰਹਿ ਨੇ ਫ਼ਸਲ ਦੇ ਵਾਧੇ ਵਿੱਚ ਰੁਕਾਵਟ ਵੇਖੀ ਹੈ। 5-6 ਥਾਵਾਂ ਤੋਂ 15 ਸੈਂਟੀਮੀਟਰ ਡੂੰਘਾ ਨਮੂਨਾ ਲੈ ਕੇ KVK ਲੈਬ ਭੇਜੋ।"
                badge = "Soil Alert"
                color = "#7C3AED"
                icon = "🧪"
            else:
                t_en = "Mulching & Surface Evaporation Shield"
                t_hi = "पराली मल्चिंग एवं वाष्पीकरण नियंत्रण"
                t_pa = "ਪਰਾਲੀ ਮਲਚਿੰਗ ਅਤੇ ਵਾਸ਼ਪੀਕਰਨ ਰੋਕਥਾਮ"
                
                a_en = "Apply 2 tonnes/acre crop-residue straw mulch between rows to cut MODIS evapotranspiration losses by 15-20%."
                a_hi = "खेत में 2 टन प्रति एकड़ धान की पराली बिछाएं ताकि तेज धूप में मिट्टी की नमी न उड़े।"
                a_pa = "ਖੇਤ ਵਿੱਚ 2 ਟਨ ਪ੍ਰਤੀ ਏਕੜ ਪਰਾਲੀ ਦੀ ਮਲਚਿੰਗ ਕਰੋ ਤਾਂ ਜੋ ਸੂਰਜ ਦੀ ਗਰਮੀ ਨਾਲ ਨਮੀ ਨਾ ਉੱਡੇ।"
                badge = "Aeration"
                color = "#0284C7"
                icon = "🌾"

        # --- DAY 5, 6 & 7: REMEDIATION & EXTENSION SCOUTING ---
        else:
            if has_soil_alert:
                t_en = "Gypsum & Dhaincha Green Manuring"
                t_hi = "जिप्सम व ढैंचा हरी खाद अनुप्रयोग"
                t_pa = "ਜਿਪਸਮ ਅਤੇ ਜੰਤਰ (ਢੈਂਚਾ) ਹਰੀ ਖਾਦ"
                
                a_en = "Incorporate 2-4 bags/acre agricultural gypsum in alkaline patches; prepare Dhaincha (Sesbania) to rebuild organic carbon."
                a_hi = "क्षारीय मिट्टी में 2-4 बैग जिप्सम डालें और जैविक कार्बन बढ़ाने के लिए ढैंचा हरी खाद की तैयारी करें।"
                a_pa = "ਕੱਲਰ ਵਾਲੀ ਜ਼ਮੀਨ ਵਿੱਚ 2-4 ਬੋਰੀਆਂ ਜਿਪਸਮ ਪਾਓ ਅਤੇ ਜੈਵਿਕ ਕਾਰਬਨ ਵਧਾਉਣ ਲਈ ਜੰਤਰ ਦੀ ਬਿਜਾਈ ਕਰੋ।"
                badge = "Remedy"
                color = "#D97706"
                icon = "🚜"
            else:
                t_en = "7-Day Re-Assessment & Tubewell Audit"
                t_hi = "7-दिवसीय समीक्षा व ट्यूबवेल ऑडिट"
                t_pa = "7-ਦਿਨਾਂ ਦੀ ਸਮੀਖਿਆ ਅਤੇ ਟਿਊਬਵੈੱਲ ਆਡਿਟ"
                
                a_en = "Re-check NASA SMAP soil moisture telemetry. Verify tubewell meter logs to benchmark electric power and water saved."
                a_hi = "नासा उपग्रह डेटा से दोबारा खेत की नमी जांचें। ट्यूबवेल का बिजली मीटर चेक कर पानी व बिजली की बचत दर्ज करें।"
                a_pa = "ਨਾਸਾ ਸੈਟੇਲਾਈਟ ਡੇਟਾ ਤੋਂ ਦੁਬਾਰਾ ਨਮੀ ਚੈੱਕ ਕਰੋ। ਟਿਊਬਵੈੱਲ ਦੇ ਮੀਟਰ ਤੋਂ ਬਚਾਈ ਗਈ ਬਿਜਲੀ ਅਤੇ ਪਾਣੀ ਦਾ ਹਿਸਾਬ ਲਗਾਓ।"
                badge = "Audit"
                color = "#059669"
                icon = "📊"

        # Select localized text
        if lang == "pa":
            title = t_pa
            action = a_pa
        elif lang == "hi":
            title = t_hi
            action = a_hi
        else:
            title = t_en
            action = a_en

        calendar_days.append({
            "day_number": day_step,
            "day_label": fc.get("day_label", f"Day +{day_step}"),
            "title": title,
            "action": action,
            "badge": badge,
            "badge_color": color,
            "icon": icon,
            "projected_sm": sm_val,
            "risk_zone": zone
        })

    return calendar_days
