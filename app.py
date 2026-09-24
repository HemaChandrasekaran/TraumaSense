from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

from translations import get_translations

import uuid
import os
import random

from transformers import pipeline


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "trauma-assessment-demo-secret"


# ============================================================
# LANGUAGES
# ============================================================

LANGUAGES = {
    "English": "English",
    "Tamil": "தமிழ்",
    "Hindi": "हिन्दी",
    "Telugu": "తెలుగు",
    "Malayalam": "മലയാളം",
    "Kannada": "ಕನ್ನಡ",
    "Bengali": "বাংলা",
    "Marathi": "मराठी"
}


# ============================================================
# AI MODEL
# ============================================================

print()
print("=" * 60)
print("Loading AI emotion model...")
print("=" * 60)

try:

    emotion_model = pipeline(
        "text-classification",
        model="joeddav/distilbert-base-uncased-go-emotions-student",
        top_k=None
    )

    AI_MODEL_READY = True

    print("AI emotion model loaded successfully.")

except Exception as e:

    emotion_model = None

    AI_MODEL_READY = False

    print("AI model loading failed:")
    print(e)

print("=" * 60)
print()


# ============================================================
# LANGUAGE CONTEXT
# ============================================================

@app.context_processor
def inject_language():

    language = session.get(
        "language",
        "English"
    )

    try:

        t = get_translations(language)

    except Exception:

        t = {}

    return {
        "current_language": language,
        "languages": LANGUAGES,
        "t": t
    }


# ============================================================
# SET LANGUAGE
# ============================================================

@app.route("/set-language/<language>")
def set_language(language):

    if language not in LANGUAGES:

        language = "English"

    session["language"] = language

    return redirect(
        request.referrer or "/assessment"
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# ASSESSMENT
# ============================================================

@app.route("/assessment")
def assessment():

    return render_template(
        "assessment.html"
    )


# ============================================================
# VISUAL EMOTIONAL RESPONSE ASSESSMENT
# ============================================================

@app.route("/visual-assessment", methods=["GET"])
def visual_assessment():

    image_folder = os.path.join(
        app.static_folder,
        "captcha_images"
    )

    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    available_images = [
        file for file in os.listdir(image_folder)
        if file.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        )
    ]

    if len(available_images) < 6:
        return (
            "<h2>Visual Assessment Setup Required</h2>"
            "<p>Please add at least 6 pictures to "
            "<b>static/captcha_images</b>.</p>"
        ), 400

    selected_images = random.sample(available_images, 6)
    random.shuffle(selected_images)

    session["visual_images"] = selected_images

    visual_assessment_id = (
        "VA-" + uuid.uuid4().hex[:8].upper()
    )
    session["visual_assessment_id"] = visual_assessment_id

    return render_template(
        "visual_assessment.html",
        images=selected_images,
        assessment_id=visual_assessment_id
    )


# ============================================================
# VISUAL RESPONSE ANALYSIS
# ============================================================

