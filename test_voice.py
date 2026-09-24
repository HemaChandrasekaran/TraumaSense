import librosa
import numpy as np

audio_file = "voice.wav"

y, sr = librosa.load(audio_file, sr=None)

# Pitch
pitch = librosa.yin(y, fmin=70, fmax=400)

# Energy
energy = np.mean(librosa.feature.rms(y=y))

# Speaking-related spectral information
spectral_centroid = np.mean(
    librosa.feature.spectral_centroid(y=y, sr=sr)
)

print("🎙️ VOICE ANALYSIS")
print("----------------------")
print("Sample rate:", sr)
print("Audio duration:", round(len(y) / sr, 2), "seconds")
print("Average pitch:", round(float(np.nanmean(pitch)), 2), "Hz")
print("Voice energy:", round(float(energy), 4))
print("Spectral centroid:", round(float(spectral_centroid), 2))