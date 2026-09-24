# ============================================================
# TEXT + VOICE FUSION ENGINE
# ============================================================


def calculate_fusion(text_result, voice_result):

    # ========================================================
    # TEXT SVI
    # ========================================================

    text_score = 0.0

    if text_result:

        text_score = float(
            text_result.get(
                "svi",
                0
            )
        )


    # Keep score between 0 and 100

    text_score = max(
        0,
        min(
            100,
            text_score
        )
    )


    # ========================================================
    # VOICE DISTRESS SCORE
    # ========================================================

    voice_score = 0.0

    if voice_result:

        raw_voice_score = float(

            voice_result.get(
                "distress_score",
                0
            )

        )


        # Convert 0–8 into 0–100

        voice_score = (
            raw_voice_score / 8
        ) * 100


    voice_score = max(
        0,
        min(
            100,
            voice_score
        )
    )


    # ========================================================
    # COMBINED SVI
    # ========================================================

    if text_result and voice_result:

        # Text contributes 60%
        # Voice contributes 40%

        combined_score = (

            text_score * 0.60

            +

            voice_score * 0.40

        )

    elif text_result:

        combined_score = text_score

    elif voice_result:

        combined_score = voice_score

    else:

        combined_score = 0


    combined_score = max(
        0,
        min(
            100,
            combined_score
        )
    )


    # ========================================================
    # FINAL RISK LEVEL
    # ========================================================

    if combined_score >= 70:

        level = "HIGH"

    elif combined_score >= 40:

        level = "MODERATE"

    else:

        level = "LOW"


    # ========================================================
    # SIGNAL AGREEMENT
    # ========================================================

    if text_result and voice_result:

        difference = abs(
            text_score -
            voice_score
        )


        if difference <= 15:

            signal = "STRONG AGREEMENT"

        elif difference <= 30:

            signal = "PARTIAL AGREEMENT"

        else:

            signal = "DIFFERENT SIGNALS"


    elif text_result:

        signal = "TEXT ONLY"

    elif voice_result:

        signal = "VOICE ONLY"

    else:

        signal = "NO DATA"


    # ========================================================
    # EXPLANATION
    # ========================================================

    explanation = []


    if text_result:

        explanation.append(

            f"Text-based SVI: "
            f"{text_score:.2f}/100."

        )


        # Existing explanation

        if text_result.get(
            "svi_explanation"
        ):

            explanation.append(

                text_result[
                    "svi_explanation"
                ]

            )


    if voice_result:

        explanation.append(

            f"Voice distress indicator: "
            f"{voice_score:.2f}/100."

        )


        # Pause

        pause_ratio = float(

            voice_result.get(
                "pause_ratio",
                0
            )

        )


        if pause_ratio >= 40:

            explanation.append(

                "Higher pause activity "
                "was detected in the recording."

            )


        # Pitch

        pitch_variation = float(

            voice_result.get(
                "pitch_variation",
                0
            )

        )


        if pitch_variation >= 50:

            explanation.append(

                "Higher pitch variation "
                "was detected."

            )


        # Sadness

        emotions = voice_result.get(
            "emotions",
            {}
        )


        sad_score = float(

            emotions.get(
                "sad",
                0
            )

        )


        if sad_score >= 40:

            explanation.append(

                "A strong sadness-related "
                "voice signal was detected."

            )


    # ========================================================
    # SAFETY FLAG
    # ========================================================

    safety_flag = False


    if text_result:

        safety_flag = bool(

            text_result.get(
                "safety_flag",
                False
            )

        )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "text_svi":
            round(
                text_score,
                2
            ),

        "voice_score":
            round(
                voice_score,
                2
            ),

        "combined_svi":
            round(
                combined_score,
                2
            ),

        "level":
            level,

        "signal":
            signal,

        "safety_flag":
            safety_flag,

        "explanation":
            explanation

    }