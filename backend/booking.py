"""
booking.py

a structure of one booking having all the CONVERSATION STATE required for the booking

"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Booking:
    #Optional[str] means that a state can be a string but right now its empty
    customer_name: Optional[str] = None
    vehicle_type: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    contact_details: Optional[str] = None

    # Booking workflow state
    #if a customer confirms the status become confirm
    
    booking_status: str = "collecting"
    awaiting_confirmation: bool = False

    #return a missing state list that is missing from the current conversation and are required for booking
    def missing_fields(self):
        missing = []

        if not self.customer_name:
            missing.append("customer_name")

        if not self.vehicle_type:
            missing.append("vehicle_type")

        if not self.preferred_date:
            missing.append("preferred_date")

        if not self.preferred_time:
            missing.append("preferred_time")

        if not self.contact_details:
            missing.append("contact_details")

        return missing

    #if there are no missing fields left then the booking is completed
    def is_complete(self):
        return len(self.missing_fields()) == 0