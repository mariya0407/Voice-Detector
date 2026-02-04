import requests
import base64
import json

# CONFIGURATION
API_URL = "http://127.0.0.1:8000/api/voice-detection"
API_KEY = "sk_test_123456789"
AUDIO_FILE = "sample.mp3"  # Make sure this file exists in your folder!

def send_request():
    try:
        # 1. Read the MP3 file and convert to Base64
        with open(AUDIO_FILE, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')

        # 2. Prepare the JSON Payload
        payload = {
            "language": "English",
            "audioFormat": "mp3",
            "audioBase64": encoded_string
        }

        # 3. Prepare Headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }

        # 4. Send the POST Request
        print("🚀 Sending request to API...")
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

        # 5. Print the Result
        print("\n📬 Response Received:")
        print(json.dumps(response.json(), indent=4))

    except FileNotFoundError:
        print(f"❌ Error: Could not find '{AUDIO_FILE}'. Please add an MP3 file to the folder.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_request()