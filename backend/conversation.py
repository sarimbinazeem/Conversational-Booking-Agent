"""
conversation.py

Manages the state and flow of one customer conversation.
"""

from backend.booking import Booking

from backend.ai_agent import (
    extract_booking_information,
    generate_booking_response
)


class Conversation:

    def __init__(self):
        # Create an empty booking state.
        self.booking = Booking()

    def process_message(self, user_message):

        # -------------------------------------------------
        # STEP 1 — Create current state dictionary
        # -------------------------------------------------

        current_booking = {
            "customer_name": self.booking.customer_name,
            "vehicle_type": self.booking.vehicle_type,
            "preferred_date": self.booking.preferred_date,
            "preferred_time": self.booking.preferred_time,
            "contact_details": self.booking.contact_details
        }

        # -------------------------------------------------
        # STEP 2 — Extract information from latest message
        # -------------------------------------------------

        extracted_information = extract_booking_information(
            user_message,
            current_booking
        )

        # -------------------------------------------------
        # STEP 3 — Update only fields that contain new data
        # -------------------------------------------------

        if extracted_information.get("customer_name") is not None:
            self.booking.customer_name = (
                extracted_information["customer_name"]
            )

        if extracted_information.get("vehicle_type") is not None:
            self.booking.vehicle_type = (
                extracted_information["vehicle_type"]
            )

        if extracted_information.get("preferred_date") is not None:
            self.booking.preferred_date = (
                extracted_information["preferred_date"]
            )

        if extracted_information.get("preferred_time") is not None:
            self.booking.preferred_time = (
                extracted_information["preferred_time"]
            )

        if extracted_information.get("contact_details") is not None:
            self.booking.contact_details = (
                extracted_information["contact_details"]
            )

        # -------------------------------------------------
        # STEP 4 — Generate conversational response
        # -------------------------------------------------

        response = generate_booking_response(
            user_message,
            self.booking
        )

        # Return both the updated booking state
        # and the natural language response.
        return {
            "response": response,
            "booking": self.booking
        }