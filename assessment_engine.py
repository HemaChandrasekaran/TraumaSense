from transformers import pipeline


# ============================================================
# LOAD PRETRAINED EMOTION MODEL
# ============================================================

classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)


# ============================================================
# AI TEXT ANALYSIS
# ============================================================

def analyze_text(text):

    # Get emotion results
    results = classifier(text)[0]

    emotions = {}

    for result in results:
        emotions[result["label"]] = result["score"]


    # --------------------------------------------------------
    # IMPORTANT EMOTIONS
    # --------------------------------------------------------

    fear = emotions.get("fear", 0)

    nervousness = emotions.get("nervousness", 0)

    sadness = emotions.get("sadness", 0)


    # --------------------------------------------------------
    # PROTOTYPE SCORES
    # --------------------------------------------------------

    stress = (
        nervousness * 0.6 +
        fear * 0.4
    ) * 100


    fear_score = fear * 100


    anxiety = (
        nervousness * 0.7 +
        fear * 0.3
    ) * 100


    trauma_distress = (
        sadness * 0.5 +
        fear * 0.5
    ) * 100


    # --------------------------------------------------------
    # VULNERABILITY DETECTION
    # --------------------------------------------------------

    vulnerability_words = [

        "threatened",
        "unsafe",
        "alone",
        "helpless",
        "displaced",
        "afraid",
        "danger"

    ]


    text_lower = text.lower()


    vulnerability_count = 0


    for word in vulnerability_words:

        if word in text_lower:

            vulnerability_count += 1


    vulnerability = min(
        vulnerability_count * 15,
        100
    )


    # --------------------------------------------------------
    # SAFETY INDICATOR DETECTION
    # --------------------------------------------------------

    safety_words = [

        "threatened",
        "unsafe",
        "danger",
        "kill",
        "murder",
        "attack",
        "harm",
        "violence"

    ]


    safety_indicators = []


    for word in safety_words:

        if word in text_lower:

            safety_indicators.append(word)


    safety_flag = len(
        safety_indicators
    ) > 0


    # --------------------------------------------------------
    # SVI CALCULATION
    # --------------------------------------------------------

    svi = (

        stress +
        fear_score +
        anxiety +
        trauma_distress +
        vulnerability

    ) / 5


    # --------------------------------------------------------
    # RISK CATEGORY
    # --------------------------------------------------------

    if svi <= 25:

        risk = "LOW"

    elif svi <= 50:

        risk = "MODERATE"

    elif svi <= 75:

        risk = "HIGH"

    else:

        risk = "CRITICAL"


    # --------------------------------------------------------
    # SVI CONTRIBUTION
    # --------------------------------------------------------

    contributions = {

        "Stress": round(stress / 5, 2),

        "Fear": round(fear_score / 5, 2),

        "Anxiety": round(anxiety / 5, 2),

        "Trauma Distress":
            round(trauma_distress / 5, 2),

        "Vulnerability":
            round(vulnerability / 5, 2)

    }


    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    highest_factor = max(
        contributions,
        key=contributions.get
    )


    explanation = (
        f"{highest_factor} is the largest "
        f"contributor to the current SVI."
    )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {

        "stress": round(
            stress,
            2
        ),

        "fear": round(
            fear_score,
            2
        ),

        "anxiety": round(
            anxiety,
            2
        ),

        "trauma_distress": round(
            trauma_distress,
            2
        ),

        "vulnerability": round(
            vulnerability,
            2
        ),

        "svi": round(
            svi,
            2
        ),

        "risk": risk,

        "safety_flag":
            safety_flag,

        "safety_indicators":
            safety_indicators,

        "svi_contributions":
            contributions,

        "svi_explanation":
            explanation

    }


# ============================================================
# SUPPORT RECOMMENDATIONS
# ============================================================

def get_recommendations(result):

    recommendations = []


    # High fear or safety indicators

    if (
        result["fear"] >= 60
        or result["safety_flag"]
    ):

        recommendations.append(
            "Safety assessment"
        )


    # Moderate or high stress

    if result["stress"] >= 40:

        recommendations.append(
            "Counselling assessment"
        )


    # High vulnerability

    if result["vulnerability"] >= 30:

        recommendations.append(
            "Legal assistance assessment"
        )


    # High overall risk

    if result["svi"] >= 75:

        recommendations.append(
            "Priority human review"
        )


    # Default

    if not recommendations:

        recommendations.append(
            "Standard human review"
        )


    return recommendations


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    text = input(
        "Enter victim's statement: "
    )


    result = analyze_text(
        text
    )


    print("\n--- AI ASSESSMENT ---")


    print(
        "Stress:",
        result["stress"]
    )

    print(
        "Fear:",
        result["fear"]
    )

    print(
        "Anxiety:",
        result["anxiety"]
    )

    print(
        "Trauma Distress:",
        result["trauma_distress"]
    )

    print(
        "Vulnerability:",
        result["vulnerability"]
    )


    print(
        "\nSVI:",
        result["svi"],
        "/ 100"
    )


    print(
        "Risk Level:",
        result["risk"]
    )


    print(
        "\n--- SVI CONTRIBUTION ---"
    )


    for factor, value in result[
        "svi_contributions"
    ].items():

        print(
            factor,
            ":",
            value
        )


    print(
        "\nExplanation:",
        result["svi_explanation"]
    )


    if result["safety_flag"]:

        print(
            "\n⚠️ Safety Indicators:",
            ", ".join(
                result["safety_indicators"]
            )
        )