@app.route("/visual-assessment/analyze", methods=["POST"])
def visual_assessment_analyze():

    selected_image = request.form.get(
        "selected_image", ""
    ).strip()

    description = request.form.get(
        "description", ""
    ).strip()

    if not selected_image:
        return (
            "<script>"
            "alert('Please select a picture.');"
            "window.history.back();"
            "</script>"
        )

    if not description:
        return (
            "<script>"
            "alert('Please describe what you see in the picture.');"
            "window.history.back();"
            "</script>"
        )

    shown_images = session.get("visual_images", [])

    if selected_image not in shown_images:
        return (
            "<script>"
            "alert('Invalid picture selection.');"
            "window.location.href='/visual-assessment';"
            "</script>"
        )

    # --------------------------------------------------------
    # AI VISUAL EMOTION ANALYSIS
    # --------------------------------------------------------

    visual_emotions = analyze_emotions(description)

    fear = get_score(
        visual_emotions,
        ["fear", "horror"]
    )

    anxiety = get_score(
        visual_emotions,
        ["nervousness", "fear"]
    )

    sadness = get_score(
        visual_emotions,
        ["sadness", "grief"]
    )

    visual_score = round(
        (
            fear * 0.40
            + anxiety * 0.30
            + sadness * 0.30
        ),
        2
    )

    visual_score = max(
        0,
        min(100, visual_score)
    )

    visual_level = get_stress_level(
        visual_score
    )

    dominant_emotion = "neutral"
    dominant_score = 0

    if visual_emotions:
        dominant_emotion = max(
            visual_emotions,
            key=visual_emotions.get
        )
        dominant_score = round(
            visual_emotions[dominant_emotion],
            2
        )

    if visual_level == "HIGH":
        explanation = (
            "The response contains stronger emotional indicators "
            "such as fear, nervousness or sadness. Additional "
            "human review may be useful."
        )
    elif visual_level == "MODERATE":
        explanation = (
            "The response contains some emotional indicators. "
            "This can be considered as an additional screening "
            "input together with the other assessment results."
        )
    else:
        explanation = (
            "The response contains relatively lower levels of "
            "the emotional indicators used by this screening."
        )

    visual_result = {
        "assessment_id": session.get(
            "visual_assessment_id", "VA-DEMO001"
        ),
        "selected_image": selected_image,
        "description": description,
        "fear": fear,
        "anxiety": anxiety,
        "sadness": sadness,
        "visual_score": visual_score,
        "visual_level": visual_level,
        "dominant_emotion": dominant_emotion,
        "dominant_score": dominant_score,
        "emotion_scores": visual_emotions,
        "explanation": explanation,
        "screening_type": (
            "AI-Assisted Visual Emotional Response Screening"
        )
    }

    session["visual_result"] = visual_result
    session.modified = True

    return redirect("/behavioral-assessment")
    # --------------------------------------------------------
    # GET TEXT ASSESSMENT RESULT
    # --------------------------------------------------------

    previous_result = session.get(
        "assessment_result",
        {}
    )

    text_svi = float(
        previous_result.get(
            "vulnerability",
            0
        ) or 0
    )

    visual_svi = float(
        visual_score
    )

    behavioral_data = session.get(
        "behavioral_result",
        {}
    )

    behavioral_svi = float(
        behavioral_data.get(
            "score",
            0
        ) or 0
    )

    mood_svi = calculate_mood_score()

    # --------------------------------------------------------
    # FINAL COMBINED SVI
    # --------------------------------------------------------

    svi = calculate_combined_svi(
        text_score=text_svi,
        visual_score=visual_svi,
        behavioral_score=behavioral_svi,
        mood_score=mood_svi
    )

    svi_level = get_siv_level(svi)

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    narrative = previous_result.get(
        "original_text",
        ""
    )

    safety_indicators = detect_safety_indicators(
        narrative
    )

    safety_flag = len(safety_indicators) > 0

    if safety_flag or svi >= 70:
        risk = "HIGH"
    elif svi >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    if risk == "HIGH":
        svi_explanation = (
            "The AI assessment indicates a high level of emotional "
            "distress or vulnerability. Priority human review may "
            "be appropriate."
        )
    elif risk == "MEDIUM":
        svi_explanation = (
            "The AI assessment indicates a moderate level of emotional "
            "distress or vulnerability. Further human review may be useful."
        )
    else:
        svi_explanation = (
            "The AI assessment indicates a relatively lower level "
            "of emotional distress."
        )

    # --------------------------------------------------------
    # SVI CONTRIBUTIONS
    # Text = 45%, Visual = 20%, Behavioral = 20%, Mood = 15%
    # --------------------------------------------------------

    svi_contributions = {
        "text": round(text_svi * 0.45, 2),
        "visual": round(visual_svi * 0.20, 2),
        "behavioral": round(behavioral_svi * 0.20, 2),
        "mood": round(mood_svi * 0.15, 2)
    }

    # --------------------------------------------------------
    # UPDATE FINAL RESULT
    # --------------------------------------------------------

    previous_result.update({
        "svi": svi,
        "svi_level": svi_level,
        "risk": risk,
        "safety_flag": safety_flag,
        "safety_indicators": safety_indicators,
        "svi_explanation": svi_explanation,
        "visual_svi": visual_svi,
        "behavioral_svi": behavioral_svi,
        "mood_svi": mood_svi,
        "svi_components": {
            "text": text_svi,
            "visual": visual_svi,
            "behavioral": behavioral_svi,
            "mood": mood_svi
        },
        "svi_weights": {
            "text": 45,
            "visual": 20,
            "behavioral": 20,
            "mood": 15
        },
        "svi_contributions": svi_contributions
    })

    session["assessment_result"] = previous_result
    session.modified = True

    # Final result after visual assessment
    return redirect("/result")


