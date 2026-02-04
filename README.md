# Veritas AI: Multi-Language Voice Detection API

Veritas AI is a secure REST API designed to distinguish between **Human** and **AI-Generated** voices. It specifically supports five languages: Tamil, English, Hindi, Malayalam, and Telugu.

## 🚀 Features
* **Multi-Language Support:** Optimized for Dravidian and Indo-Aryan linguistic patterns.
* **Deep Audio Analysis:** Uses MFCC variance, Pitch Standard Deviation, and Harmonic-to-Noise Ratio (HNR).
* **Secure API:** Protected via `x-api-key` header validation.
* **Elegant Frontend:** A glassmorphism-style web interface for easy testing.

## 🛠️ Tech Stack
* **Backend:** FastAPI (Python)
* **AI Logic:** Librosa & NumPy
* **Frontend:** HTML5 / CSS3 (Glassmorphism) / Vanilla JS

## 📂 Folder Structure
```text
VoiceDetector/
├── main.py           # FastAPI Server & Routes
├── brain.py          # Audio Analysis Logic
├── static/
│   └── index.html    # Web Interface
├── requirements.txt  # Python Dependencies
└── Procfile          # Deployment Instructions for Cloud

#Installation & Setup

Clone the repo: git clone https://github.com/your-username/VoiceDetector.git

Install deps: pip install -r requirements.txt

Run: uvicorn main:app --reload