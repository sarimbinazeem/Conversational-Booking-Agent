import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

url = "https://api.vapi.ai/chat"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "assistantId": ASSISTANT_ID,
    "input": "Hi, I want to book a car wash."
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

print("Status:", response.status_code)
print("Response:")
print(response.text)