# ============================================================
# AI EMOTION ANALYSIS
# ============================================================

def analyze_emotions(text):

    if not AI_MODEL_READY:

        return {}

    try:

        output = emotion_model(text)

        if (
            isinstance(output, list)
            and len(output) > 0
            and isinstance(output[0], list)
        ):

            emotions = output[0]

        else:

            emotions = output

        scores = {}

        for item in emotions:

            label = item.get(
                "label"
            )

            score = item.get(
                "score",
                0
            )

            if label:

                scores[label] = round(
                    float(score) * 100,
                    2
                )

        return scores

    except Exception as e:

        print(
            "Emotion analysis error:",
            e
        )

        return {}


# ============================================================
# GET EMOTION SCORE
# ============================================================

def get_score(scores, emotions):

    values = []

    for emotion in emotions:

        values.append(
            scores.get(
                emotion,
                0
            )
        )

    if not values:

        return 0

    return round(
        max(values),
        2
    )


# ============================================================
# STRESS INDICATOR
#
# Separate from SIV.
#
# SIV = overall vulnerability
# Stress Indicator = stress-related emotions only
# ============================================================

def calculate_stress_indicator(scores):

    nervousness = scores.get(
        "nervousness",
        0
    )

    annoyance = scores.get(
        "annoyance",
        0
    )

    anger = scores.get(
        "anger",
        0
    )

    frustration = scores.get(
        "disapproval",
        0
    )

    stress_indicator = (
        nervousness * 0.45
        + annoyance * 0.20
        + anger * 0.20
        + frustration * 0.15
    )

    return round(
        min(stress_indicator, 100),
        2
    )


# ============================================================
# STRESS LEVEL
# ============================================================

def get_stress_level(score):

    if score >= 70:

        return "HIGH"

    elif score >= 40:

        return "MODERATE"

    else:

        return "LOW"


# ============================================================
# SIV LEVEL
# ============================================================

def get_siv_level(score):

    if score >= 70:

        return "HIGH"

    elif score >= 40:

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# SAFETY INDICATORS
# ============================================================

def detect_safety_indicators(text):

    lower_text = text.lower()

    safety_words = [

        "danger",
        "unsafe",
        "threat",
        "threatened",
        "attack",
        "attacked",
        "violence",
        "violent",
        "abuse",
        "abused",
        "hurt",
        "harm",
        "emergency",
        "help",
        "kill",
        "killed",
        "suicide"

    ]

    found = []

    for word in safety_words:

        if word in lower_text:

            found.append(word)

    return found


# ============================================================
# MOOD DIARY
# ============================================================

def calculate_mood_score():

    moods = session.get("mood_diary", [])

    if not moods:
        return 0

    mood_values = {
        "Very Sad": 100,
        "Sad": 75,
        "Neutral": 50,
        "Good": 25,
        "Very Good": 0
    }

    recent_moods = moods[-5:]
    scores = []

    for entry in recent_moods:
        mood = entry.get("mood")
        if mood in mood_values:
            scores.append(mood_values[mood])

    if not scores:
        return 0

    return round(sum(scores) / len(scores), 2)


@app.route("/mood-diary", methods=["GET"])
def mood_diary():

    return render_template(
        "mood_diary.html",
        moods=session.get("mood_diary", [])
    )


@app.route("/mood-diary/save", methods=["POST"])
def mood_diary_save():

    mood = request.form.get("mood", "Neutral").strip()
    note = request.form.get("note", "").strip()

    allowed_moods = {
        "Very Sad", "Sad", "Neutral", "Good", "Very Good"
    }

    if mood not in allowed_moods:
        mood = "Neutral"

    diary = session.get("mood_diary", [])
    diary.append({"mood": mood, "note": note})
    session["mood_diary"] = diary[-20:]
    session.modified = True

    return redirect("/mood-diary")


# ============================================================
# GOOSE COMPANION
# ============================================================

@app.route("/goose", methods=["GET"])
def goose():

    return render_template("goose.html")


