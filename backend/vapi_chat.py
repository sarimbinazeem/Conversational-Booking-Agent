import os
import requests

from dotenv import load_dotenv

load_dotenv()


VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

VAPI_CHAT_URL = "https://api.vapi.ai/chat"


def send_message_to_vapi(message, session_id):
    """
    Send a text message to the Vapi Car Wash assistant.

    session_id keeps the WhatsApp customer's
    conversation associated with the same session.
    """

    if not VAPI_API_KEY:
        raise RuntimeError("VAPI_API_KEY is missing from .env")

    if not VAPI_ASSISTANT_ID:
        raise RuntimeError("VAPI_ASSISTANT_ID is missing from .env")

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "assistantId": VAPI_ASSISTANT_ID,
        "input": message,
        "sessionId": session_id
    }

    response = requests.post(
        VAPI_CHAT_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    return response.json()