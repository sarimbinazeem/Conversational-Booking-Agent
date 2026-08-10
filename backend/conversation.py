"""
conversation.py

Manages the state and workflow of one customer conversation.

The workflow is:

1. Collect booking information
2. Ask for missing information
3. Present booking summary
4. Ask for confirmation
5. Confirm or modify booking
"""

from backend.booking import Booking

from backend.ai_agent import (
    extract_booking_information,
    generate_booking_response
)
from backend.database import create_booking

class Conversation:

    def __init__(self,session_id):
        self.session_id = session_id
        self.booking = Booking()

    # CHECK WHETHER ALL REQUIRED INFORMATION EXISTS

    def is_booking_complete(self):

        return all([
            self.booking.customer_name,
            self.booking.vehicle_type,
            self.booking.preferred_date,
            self.booking.preferred_time,
            self.booking.contact_details
        ])
    # GET CURRENT BOOKING STATE


    def get_booking_data(self):

        return {
            "customer_name": self.booking.customer_name,
            "vehicle_type": self.booking.vehicle_type,
            "preferred_date": self.booking.preferred_date,
            "preferred_time": self.booking.preferred_time,
            "contact_details": self.booking.contact_details,
            "booking_status": self.booking.booking_status,
            "awaiting_confirmation": self.booking.awaiting_confirmation
        }

    # PROCESS CUSTOMER MESSAGE

    def process_message(self, user_message):

        # Check whether we are waiting for confirmation.


        if self.booking.awaiting_confirmation:

            confirmation = self.detect_confirmation(user_message)

            #if there is confirmation then save trhe booking in the database
            if confirmation == "yes":
                booking_id = create_booking(
                    session_id=self.session_id,
                    customer_name=self.booking.customer_name,
                    vehicle_type=self.booking.vehicle_type,
                    preferred_date=self.booking.preferred_date,
                    preferred_time=self.booking.preferred_time,
                    contact_details=self.booking.contact_details
                )

                self.booking.booking_id = booking_id
                self.booking.booking_status = "confirmed"
                self.booking.awaiting_confirmation = False

                return {
                    "response": self.generate_confirmation_message(),
                    "booking": self.booking
                }

            elif confirmation == "no":

                self.booking.awaiting_confirmation = False

                response = (
                    "No problem. What would you like to change "
                    "about the booking?"
                )

                return {
                    "response": response,
                    "booking": self.booking
                }

        # -------------------------------------------------
        # STEP 2
        # Current booking state
        # -------------------------------------------------

        current_booking = {
            "customer_name": self.booking.customer_name,
            "vehicle_type": self.booking.vehicle_type,
            "preferred_date": self.booking.preferred_date,
            "preferred_time": self.booking.preferred_time,
            "contact_details": self.booking.contact_details
        }

        # -------------------------------------------------
        # STEP 3
        # Extract new information
        # -------------------------------------------------

        extracted_information = extract_booking_information(
            user_message,
            current_booking
        )

        # -------------------------------------------------
        # STEP 4
        # Update booking state
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
        # STEP 5
        # Check if all information has been collected.
        # -------------------------------------------------

        if self.is_booking_complete():

            self.booking.awaiting_confirmation = True

            self.booking.booking_status = "awaiting_confirmation"

            response = self.generate_summary()

        else:

            self.booking.awaiting_confirmation = False

            self.booking.booking_status = "collecting"

            response = generate_booking_response(
                user_message,
                self.booking
            )

        # -------------------------------------------------
        # STEP 6
        # Return result
        # -------------------------------------------------

        return {
            "response": response,
            "booking": self.booking
        }

    # GENERATE BOOKING SUMMARY

    def generate_summary(self):

        return (
            "Perfect! I have all the information I need.\n\n"
            "Here is your booking summary:\n\n"
            f"Name: {self.booking.customer_name}\n"
            f"Vehicle: {self.booking.vehicle_type}\n"
            f"Date: {self.booking.preferred_date}\n"
            f"Time: {self.booking.preferred_time}\n"
            f"Contact: {self.booking.contact_details}\n\n"
            "Would you like me to confirm this booking?"
        )

    # DETECT YES / NO CONFIRMATION

    def detect_confirmation(self, message):

        normalized = message.lower().strip()

        yes_words = [
            "yes",
            "yeah",
            "yep",
            "yup",
            "sure",
            "confirm",
            "confirmed",
            "please confirm",
            "go ahead",
            "that's correct",
            "correct"
        ]

        no_words = [
            "no",
            "nope",
            "don't",
            "do not",
            "cancel",
            "change",
            "modify"
        ]

        for word in yes_words:
            if word in normalized:
                return "yes"

        for word in no_words:
            if word in normalized:
                return "no"

        return "unknown"

    # FINAL CONFIRMATION MESSAGE


    def generate_confirmation_message(self):

        return (
            "Your car wash appointment has been confirmed! "
            f"We'll see you on {self.booking.preferred_date} "
            f"at {self.booking.preferred_time}. "
            "Thank you for choosing our car wash service!"
        )