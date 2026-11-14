"""
Soil Testing Protocol & Agronomic Remediation Guide for Punjab Farmers.
Based on Punjab Agricultural University (PAU) and ICAR/KVK diagnostic standards.
"""

SOIL_TESTING_STEPS = [
    {
        "step_number": 1,
        "title_en": "Field Stratification & Spot Selection",
        "title_hi": "खेत का चयन एवं 5-6 स्थानों की पहचान",
        "title_pa": "ਖੇਤ ਦੀ ਚੋਣ ਅਤੇ 5-6 ਥਾਵਾਂ ਦੀ ਪਛਾਣ",
        "desc_en": "Divide field into uniform sampling units. Select 5 to 6 representative spots in a zigzag pattern across the field, avoiding field bunds, compost heaps, and shade trees.",
        "desc_hi": "खेत को एक समान हिस्सों में बांटें। मेड़ों, खाद के ढेरों और पेड़ों की छाया से दूर, जिग-जैग तरीके से 5-6 बिंदु चुनें।",
        "desc_pa": "ਖੇਤ ਨੂੰ ਇਕਸਾਰ ਹਿੱਸਿਆਂ ਵਿੱਚ ਵੰਡੋ। ਵੱਟਾਂ, ਰੂੜੀ ਦੇ ਢੇਰਾਂ ਅਤੇ ਰੁੱਖਾਂ ਦੀ ਛਾਂ ਤੋਂ ਦੂਰ, 5-6 ਥਾਵਾਂ ਚੁਣੋ।"
    },
    {
        "step_number": 2,
        "title_en": "V-Shaped 15 cm Depth Sampling",
        "title_pa": "15 ਸੈਂਟੀਮੀਟਰ ਡੂੰਘਾ V-ਆਕਾਰ ਦਾ ਕੱਟ",
        "title_hi": "15 सेमी गहरा V-आकार का कट",
        "desc_en": "Clear surface debris without scraping soil. Dig a V-shaped pit to a depth of 15 cm (plow layer). Using a clean spade or auger, slice a uniform 2 cm thick soil core from the pit edge.",
        "desc_hi": "सतह से खरपतवार हटाएं। 15 सेमी गहरा V-आकार का गड्ढा बनाएं और किनारे से 2 सेमी मोटी मिट्टी की परत निकालें।",
        "desc_pa": "ਸਤ੍ਹਾ ਤੋਂ ਕੂੜਾ-ਕਰਕਟ ਸਾਫ਼ ਕਰੋ। 15 ਸੈਂਟੀਮੀਟਰ ਡੂੰਘਾ V-ਆਕਾਰ ਦਾ ਟੋਆ ਪੁੱਟੋ ਅਤੇ ਕਿਨਾਰੇ ਤੋਂ 2 ਸੈਂਟੀਮੀਟਰ ਮੋਟੀ ਮਿੱਟੀ ਦੀ ਪਰਤ ਲਓ।"
    },
    {
        "step_number": 3,
        "title_en": "Composite Mixing & Quartering",
        "title_hi": "मिश्रण एवं चौथाई विधि (Quartering)",
        "title_pa": "ਮਿਸ਼ਰਣ ਅਤੇ ਚੌਥਾਈ ਵਿਧੀ (Quartering)",
        "desc_en": "Collect all sub-samples in a clean plastic bucket (avoid metal buckets). Thoroughly mix, break lumps, spread on clean paper, divide into 4 quarters, discard opposite quarters until ~500 grams remain.",
        "desc_hi": "सभी नमूनों को साफ प्लास्टिक बाल्टी में अच्छी तरह मिलाएं। कागज पर फैलाकर 4 हिस्से करें, दो विपरीत हिस्से हटाएं जब तक लगभग 500 ग्राम मिट्टी न बचे।",
        "desc_pa": "ਸਾਰੇ ਨਮੂਨਿਆਂ ਨੂੰ ਸਾਫ਼ ਪਲਾਸਟਿਕ ਦੀ ਬਾਲਟੀ ਵਿੱਚ ਚੰਗੀ ਤਰ੍ਹਾਂ ਮਿਲਾਓ। ਚਾਰ ਹਿੱਸਿਆਂ ਵਿੱਚ ਵੰਡੋ ਅਤੇ ਉਲਟ ਹਿੱਸੇ ਹਟਾਓ ਜਦੋਂ ਤੱਕ 500 ਗ੍ਰਾਮ ਮਿੱਟੀ ਨਾ ਬਚ ਜਾਵੇ।"
    },
    {
        "step_number": 4,
        "title_en": "Packaging & Lab Submission (KVK / PAU)",
        "title_hi": "पैकिंग और KVK/PAU लैब में जमा करना",
        "title_pa": "ਪੈਕਿੰਗ ਅਤੇ KVK/PAU ਲੈਬ ਵਿੱਚ ਜਮ੍ਹਾ ਕਰਨਾ",
        "desc_en": "Air-dry in shade (do not heat or sun-bake). Pack in a labeled cloth/polythene bag stating Farmer Name, Village, Survey/Khasra No., and submit to the nearest Krishi Vigyan Kendra (KVK) or PAU lab.",
        "desc_hi": "छाया में सुखाएं (धूप में नहीं)। किसान का नाम, गांव और खसरा नंबर लिखकर नजदीकी केवीके (KVK) या पीएयू (PAU) लैब में जमा करें।",
        "desc_pa": "ਛਾਂ ਵਿੱਚ ਸੁਕਾਓ (ਧੁੱਪ ਵਿੱਚ ਨਹੀਂ)। ਕਿਸਾਨ ਦਾ ਨਾਮ, ਪਿੰਡ ਅਤੇ ਖਸਰਾ ਨੰਬਰ ਲਿਖ ਕੇ ਨਜ਼ਦੀਕੀ ਕ੍ਰਿਸ਼ੀ ਵਿਗਿਆਨ ਕੇਂਦਰ (KVK) ਜਾਂ PAU ਲੈਬ ਵਿੱਚ ਦਿਓ।"
    }
]

