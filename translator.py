# Lightweight multilingual preprocessing
# Used for SIH prototype demonstration.
# This is NOT a professional translation service.

TRANSLATIONS = {

    "Tamil": {
        "பயம்": "fear",
        "பயமாக": "scared",
        "பயமாக இருக்கிறது": "I am scared",
        "அச்சம்": "fear",
        "மிரட்டல்": "threat",
        "மிரட்டினார்": "threatened",
        "தனியாக": "alone",
        "கவலை": "anxiety",
        "கவலையாக": "anxious",
        "மன அழுத்தம்": "stress",
        "துன்பம்": "distress",
        "அழுகிறேன்": "crying",
        "பாதுகாப்பாக இல்லை": "not safe",
        "உதவி": "help"
    },

    "Hindi": {
        "डर": "fear",
        "डरा हुआ": "scared",
        "धमकी": "threat",
        "धमकी दी": "threatened",
        "अकेला": "alone",
        "चिंता": "anxiety",
        "तनाव": "stress",
        "दुख": "distress",
        "रो रहा": "crying",
        "सुरक्षित नहीं": "not safe",
        "मदद": "help"
    },

    "Telugu": {
        "భయం": "fear",
        "భయంగా": "scared",
        "బెదిరింపు": "threat",
        "బెదిరించారు": "threatened",
        "ఒంటరిగా": "alone",
        "ఆందోళన": "anxiety",
        "ఒత్తిడి": "stress",
        "బాధ": "distress",
        "ఏడుస్తున్నాను": "crying",
        "సురక్షితంగా లేదు": "not safe",
        "సహాయం": "help"
    },

    "Malayalam": {
        "ഭയം": "fear",
        "ഭയമാണ്": "scared",
        "ഭീഷണി": "threat",
        "ഭീഷണിപ്പെടുത്തി": "threatened",
        "ഒറ്റയ്ക്ക്": "alone",
        "ഉത്കണ്ഠ": "anxiety",
        "സമ്മർദ്ദം": "stress",
        "വേദന": "distress",
        "കരയുന്നു": "crying",
        "സുരക്ഷിതമല്ല": "not safe",
        "സഹായം": "help"
    },

    "Kannada": {
        "ಭಯ": "fear",
        "ಹೆದರಿಕೆ": "scared",
        "ಬೆದರಿಕೆ": "threat",
        "ಬೆದರಿಸಿದರು": "threatened",
        "ಒಂಟಿಯಾಗಿ": "alone",
        "ಆತಂಕ": "anxiety",
        "ಒತ್ತಡ": "stress",
        "ದುಃಖ": "distress",
        "ಅಳುತ್ತಿದ್ದೇನೆ": "crying",
        "ಸುರಕ್ಷಿತವಾಗಿಲ್ಲ": "not safe",
        "ಸಹಾಯ": "help"
    }
}


def translate_to_english(text, language):

    if not text:
        return ""

    if language == "English":
        return text

    translated_text = text

    language_dictionary = TRANSLATIONS.get(
        language,
        {}
    )

    # Replace known phrases
    for original, english in language_dictionary.items():

        translated_text = translated_text.replace(
            original,
            english
        )

    return translated_text