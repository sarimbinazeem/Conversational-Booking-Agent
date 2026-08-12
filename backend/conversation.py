"""
conversation.py

Manages the state and workflow of one customer conversation.

Workflow:

1. Collect booking information
2. Ask for missing information
3. Present complete booking summary
4. Wait for explicit confirmation
5. Confirm or modify booking

The conversation layer controls booking confirmation.
The AI does not directly create bookings.
"""

from backend.booking import Booking

from backend.ai_agent import (
    extract_booking_information,
    generate_booking_response
)

from backend.database import create_booking


class Conversation:

    def __init__(self, session_id):
        self.session_id = session_id
        self.booking = Booking()

    # =====================================================
    # CHECK WHETHER BOOKING IS COMPLETE
    # =====================================================

    def is_booking_complete(self):
        return self.booking.is_complete()

    # =====================================================
    # GET CURRENT BOOKING STATE
    # =====================================================

    def get_booking_data(self):

        return {
            "customer_name": self.booking.customer_name,
            "vehicle_type": self.booking.vehicle_type,
            "preferred_date": self.booking.preferred_date,
            "preferred_time": self.booking.preferred_time,
            "contact_details": self.booking.contact_details,
            "booking_status": self.booking.booking_status,
            "awaiting_confirmation":
                self.booking.awaiting_confirmation
        }

    # =====================================================
    # PROCESS CUSTOMER MESSAGE
    # =====================================================

    def process_message(self, user_message):

        user_message = user_message.strip()

        if not user_message:
            return {
                "response": (
                    "Please tell me how I can help you "
                    "with your car wash booking."
                ),
                "booking": self.booking
            }

        # -------------------------------------------------
        # STEP 1
        # Handle confirmation state FIRST
        # -------------------------------------------------

        if self.booking.awaiting_confirmation:

            confirmation = self.detect_confirmation(
                user_message
            )

            # ---------------------------------------------
            # FINAL YES
            # ---------------------------------------------

            if confirmation == "yes":

                return self.confirm_booking()

            # ---------------------------------------------
            # FINAL NO
            # ---------------------------------------------

            if confirmation == "no":

                self.booking.awaiting_confirmation = False
                self.booking.booking_status = "collecting"

                return {
                    "response": (
                        "No problem. What would you like "
                        "to change about the booking?"
                    ),
                    "booking": self.booking
                }

            # ---------------------------------------------
            # UNKNOWN RESPONSE
            # ---------------------------------------------

            return {
                "response": (
                    "Please reply with yes to confirm the "
                    "booking, or no if you'd like to make "
                    "a change."
                ),
                "booking": self.booking
            }

        # -------------------------------------------------
        # STEP 2
        # Store current booking state
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
        # Extract information from latest message
        # -------------------------------------------------

        try:

            extracted_information = (
                extract_booking_information(
                    user_message,
                    current_booking
                )
            )

        except Exception as error:

            print(
                "AI extraction error:",
                str(error)
            )

            return {
                "response": (
                    "Sorry, I had trouble understanding "
                    "that. Could you please try again?"
                ),
                "booking": self.booking
            }

        # -------------------------------------------------
        # STEP 4
        # Update booking information
        # -------------------------------------------------

        self.update_booking(
            extracted_information
        )

        # -------------------------------------------------
        # STEP 5
        # Check completeness
        # -------------------------------------------------

        if self.is_booking_complete():

            # The summary has now been generated.
            # Only AFTER this point can a later
            # confirmation message create a booking.

            self.booking.awaiting_confirmation = True
            self.booking.booking_status = (
                "awaiting_confirmation"
            )

            return {
                "response": self.generate_summary(),
                "booking": self.booking
            }

        # -------------------------------------------------
        # STEP 6
        # Continue collecting information
        # -------------------------------------------------

        self.booking.awaiting_confirmation = False
        self.booking.booking_status = "collecting"

        try:

            response = generate_booking_response(
                user_message,
                self.booking
            )

        except Exception as error:

            print(
                "AI response generation error:",
                str(error)
            )

            response = self.fallback_missing_information()

        return {
            "response": response,
            "booking": self.booking
        }

    # =====================================================
    # UPDATE BOOKING
    # =====================================================

    def update_booking(self, extracted_information):
        """
        Update only fields explicitly extracted from
        the customer's latest message.

        This prevents already-known information from
        being accidentally overwritten with null.
        """

        fields = [
            "customer_name",
            "vehicle_type",
            "preferred_date",
            "preferred_time",
            "contact_details"
        ]

        changed = False

        for field in fields:

            value = extracted_information.get(field)

            if value is not None:

                setattr(
                    self.booking,
                    field,
                    value
                )

                changed = True

        # If information was changed, make sure an old
        # confirmation state cannot remain active.

        if changed:
            self.booking.awaiting_confirmation = False

            if self.booking.booking_status != "confirmed":
                self.booking.booking_status = "collecting"

    # =====================================================
    # GENERATE BOOKING SUMMARY
    # =====================================================

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

    # =====================================================
    # DETECT CONFIRMATION
    # =====================================================

    def detect_confirmation(self, message):
        """
        Detect an explicit yes/no response.

        This function is ONLY called when a complete
        booking summary has already been presented.
        """

        normalized = (
            message
            .lower()
            .strip()
        )

        # Exact/common confirmation phrases.

        yes_phrases = {
            "yes",
            "yes please",
            "yes, please",
            "yeah",
            "yeah please",
            "yep",
            "yup",
            "sure",
            "confirm",
            "confirmed",
            "please confirm",
            "go ahead",
            "go ahead please",
            "that's correct",
            "that is correct",
            "correct",
            "book it",
            "please book it",
            "do it"
        }

        no_phrases = {
            "no",
            "nope",
            "no thanks",
            "no thank you",
            "cancel",
            "change",
            "modify"
        }

        if normalized in yes_phrases:
            return "yes"

        if normalized in no_phrases:
            return "no"

        return "unknown"

    # =====================================================
    # CONFIRM BOOKING
    # =====================================================

    def confirm_booking(self):
        """
        Create the database booking ONLY after:

        1. All required information exists.
        2. The summary was already presented.
        3. The customer explicitly confirmed it.
        """

        # Safety check #1
        if not self.booking.is_complete():

            self.booking.awaiting_confirmation = False
            self.booking.booking_status = "collecting"

            return {
                "response": (
                    "I still need some booking information "
                    "before I can confirm the appointment."
                ),
                "booking": self.booking
            }

        # Safety check #2
        #
        # This method should only be reached when
        # awaiting_confirmation is True.
        if not self.booking.awaiting_confirmation:

            return {
                "response": (
                    "I need to show you the complete booking "
                    "summary before I can confirm it."
                ),
                "booking": self.booking
            }

        # -------------------------------------------------
        # CREATE DATABASE BOOKING
        # -------------------------------------------------

        try:

            booking_id = create_booking(
                session_id=self.session_id,
                customer_name=self.booking.customer_name,
                vehicle_type=self.booking.vehicle_type,
                preferred_date=self.booking.preferred_date,
                preferred_time=self.booking.preferred_time,
                contact_details=self.booking.contact_details
            )

        except Exception as error:

            print(
                "BOOKING DATABASE ERROR:",
                str(error)
            )

            # IMPORTANT:
            # Never mark the booking confirmed if
            # database creation failed.

            self.booking.booking_status = (
                "awaiting_confirmation"
            )
            self.booking.awaiting_confirmation = True

            return {
                "response": (
                    "I couldn't complete the booking "
                    "right now. Please try again."
                ),
                "booking": self.booking
            }

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        self.booking.booking_id = booking_id
        self.booking.booking_status = "confirmed"
        self.booking.awaiting_confirmation = False

        return {
            "response": self.generate_confirmation_message(),
            "booking": self.booking
        }

    # =====================================================
    # FALLBACK MISSING INFORMATION RESPONSE
    # =====================================================

    def fallback_missing_information(self):

        missing = self.booking.missing_fields()

        if not missing:

            return self.generate_summary()

        field_questions = {
            "customer_name":
                "May I have your name?",
            "vehicle_type":
                "What type of vehicle do you have?",
            "preferred_date":
                "What day would you like the car wash?",
            "preferred_time":
                "What time would you prefer?",
            "contact_details":
                "What phone number or email should I use?"
        }

        return field_questions[missing[0]]

    # =====================================================
    # FINAL CONFIRMATION MESSAGE
    # =====================================================

    def generate_confirmation_message(self):

        return (
            "Your car wash appointment has been confirmed!\n\n"
            f"Booking ID: {self.booking.booking_id}\n"
            f"Name: {self.booking.customer_name}\n"
            f"Vehicle: {self.booking.vehicle_type}\n"
            f"Date: {self.booking.preferred_date}\n"
            f"Time: {self.booking.preferred_time}\n\n"
            "Thank you for choosing our car wash service!"
        )