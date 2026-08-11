"""
whatsapp.py

WhatsApp communication adapter.

This file connects the existing booking workflow
to a WhatsApp API provider.

The booking logic itself remains inside Conversation.
"""

import os
import requests

from dotenv import load_dotenv

from backend.session_manager import SessionManager


# Load environment variables
load_dotenv()


class WhatsAppAgent:

    def __init__(self):

        """
        Create the WhatsApp agent.

        The agent owns the WhatsApp conversation sessions
        and contains the provider-specific sending logic.
        """

        self.session_manager = SessionManager()

        self.api_key = os.getenv("VAPI_API_KEY")

        self.base_url = os.getenv(
            "VAPI_BASE_URL",
            "https://api.wapi.io"
        )

        self.send_endpoint = os.getenv(
            "VAPI_SEND_ENDPOINT",
            "/v1/send"
        )

    # ---------------------------------------------------------
    # PROCESS INCOMING MESSAGE
    # ---------------------------------------------------------

    def process_message(self, sender_id, message):

        """
        Process a WhatsApp message.

        sender_id:
            WhatsApp customer's unique identifier.

        message:
            Text sent by the customer.
        """

        # Get the customer's existing conversation.
        conversation = self.session_manager.get_conversation(
            sender_id
        )

        # Send the message into our existing
        # booking conversation workflow.
        result = conversation.process_message(
            message
        )

        return result

    # ---------------------------------------------------------
    # SEND WHATSAPP MESSAGE
    # ---------------------------------------------------------

    def send_message(self, recipient, message):

        """
        Send a text message through VAPI.
        """

        if not self.api_key:

            raise RuntimeError(
                "VAPI_API_KEY is missing from .env"
            )

        #left side of base url / right side of send endpoint
        url = (
            self.base_url.rstrip("/")
            + "/"
            + self.send_endpoint.lstrip("/")
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "to": recipient,
            "message": message
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        #if there is an error it raises it
        response.raise_for_status()

        #converts json into object
        return response.json()