@app.route("/goose/respond", methods=["POST"])
def goose_respond():

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "reply": "You can tell me what is on your mind."
        }), 400

    lower = message.lower()

    if any(word in lower for word in ["sad", "cry", "lonely", "upset"]):
        reply = "It sounds like you are having a difficult moment. You can share more if you feel comfortable."
    elif any(word in lower for word in ["afraid", "scared", "fear", "unsafe"]):
        reply = "I hear that you are feeling afraid or unsafe. Your safety matters, and human support can help."
    elif any(word in lower for word in ["happy", "good", "great", "excited"]):
        reply = "That sounds wonderful! I am happy to hear that you are feeling positive today."
    else:
        reply = "Thank you for sharing with me. I am here to listen, and you can take things one step at a time."

    return jsonify({
        "success": True,
        "reply": reply
    })


# ============================================================
# BEHAVIORAL RESPONSE ASSESSMENT
# ============================================================

@app.route(
    "/behavioral-assessment",
    methods=["GET"]
)
def behavioral_assessment():

    return render_template(
        "behavioral_assessment.html"
    )


@app.route(
    "/behavioral-assessment/analyze",
    methods=["POST"]
)
def behavioral_assessment_analyze():

    # Each question is scored from 0 to 3.
    # Five questions therefore give a maximum of 15.

    scores = []

    for i in range(5):

        raw = request.form.get(
            f"q{i}",
            "0"
        )

        try:

            value = int(raw)

        except ValueError:

            value = 0

        value = max(
            0,
            min(
                3,
                value
            )
        )

        scores.append(
            value
        )

    # --------------------------------------------------------
    # TOTAL SCORE
    # --------------------------------------------------------

    total = sum(
        scores
    )

    behavioral_score = round(
        (total / 15) * 100,
        2
    )

    # --------------------------------------------------------
    # BEHAVIORAL LEVEL
    # --------------------------------------------------------

    if behavioral_score >= 70:

        level = "HIGH"

    elif behavioral_score >= 40:

        level = "MEDIUM"

    else:

        level = "LOW"

    # --------------------------------------------------------
    # SAVE BEHAVIORAL RESULT
    # --------------------------------------------------------

    session[
        "behavioral_result"
    ] = {

        "score":
            behavioral_score,

        "raw_score":
            total,

        "responses":
            scores,

        "level":
            level
    }

    session.modified = True

    # --------------------------------------------------------
    # SHOW BEHAVIORAL RESULT
    # --------------------------------------------------------

    return render_template(

        "behavioral_result.html",

        result=session[
            "behavioral_result"
        ]

    )
# --------------------------------------------------------
    # FINAL SVI AFTER VISUAL + BEHAVIORAL ASSESSMENT
    # --------------------------------------------------------

    result_data = session.get(
        "assessment_result",
        {}
    )

    visual_data = session.get(
        "visual_result",
        {}
    )

    text_svi = float(
        result_data.get(
            "vulnerability",
            0
        ) or 0
    )

    visual_svi = float(
        visual_data.get(
            "visual_score",
            0
        ) or 0
    )

    mood_svi = calculate_mood_score()

    final_svi = calculate_combined_svi(
        text_score=text_svi,
        visual_score=visual_svi,
        behavioral_score=behavioral_score,
        mood_score=mood_svi
    )

    final_svi_level = get_siv_level(
        final_svi
    )

    narrative = result_data.get(
        "original_text",
        ""
    )

    safety_indicators = detect_safety_indicators(
        narrative
    )

    safety_flag = bool(
        safety_indicators
    )

    if safety_flag or final_svi >= 70:
        risk = "HIGH"
    elif final_svi >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    if risk == "HIGH":
        explanation = (
            "The AI assessment indicates a high level of emotional "
            "distress or vulnerability. Priority human review may "
            "be appropriate."
        )
    elif risk == "MEDIUM":
        explanation = (
            "The AI assessment indicates a moderate level of emotional "
            "distress or vulnerability. Further human review may be useful."
        )
    else:
        explanation = (
            "The AI assessment indicates a relatively lower level "
            "of emotional distress."
        )

    result_data.update({
        "svi": final_svi,
        "svi_level": final_svi_level,
        "risk": risk,
        "safety_flag": safety_flag,
        "safety_indicators": safety_indicators,
        "svi_explanation": explanation,
        "visual_svi": visual_svi,
        "behavioral_svi": behavioral_score,
        "mood_svi": mood_svi,
        "svi_components": {
            "text": text_svi,
            "visual": visual_svi,
            "behavioral": behavioral_score,
            "mood": mood_svi
        },
        "svi_weights": {
            "text": 45,
            "visual": 20,
            "behavioral": 20,
            "mood": 15
        },
        "svi_contributions": {
            "text": round(text_svi * 0.45, 2),
            "visual": round(visual_svi * 0.20, 2),
            "behavioral": round(behavioral_score * 0.20, 2),
            "mood": round(mood_svi * 0.15, 2),
            "stress": result_data.get("stress", 0),
            "fear": result_data.get("fear", 0),
            "anxiety": result_data.get("anxiety", 0),
            "trauma": result_data.get("trauma_distress", 0)
        }
    })

    session["assessment_result"] = result_data
    session.modified = True

    return render_template(
        "behavioral_result.html",
        result=behavioral_result
    )


