"""
booking.py

Defines the booking data structure used throughout
the conversational booking workflow.
"""

from dataclasses import dataclass


@dataclass
class Booking:

    # Database booking ID for database
    booking_id: int | None = None

    # Required booking information
    customer_name: str | None = None
    vehicle_type: str | None = None
    preferred_date: str | None = None
    preferred_time: str | None = None
    contact_details: str | None = None

    # Booking workflow state for confirmation state
    booking_status: str = "collecting"
    awaiting_confirmation: bool = False