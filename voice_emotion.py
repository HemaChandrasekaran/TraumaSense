import librosa
import numpy as np
from transformers import pipeline


# -------------------------------------------------
# LOAD VOICE EMOTION MODEL
# -------------------------------------------------

print("Loading voice emotion model...")

voice_classifier = pipeline(
    "audio-classification",
    model="superb/hubert-base-superb-er"
)


# -------------------------------------------------
# VOICE ANALYSIS FUNCTION
# -------------------------------------------------

def analyze_voice(audio_file):

    # ---------------------------------------------
    # LOAD AUDIO
    # ---------------------------------------------

    audio, sample_rate = librosa.load(
        audio_file,
        sr=16000,
        mono=True
    )


    duration = (
        len(audio) / sample_rate
    )


    # ---------------------------------------------
    # AI EMOTION ANALYSIS
    # ---------------------------------------------

    results = voice_classifier({

        "raw": audio,

        "sampling_rate":
            sample_rate

    })


    emotions = {}


    for result in results:

        emotions[
            result["label"]
        ] = round(
            result["score"] * 100,
            2
        )


    # ---------------------------------------------
    # PITCH ANALYSIS
    # ---------------------------------------------

    pitch = librosa.yin(

        audio,

        fmin=70,

        fmax=400,

        sr=sample_rate

    )


    pitch = pitch[
        np.isfinite(pitch)
    ]


    if len(pitch) > 0:

        average_pitch = float(
            np.mean(pitch)
        )

        pitch_variation = float(
            np.std(pitch)
        )

    else:

        average_pitch = 0

        pitch_variation = 0


    # ---------------------------------------------
    # VOICE ENERGY
    # ---------------------------------------------

    rms = librosa.feature.rms(
        y=audio
    )[0]


    average_energy = float(
        np.mean(rms)
    )


    # ---------------------------------------------
    # PAUSE ANALYSIS
    # ---------------------------------------------

    silence_threshold = 0.01


    silent_frames = (
        rms < silence_threshold
    )


    pause_ratio = float(

        np.mean(
            silent_frames
        ) * 100

    )


    # ---------------------------------------------
    # DISTRESS INDICATOR
    # ---------------------------------------------

    distress_points = 0


    sad_score = emotions.get(
        "sad",
        0
    )


    angry_score = emotions.get(
        "ang",
        0
    )


    # Sadness

    if sad_score >= 40:

        distress_points += 2

    elif sad_score >= 25:

        distress_points += 1


    # Anger

    if angry_score >= 30:

        distress_points += 2

    elif angry_score >= 15:

        distress_points += 1


    # Pauses

    if pause_ratio >= 40:

        distress_points += 2

    elif pause_ratio >= 25:

        distress_points += 1


    # Pitch variation

    if pitch_variation >= 50:

        distress_points += 2

    elif pitch_variation >= 30:

        distress_points += 1


    # ---------------------------------------------
    # DISTRESS LEVEL
    # ---------------------------------------------

    if distress_points >= 5:

        distress_level = "HIGH"

    elif distress_points >= 3:

        distress_level = "MODERATE"

    else:

        distress_level = "LOW"


    # ---------------------------------------------
    # RETURN RESULT
    # ---------------------------------------------

    return {

        "emotions":
            emotions,

        "duration":
            round(
                duration,
                2
            ),

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
                average_energy,
                4
            ),

        "pause_ratio":
            round(
                pause_ratio,
                2
            ),

        "distress_level":
            distress_level,

        "distress_score":
            distress_points

    }