# ============================================================
# SVI FUSION
# ============================================================

def calculate_combined_svi(
    text_score=0,
    visual_score=0,
    behavioral_score=0,
    mood_score=0
):
    """Prototype screening indicator, not a medical diagnosis."""

    combined = (
        (float(text_score) * 0.45)
        + (float(visual_score) * 0.20)
        + (float(behavioral_score) * 0.20)
        + (float(mood_score) * 0.15)
    )

    return round(
        min(max(combined, 0), 100),
        2
    )


# ============================================================
# ANALYZE
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    print()
    print("=" * 60)
    print("ANALYZE REQUEST RECEIVED")
    print("=" * 60)

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    selected_language = request.form.get(
        "language",
        "English"
    )

    if selected_language not in LANGUAGES:

        selected_language = "English"

    session["language"] = selected_language

    print(
        "Language:",
        selected_language
    )

    # --------------------------------------------------------
    # NARRATIVE
    # --------------------------------------------------------

    narrative = request.form.get(
        "narrative",
        ""
    ).strip()

    print(
        "Narrative received:",
        bool(narrative)
    )

    # --------------------------------------------------------
    # CONSENT
    # --------------------------------------------------------

    consent = request.form.get(
        "consent",
        ""
    )

    print(
        "Consent received:",
        bool(consent)
    )

    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    voice_file = request.files.get(
        "voice_file"
    )

    voice_received = False

    if voice_file and voice_file.filename:

        voice_received = True

        print(
            "Voice file received:",
            voice_file.filename
        )

    else:

        print(
            "No voice file received."
        )

    # --------------------------------------------------------
    # EMPTY TEXT
    # --------------------------------------------------------

    if not narrative:

        return redirect(
            "/assessment"
        )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    emotion_scores = analyze_emotions(
        narrative
    )

    print(
        "Emotion scores:",
        emotion_scores
    )

    # ========================================================
    # STRESS
    # ========================================================

    stress = get_score(

        emotion_scores,

        [
            "nervousness",
            "annoyance",
            "anger"
        ]

    )

    # ========================================================
    # SEPARATE STRESS INDICATOR
    # ========================================================

    stress_indicator = calculate_stress_indicator(
        emotion_scores
    )

    stress_level = get_stress_level(
        stress_indicator
    )

    # ========================================================
    # FEAR
    # ========================================================

    fear = get_score(

        emotion_scores,

        [
            "fear",
            "horror"
        ]

    )

    # ========================================================
    # ANXIETY
    # ========================================================

    anxiety = get_score(

        emotion_scores,

        [
            "nervousness",
            "fear"
        ]

    )

    # ========================================================
    # TRAUMA / DISTRESS
    # ========================================================

    trauma_distress = get_score(

        emotion_scores,

        [
            "sadness",
            "grief",
            "fear",
            "remorse"
        ]

    )

    # ========================================================
    # VULNERABILITY
    # ========================================================

    vulnerability = round(

        (
            stress
            + fear
            + anxiety
            + trauma_distress
        ) / 4,

        2

    )

    # ========================================================
    # PREPARE DATA FOR VISUAL ASSESSMENT
    # ========================================================

    # Text-based signal
    text_svi = vulnerability

    # Visual assessment will happen next.
    visual_svi = 0

    # Behavioral assessment signal
    behavioral_data = session.get("behavioral_result", {})
    behavioral_svi = float(
        behavioral_data.get("score", 0) or 0
    )

    # Mood diary signal
    mood_svi = calculate_mood_score()

    # Clear any previous visual assessment so that an old case
    # cannot affect the current assessment.
    session.pop("visual_result", None)
    session.pop("visual_images", None)
    session.pop("visual_assessment_id", None)

    # Temporary SVI before visual assessment. The final SVI is
    # recalculated in /visual-assessment/analyze.
    svi = calculate_combined_svi(
        text_score=text_svi,
        visual_score=visual_svi,
        behavioral_score=behavioral_svi,
        mood_score=mood_svi
    )

    svi_level = get_siv_level(svi)

    # ========================================================
    # SAFETY
    # ========================================================

    safety_indicators = detect_safety_indicators(
        narrative
    )

    safety_flag = (
        len(safety_indicators) > 0
    )

    # ========================================================
    # RISK
    # ========================================================

    if safety_flag or svi >= 70:

        risk = "HIGH"

    elif svi >= 40:

        risk = "MEDIUM"

    else:

        risk = "LOW"

    # ========================================================
    # EXPLANATION
    # ========================================================

    if risk == "HIGH":

        svi_explanation = (

            "The AI assessment indicates "
            "a high level of emotional "
            "distress or vulnerability. "
            "Priority human review may "
            "be appropriate."

        )

    elif risk == "MEDIUM":

        svi_explanation = (

            "The AI assessment indicates "
            "a moderate level of emotional "
            "distress or vulnerability. "
            "Further human review may "
            "be useful."

        )

    else:

        svi_explanation = (

            "The AI assessment indicates "
            "a relatively lower level "
            "of emotional distress."

        )

    # ========================================================
    # CASE ID
    # ========================================================

    case_id = (

        "TA-"
        + uuid.uuid4().hex[:8].upper()

    )

    # ========================================================
    # RESULT
    # ========================================================

    result_data = {

        "case_id":
            case_id,

        "svi":
            svi,

        "svi_level":
            svi_level,

        "risk":
            risk,

        "stress":
            stress,

        "stress_indicator":
            stress_indicator,

        "stress_level":
            stress_level,

        "fear":
            fear,

        "anxiety":
            anxiety,

        "trauma_distress":
            trauma_distress,

        "vulnerability":
            vulnerability,

        "safety_flag":
            safety_flag,

        "safety_indicators":
            safety_indicators,

        "svi_explanation":
            svi_explanation,

        "svi_contributions": {

            "text":
                text_svi,

            "visual":
                visual_svi,

            "behavioral":
                behavioral_svi,

            "mood":
                mood_svi,

            "stress":
                stress,

            "fear":
                fear,

            "anxiety":
                anxiety,

            "trauma":
                trauma_distress

        },

        "svi_components": {

            "text":
                text_svi,

            "visual":
                visual_svi,

            "behavioral":
                behavioral_svi,

            "mood":
                mood_svi

        },

        "svi_weights": {

            "text": 45,
            "visual": 20,
            "behavioral": 20,
            "mood": 15

        },

        "visual_svi":
            visual_svi,

        "behavioral_svi":
            behavioral_svi,

        "mood_svi":
            mood_svi,

        "emotion_scores":
            emotion_scores,

        "original_text":
            narrative,

        "analysis_text":
            narrative,

        "language":
            selected_language,

        "model":
            "joeddav/distilbert-base-uncased-go-emotions-student",

        "voice_received":
            voice_received

    }

    # ========================================================
    # SAVE SESSION
    # ========================================================

    session[
        "assessment_result"
    ] = result_data

    session[
        "case_id"
    ] = case_id

    session[
        "selected_language"
    ] = selected_language

    # Start a fresh visual assessment for this case.
    session.pop("visual_result", None)
    session.pop("visual_images", None)
    session.pop("visual_assessment_id", None)

    session.modified = True

    # ========================================================
    # TERMINAL
    # ========================================================

    print()
    print("-" * 60)
    print("ASSESSMENT COMPLETE")
    print("-" * 60)
    print("SIV:", svi)
    print("SIV LEVEL:", svi_level)
    print("STRESS INDICATOR:", stress_indicator)
    print("STRESS LEVEL:", stress_level)
    print("RISK:", risk)
    print("SAFETY:", safety_flag)
    print("CASE:", case_id)
    print("-" * 60)
    print()

    # Continue to the Visual Emotional Response Assessment.
    # The final SVI is calculated after visual analysis.
    return redirect(
        "/visual-assessment"
    )


