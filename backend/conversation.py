"""
conversation.py

this is a conversaiton manager

"""

from backend.booking import Booking
from backend.ai_agent import extract_booking_information

#For conversational states memory
class Conversation:
    
    def __init__(self):
        #a booking dataclass
        self.booking = Booking()

    def process_message(self, user_message):

        current_booking = {
            "customer_name": self.booking.customer_name,
            "vehicle_type": self.booking.vehicle_type,
            "preferred_date": self.booking.preferred_date,
            "preferred_time": self.booking.preferred_time,
            "contact_details": self.booking.contact_details
        }
        
        # Ask the LLM to extract information from the
        # customer's latest message.
        extracted_information = extract_booking_information(
            user_message,
            current_booking
        )

        # IMPORTANT:
        # Only update a field if the LLM actually extracted
        # a value for that field.
        #
        # This prevents previously collected information
        # from being accidentally replaced with None.

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

        return self.booking