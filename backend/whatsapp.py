"""
whatsapp.py

WhatsApp communication adapter.

This module connects the WhatsApp channel to the existing
conversational booking workflow.

WhatsApp/WAPI is responsible only for communication.

The actual booking intelligence remains inside:

WhatsApp
    ↓
WhatsAppAgent
    ↓
Conversation
    ↓
AI Agent
    ↓
Database
"""

import os
import requests

from dotenv import load_dotenv

from backend.session_manager import SessionManager


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# WHATSAPP AGENT
# =========================================================

class WhatsAppAgent:

    def __init__(self):
        """
        Create the WhatsApp agent.

        Each WhatsApp customer gets their own conversation
        session.
        """

        self.session_manager = SessionManager()

        # -------------------------------------------------
        # WAPI configuration
        # -------------------------------------------------

        self.api_key = os.getenv("WAPI_API_KEY")

        self.base_url = os.getenv(
            "WAPI_BASE_URL",
            "https://api.wapi.io"
        )

        self.send_endpoint = os.getenv(
            "WAPI_SEND_ENDPOINT",
            "/v1/send"
        )


    # =====================================================
    # PROCESS INCOMING MESSAGE
    # =====================================================

    def process_message(self, sender_id, message):
        """
        Process an incoming WhatsApp text message.

        sender_id:
            Unique WhatsApp identifier for the customer.

        message:
            Text sent by the customer.

        The message is passed directly into the SAME
        Conversation workflow used by the rest of the
        application.
        """

        if not sender_id:
            raise ValueError(
                "sender_id is required"
            )

        if not message:
            raise ValueError(
                "message is required"
            )

        # -------------------------------------------------
        # Get customer's conversation
        # -------------------------------------------------

        conversation = self.session_manager.get_conversation(
            sender_id
        )

        # -------------------------------------------------
        # Process through existing booking logic
        # -------------------------------------------------

        result = conversation.process_message(
            message
        )

        return result


    # =====================================================
    # SEND WHATSAPP MESSAGE
    # =====================================================

    def send_message(self, recipient, message):
        """
        Send a text message through WAPI.
        """

        if not self.api_key:
            raise RuntimeError(
                "WAPI_API_KEY is missing from .env"
            )

        if not recipient:
            raise ValueError(
                "recipient is required"
            )

        if not message:
            raise ValueError(
                "message is required"
            )

        # -------------------------------------------------
        # Build WAPI endpoint
        # -------------------------------------------------

        url = (
            self.base_url.rstrip("/")
            + "/"
            + self.send_endpoint.lstrip("/")
        )

        # -------------------------------------------------
        # Authentication
        # -------------------------------------------------

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # -------------------------------------------------
        # Message payload
        #
        # Keep this isolated here because this is the
        # provider-specific part of the application.
        # -------------------------------------------------

        payload = {
            "to": recipient,
            "message": message
        }

        # -------------------------------------------------
        # Send request
        # -------------------------------------------------

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()