# ============================================================
# RESULT PAGE
# ============================================================

@app.route("/result")
def result():

    result_data = session.get(
        "assessment_result"
    )

    if result_data is None:

        return redirect(
            "/assessment"
        )

    case_id = session.get(
        "case_id",
        result_data.get(
            "case_id",
            "TA-DEMO001"
        )
    )

    language = session.get(
        "language",
        "English"
    )

    try:

        t = get_translations(
            language
        )

    except Exception:

        t = {}

    return render_template(

        "result.html",

        result=result_data,

        t=t,

        case_id=case_id,

        fusion=result_data,

        voice_result=None,

        recommendations=[],

        original_text=
            result_data.get(
                "original_text",
                ""
            ),

        analysis_text=
            result_data.get(
                "analysis_text",
                ""
            )

    )


# ============================================================
# REVIEW PAGE
# ============================================================

@app.route("/review")
def review():

    result_data = session.get(
        "assessment_result"
    )

    if result_data is None:

        return redirect(
            "/assessment"
        )

    return render_template(

        "review.html",

        result=result_data,

        case_id=session.get(
            "case_id",
            "TA-DEMO001"
        )

    )


# ============================================================
# HUMAN REVIEW SUBMIT
# ============================================================

@app.route(
    "/review/submit",
    methods=["POST"]
)
def review_submit():

    reviewer_name = request.form.get(
        "reviewer_name",
        "Authorized Reviewer"
    )

    review_notes = request.form.get(
        "review_notes",
        ""
    ).strip()

    review_status = request.form.get(
        "review_status",
        "Reviewed"
    )

    session[
        "human_review"
    ] = {

        "reviewer_name":
            reviewer_name,

        "review_notes":
            review_notes,

        "review_status":
            review_status

    }

    session.modified = True

    return redirect(
        "/review"
    )


