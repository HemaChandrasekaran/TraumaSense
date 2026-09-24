TRANSLATIONS = {

    "en": {
        "assessment": "Trauma & Stress Assessment",
        "result": "Assessment Result",
        "your_assessment": "Your Assessment",
        "svi": "Stress Vulnerability Index",
        "emotional": "Emotional Assessment",
        "stress": "Stress",
        "fear": "Fear",
        "anxiety": "Anxiety",
        "trauma": "Trauma Distress",
        "vulnerability": "Vulnerability",
        "safety": "Safety Assessment",
        "high": "HIGH RISK",
        "medium": "MEDIUM RISK",
        "low": "LOW RISK",
        "safety_detected": "A safety indicator was detected.",
        "no_safety": "No immediate safety indicator was detected.",
        "sos": "Emergency Safety Support",
        "emergency_help": "Get Emergency Help",
        "human": "Human Communication",
        "anonymous": "Start Anonymous Chat",
        "nearby": "Find Nearby Help"
    },

    "ta": {
        "assessment": "மனஅழுத்தம் மற்றும் பாதிப்பு மதிப்பீடு",
        "result": "மதிப்பீட்டு முடிவு",
        "your_assessment": "உங்கள் மதிப்பீடு",
        "svi": "மனஅழுத்த பாதிப்பு குறியீடு",
        "emotional": "உணர்ச்சி மதிப்பீடு",
        "stress": "மனஅழுத்தம்",
        "fear": "பயம்",
        "anxiety": "பதட்டம்",
        "trauma": "பாதிப்பு மனஅழுத்தம்",
        "vulnerability": "பாதிப்பு நிலை",
        "safety": "பாதுகாப்பு மதிப்பீடு",
        "high": "அதிக ஆபத்து",
        "medium": "நடுத்தர ஆபத்து",
        "low": "குறைந்த ஆபத்து",
        "safety_detected": "பாதுகாப்பு தொடர்பான அறிகுறி கண்டறியப்பட்டது.",
        "no_safety": "உடனடி பாதுகாப்பு அறிகுறி கண்டறியப்படவில்லை.",
        "sos": "அவசர பாதுகாப்பு உதவி",
        "emergency_help": "அவசர உதவி பெறவும்",
        "human": "மனிதருடன் தொடர்பு",
        "anonymous": "அநாமதேய உரையாடலை தொடங்கவும்",
        "nearby": "அருகிலுள்ள உதவியை கண்டறியவும்"
    },

    "hi": {
        "assessment": "आघात और तनाव मूल्यांकन",
        "result": "मूल्यांकन परिणाम",
        "your_assessment": "आपका मूल्यांकन",
        "svi": "तनाव संवेदनशीलता सूचकांक",
        "emotional": "भावनात्मक मूल्यांकन",
        "stress": "तनाव",
        "fear": "डर",
        "anxiety": "चिंता",
        "trauma": "आघात तनाव",
        "vulnerability": "संवेदनशीलता",
        "safety": "सुरक्षा मूल्यांकन",
        "high": "उच्च जोखिम",
        "medium": "मध्यम जोखिम",
        "low": "कम जोखिम",
        "safety_detected": "सुरक्षा संबंधी संकेत पाया गया।",
        "no_safety": "तत्काल सुरक्षा संकेत नहीं पाया गया।",
        "sos": "आपातकालीन सुरक्षा सहायता",
        "emergency_help": "आपातकालीन सहायता प्राप्त करें",
        "human": "मानव से संपर्क",
        "anonymous": "गुमनाम चैट शुरू करें",
        "nearby": "पास में सहायता खोजें"
    }
}


def get_translations(language):

    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["en"]
    )