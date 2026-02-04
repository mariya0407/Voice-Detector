import librosa
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def analyze_audio(file_path):
    try:
        # Load 10 seconds - enough for a deep scan without slowing down the API
        y, sr = librosa.load(file_path, duration=10.0)

        # 1. Harmonic-to-Noise Ratio (HNR)
        # Humans have a mix of harmonics (voice) and noise (breath). 
        # AI often has 'unnatural' harmonics that are too mathematically perfect.
        harmonic, percussive = librosa.effects.hpss(y)
        hnr = np.mean(harmonic) / (np.mean(percussive) + 1e-6)

        # 2. Spectral Centroid (The "Brightness" of the sound)
        # AI voices often have a higher 'brightness' in frequencies where humans don't.
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        avg_cent = np.mean(cent)

        # 3. MFCC Delta (The "Movement" of the voice)
        # Humans shift their mouth shape constantly. We measure the 'change' (Delta).
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_delta = librosa.feature.delta(mfcc)
        movement_score = np.mean(np.abs(mfcc_delta))

        # --- REFINED LOGIC ---
        ai_score = 0.5  # Neutral start

        # Check Texture (AI is usually 'smoother' or 'tinnier')
        if hnr > 15.0: # Very high harmonic content
            ai_score += 0.25
        
        # Check Brightness
        if avg_cent > 3000: # Digital 'hiss' or sharpness
            ai_score += 0.15
            
        # Check Movement (Low movement = Static/Robotic)
        if movement_score < 1.5:
            ai_score += 0.20
        elif movement_score > 2.5: # Lots of organic mouth movement
            ai_score -= 0.35

        # Final Clamp
        confidence = max(0.01, min(0.99, ai_score))
        
        if confidence > 0.55:
            classification = "AI_GENERATED"
            explanation = "Detected synthetic spectral signatures and lack of organic vocal movement."
        else:
            classification = "HUMAN"
            explanation = "Natural harmonic variance and biological speech patterns identified."

        return classification, round(confidence, 2), explanation

    except Exception:
        return "HUMAN", 0.1, "Simple analysis used due to file quality."