# ============================================================
# ANONYMOUS CHAT
# ============================================================

@app.route("/anonymous-chat")
def anonymous_chat():

    return render_template(
        "anonymous_chat.html"
    )


# ============================================================
# ANONYMOUS CHAT SEND
# ============================================================

@app.route(
    "/anonymous-chat/send",
    methods=["POST"]
)
def anonymous_chat_send():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "success":
                False,

            "reply":
                "Please enter a message."

        }), 400

    message = data.get(
        "message",
        ""
    ).strip()

    if not message:

        return jsonify({

            "success":
                False,

            "reply":
                "Please enter a message."

        }), 400

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    chat_history = session.get(
        "chat_history",
        []
    )

    chat_history.append({

        "sender":
            "user",

        "message":
            message

    })

    lower_message = message.lower()

    # --------------------------------------------------------
    # DANGER
    # --------------------------------------------------------

    danger_words = [

        "danger",
        "help",
        "unsafe",
        "scared",
        "afraid",
        "threat",
        "hurt",
        "emergency",
        "violence",
        "abuse",
        "attack",
        "harm"

    ]

    # --------------------------------------------------------
    # GREETINGS
    # --------------------------------------------------------

    greeting_words = [

        "hello",
        "hi",
        "hey"

    ]

    # --------------------------------------------------------
    # REPLY
    # --------------------------------------------------------

    if any(
        word in lower_message
        for word in danger_words
    ):

        reply = (

            "Thank you for sharing this. "
            "Your message has been marked "
            "for priority human review. "
            "If you are in immediate danger, "
            "please call 112 or contact "
            "a trusted person nearby."

        )

    elif any(
        word in lower_message
        for word in greeting_words
    ):

        reply = (

            "Hello. You can share what "
            "you are experiencing here. "
            "This anonymous space is intended "
            "to help connect your concern "
            "with appropriate human review."

        )

    else:

        reply = (

            "Thank you for sharing that. "
            "Your message has been received. "
            "An authorized human reviewer "
            "can review the information "
            "and determine the appropriate "
            "next step."

        )

    # --------------------------------------------------------
    # SAVE REPLY
    # --------------------------------------------------------

    chat_history.append({

        "sender":
            "reviewer",

        "message":
            reply

    })

    session[
        "chat_history"
    ] = chat_history

    session.modified = True

    return jsonify({

        "success":
            True,

        "reply":
            reply

    })