REMEDIES_GUIDE = [
    {
        "problem": "Alkaline / Sodic Soil (pH > 8.5, ESP > 15%)",
        "remedy_en": "Apply Agricultural Grade Gypsum (Calcium Sulfate) based on gypsum requirement test (typically 2-4 bags/acre). Mix thoroughly in top 10 cm before pre-sowing irrigation to flush displaced sodium downward.",
        "remedy_hi": "जिप्सम (कैल्शियम सल्फेट) 2-4 बैग प्रति एकड़ डालें। बुवाई से पहले खेत में मिलाकर पानी भरें ताकि हानिकारक सोडियम नीचे निकल जाए।",
        "remedy_pa": "ਖੇਤ ਵਿੱਚ ਜਿਪਸਮ (ਕੈਲਸ਼ੀਅਮ ਸਲਫੇਟ) 2-4 ਬੋਰੀਆਂ ਪ੍ਰਤੀ ਏਕੜ ਪਾਓ। ਬਿਜਾਈ ਤੋਂ ਪਹਿਲਾਂ ਰੌਣੀ ਕਰਕੇ ਪਾਣੀ ਖੜ੍ਹਾ ਕਰੋ ਤਾਂ ਜੋ ਸੋਡੀਅਮ ਹੇਠਾਂ ਚਲਾ ਜਾਵੇ।"
    },
    {
        "problem": "Saline Soil with High Salt Crust (EC > 4.0 dS/m)",
        "remedy_en": "Leach accumulated surface salts using good quality canal water. Ensure laser land leveling and deep sub-soiling to break hardpan and promote downward drainage.",
        "remedy_hi": "अच्छी गुणवत्ता वाले नहरी पानी से लवणों को नीचे बहाएं (Leaching)। लेजर लैंड लेवलिंग और गहरी जुताई करें।",
        "remedy_pa": "ਚੰਗੇ ਨਹਿਰੀ ਪਾਣੀ ਨਾਲ ਖਾਰ ਨੂੰ ਹੇਠਾਂ ਵਹਾਓ (Leaching)। ਲੇਜ਼ਰ ਕਰਾਹੇ ਨਾਲ ਜ਼ਮੀਨ ਪੱਧਰੀ ਕਰੋ ਅਤੇ ਡੂੰਘੀ ਵਹਾਈ ਕਰੋ।"
    },
    {
        "problem": "Low Organic Carbon (< 0.40%) & Depleted Microbes",
        "remedy_en": "Practice Green Manuring with Dhaincha (Sesbania aculeata) or Sunhemp. Incorporate at 45-50 days before paddy transplanting. Strictly maintain Zero Stubble Burning.",
        "remedy_hi": "धान से पहले ढैंचा (Dhaincha) की हरी खाद बोएं और 45-50 दिन में जोत दें। पराली बिल्कुल न जलाएं (Zero Stubble Burning)।",
        "remedy_pa": "ਝੋਨੇ ਤੋਂ ਪਹਿਲਾਂ ਜੰਤਰ (ਢੈਂਚਾ) ਦੀ ਹਰੀ ਖਾਦ ਬੀਜੋ ਅਤੇ 45-50 ਦਿਨਾਂ ਬਾਅਦ ਵਾਹ ਦਿਓ। ਪਰਾਲੀ ਨੂੰ ਬਿਲਕੁਲ ਅੱਗ ਨਾ ਲਗਾਓ।"
    },
    {
        "problem": "Zinc & Micronutrient Chlorosis (Yellowing of Lower Leaves)",
        "remedy_en": "Apply 25 kg/acre Zinc Sulfate Heptahydrate (21%) at final field preparation, or foliar spray 0.5% ZnSO4 + 2.5% urea in standing crop during active tillering.",
        "remedy_hi": "बुवाई के समय 25 किग्रा जिंक सल्फेट (21%) प्रति एकड़ डालें, या खड़ी फसल में 0.5% जिंक सल्फेट + 2.5% यूरिया का छिड़काव करें।",
        "remedy_pa": "ਬਿਜਾਈ ਸਮੇਂ 25 ਕਿਲੋ ਜ਼ਿੰਕ ਸਲਫੇਟ (21%) ਪ੍ਰਤੀ ਏਕੜ ਪਾਓ, ਜਾਂ ਖੜ੍ਹੀ ਫਸਲ 'ਤੇ 0.5% ਜ਼ਿੰਕ ਸਲਫੇਟ + 2.5% ਯੂਰੀਆ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।"
    }
]
