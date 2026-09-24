import os
import numpy as np
import librosa

from transformers import pipeline


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"


print("Loading voice emotion AI...")


classifier = pipeline(

    "audio-classification",

    model=MODEL_NAME

)


# ============================================================
# ANALYZE VOICE
# ============================================================

def analyze_voice(audio_file):

    print("Reading audio...")


    # ========================================================
    # CHECK FILE
    # ========================================================

    if not os.path.exists(audio_file):

        raise FileNotFoundError(

            f"Voice file not found: {audio_file}"

        )


    # ========================================================
    # LOAD AUDIO
    # ========================================================

    y, sr = librosa.load(

        audio_file,

        sr=16000,

        mono=True

    )


    if len(y) == 0:

        raise ValueError(
            "Audio file is empty."
        )


    duration = len(y) / sr


    print(
        f"Audio loaded successfully!"
    )

    print(
        f"Duration: {duration:.2f} seconds"
    )


    # ========================================================
    # EMOTION ANALYSIS
    # ========================================================

    print("Analyzing voice emotion...")


    results = classifier(

        audio_file

    )


    emotions = {}


    for item in results:

        label = item["label"].lower()

        score = float(
            item["score"]
        ) * 100


        # ----------------------------------------------------
        # Normalize emotion names
        # ----------------------------------------------------

        if label in [
            "sad",
            "sadness"
        ]:

            label = "sad"


        elif label in [
            "happy",
            "happiness"
        ]:

            label = "hap"


        elif label in [
            "neutral"
        ]:

            label = "neu"


        elif label in [
            "angry",
            "anger"
        ]:

            label = "ang"


        elif label in [
            "fear",
            "fearful"
        ]:

            label = "fear"


        emotions[label] = round(

            score,

            2

        )


    # ========================================================
    # GET EMOTION VALUES
    # ========================================================

    sad = emotions.get(
        "sad",
        0
    )


    happy = emotions.get(
        "hap",
        0
    )


    neutral = emotions.get(
        "neu",
        0
    )


    angry = emotions.get(
        "ang",
        0
    )


    fear = emotions.get(
        "fear",
        0
    )


    # ========================================================
    # ACOUSTIC ANALYSIS
    # ========================================================

    print("Analyzing pitch...")


    # --------------------------------------------------------
    # PITCH
    # --------------------------------------------------------

    try:

        pitch, magnitude = librosa.piptrack(

            y=y,

            sr=sr

        )


        pitch_values = []


        for i in range(
            pitch.shape[1]
        ):

            index = np.argmax(

                magnitude[:, i]

            )


            value = pitch[
                index,
                i
            ]


            if value > 0:

                pitch_values.append(
                    value
                )


        if pitch_values:

            average_pitch = float(

                np.mean(
                    pitch_values
                )

            )


            pitch_variation = float(

                np.std(
                    pitch_values
                )

            )

        else:

            average_pitch = 0

            pitch_variation = 0


    except Exception:

        average_pitch = 0

        pitch_variation = 0


    # ========================================================
    # VOICE ENERGY
    # ========================================================

    rms = librosa.feature.rms(

        y=y

    )[0]


    voice_energy = float(

        np.mean(
            rms
        )

    )


    # ========================================================
    # PAUSE RATIO
    # ========================================================

    intervals = librosa.effects.split(

        y,

        top_db=30

    )


    voiced_samples = 0


    for start, end in intervals:

        voiced_samples += (

            end - start

        )


    total_samples = len(y)


    if total_samples > 0:

        pause_ratio = (

            1 -

            (
                voiced_samples /
                total_samples
            )

        ) * 100

    else:

        pause_ratio = 0


    # ========================================================
    # VOICE DISTRESS SCORE
    # ========================================================

    # This is a prototype acoustic/emotion indicator.
    #
    # It combines:
    #
    # Fear       → strong distress signal
    # Sadness    → distress signal
    # Anger      → distress signal
    # Pauses     → possible hesitation/distress signal
    # Pitch      → supporting acoustic signal
    #
    # It is NOT a psychological diagnosis.


    emotion_distress = (

        (fear * 0.45)

        +

        (sad * 0.30)

        +

        (angry * 0.15)

        +

        (pause_ratio * 0.10)

    )


    # --------------------------------------------------------
    # If the model doesn't provide fear,
    # sadness + acoustic signals still contribute.
    # --------------------------------------------------------

    voice_distress = max(

        0,

        min(

            100,

            emotion_distress

        )

    )


    # ========================================================
    # DISTRESS LEVEL
    # ========================================================

    if voice_distress >= 70:

        distress_level = "HIGH"


    elif voice_distress >= 40:

        distress_level = "MODERATE"


    else:

        distress_level = "LOW"


    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "voice_distress":
            round(
                voice_distress,
                2
            ),

        "distress_score":
            round(
                voice_distress,
                2
            ),

        "distress_level":
            distress_level,

        "emotions":
            emotions,

        "average_pitch":
            round(
                average_pitch,
                2
            ),

        "pitch_variation":
            round(
                pitch_variation,
                2
            ),

        "voice_energy":
            round(
                voice_energy,
                4
            ),

        "pause_ratio":
            round(
                pause_ratio,
                2
            ),

        "duration":
            round(
                duration,
                2
            )

    }


    # ========================================================
    # TERMINAL DISPLAY
    # ========================================================

    print()
    print("=" * 40)
    print("       🎙️ VOICE ASSESSMENT")
    print("=" * 40)

    print()

    print("🧠 Emotion Analysis")


    for emotion, value in emotions.items():

        print(
            f"{emotion}: {value:.2f}%"
        )


    print()

    print("📈 Acoustic Analysis")

    print(
        f"Average pitch: "
        f"{average_pitch:.2f} Hz"
    )

    print(
        f"Pitch variation: "
        f"{pitch_variation:.2f}"
    )

    print(
        f"Voice energy: "
        f"{voice_energy:.4f}"
    )

    print(
        f"Pause ratio: "
        f"{pause_ratio:.2f}%"
    )


    print()

    print("=" * 40)

    print("      🚨 VOICE DISTRESS")

    print("=" * 40)

    print(
        f"Level: "
        f"{distress_level}"
    )

    print(
        f"Indicator score: "
        f"{voice_distress:.2f} / 100"
    )

    print()

    print(
        "⚠️ This is an AI-generated "
        "indicator, not a psychological "
        "diagnosis."
    )

    print()


    return result


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    audio_file = "voice.wav"


    if not os.path.exists(audio_file):

        print(
            "❌ voice.wav was not found."
        )

        print(
            "Place your audio file in "
            "E:\\TraumaAssessment"
        )

    else:

        analyze_voice(
            audio_file
        )