# ============================================================
# CHAT HISTORY
# ============================================================

@app.route(
    "/anonymous-chat/history"
)
def anonymous_chat_history():

    return jsonify({

        "success":
            True,

        "messages":
            session.get(
                "chat_history",
                []
            )

    })


# ============================================================
# CLEAR CHAT
# ============================================================

@app.route(
    "/anonymous-chat/clear",
    methods=["POST"]
)
def clear_chat():

    session[
        "chat_history"
    ] = []

    return jsonify({

        "success":
            True

    })


# ============================================================
# SAFE LOCATION / HELP
# ============================================================

@app.route("/safe-location")
def safe_location():

    return render_template(
        "safe_location.html"
    )


# ============================================================
# SOS 112
# ============================================================

@app.route("/sos")
def sos():

    return redirect(
        "https://112.gov.in/"
    )


# ============================================================
# OFFICER / HUMAN REVIEW
#
# Kept as an alias so an old result-page button
# pointing to /officer-dashboard will still work.
# ============================================================

@app.route("/officer-dashboard")
def officer_dashboard():

    result_data = session.get(
        "assessment_result"
    )

    if result_data is None:

        return redirect(
            "/assessment"
        )

    return render_template(

        "review.html",

        result=result_data,

        case_id=session.get(
            "case_id",
            "TA-DEMO001"
        )

    )


# ============================================================
# SAVE RESULT
# ============================================================

@app.route(
    "/save-result",
    methods=["POST"]
)
def save_result():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "success":
                False,

            "message":
                "No assessment result received."

        }), 400

    session[
        "assessment_result"
    ] = data

    return jsonify({

        "success":
            True,

        "message":
            "Assessment result saved."

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "application":
            "Trauma Assessment",

        "status":
            "running",

        "ai_model":
            "joeddav/distilbert-base-uncased-go-emotions-student",

        "ai_model_ready":
            AI_MODEL_READY,

        "language":
            session.get(
                "language",
                "English"
            )

    })


# ============================================================
# BREATHING EXERCISE
# ============================================================

@app.route("/breathing")
def breathing():

    return render_template(
        "breathing.html"
    )


# ============================================================
# CALM FOCUS GAME
# ============================================================

@app.route("/game", methods=["GET"])
def game():

    return render_template(
        "game.html"
    )


# ============================================================
# MUSIC LISTENING PATTERN
# ============================================================

@app.route("/spotify", methods=["GET"])
def spotify():

    return render_template(
        "spotify.html"
    )


@app.route("/spotify/analyze", methods=["POST"])
def spotify_analyze():

    raw_score = request.form.get(
        "music_score",
        "40"
    )

    try:
        music_score = float(raw_score)
    except (ValueError, TypeError):
        music_score = 40.0

    music_score = max(
        0,
        min(100, music_score)
    )

    music_result = {
        "score": round(music_score, 2),
        "tracks_analyzed": 20,
        "repeated_tracks": 6,
        "average_listening": "42 min",
        "late_day_plays": 8
    }

    session["music_result"] = music_result
    session.modified = True

    return render_template(
        "spotify_result.html",
        result=music_result
    )


# ============================================================
# 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """

    <!DOCTYPE html>

    <html>

    <head>

        <title>404 - Page Not Found</title>

        <style>

            body {
                font-family: Arial;
                text-align: center;
                padding: 80px;
                background: #f7f8fc;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                text-decoration: none;
                font-weight: bold;
                color: #6246ea;
            }

        </style>

    </head>

    <body>

        <h1>404 - Page Not Found</h1>

        <p>
            The requested page does not exist.
        </p>

        <a href="/assessment">
            ← Back to Assessment
        </a>

    </body>

    </html>

    """, 404


# ============================================================
# 500
# ============================================================

@app.errorhandler(500)
def internal_error(error):

    return """

    <!DOCTYPE html>

    <html>

    <head>

        <title>500 - Server Error</title>

    </head>

    <body>

        <h1>500 - Server Error</h1>

        <p>
            Something went wrong.
        </p>

        <a href="/assessment">
            ← Back to Assessment
        </a>

    </body>

    </html>

    """, 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
