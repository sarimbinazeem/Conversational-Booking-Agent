"""
booking.py

Defines the booking data structure used throughout
the conversational booking workflow.
"""

from dataclasses import dataclass


@dataclass
class Booking:

    # Database booking ID
    booking_id: int | None = None

    # Required booking information
    customer_name: str | None = None
    vehicle_type: str | None = None
    preferred_date: str | None = None
    preferred_time: str | None = None
    contact_details: str | None = None

    # Booking workflow state
    #
    # Possible states:
    # collecting
    # awaiting_confirmation
    # confirmed
    # cancelled
    booking_status: str = "collecting"

    # True only after the complete booking summary
    # has been presented to the customer.
    awaiting_confirmation: bool = False

    # =====================================================
    # CHECK WHETHER BOOKING IS COMPLETE
    # =====================================================

    def is_complete(self) -> bool:
        """
        Return True when all required booking
        information has been collected.
        """

        return all([
            self.customer_name,
            self.vehicle_type,
            self.preferred_date,
            self.preferred_time,
            self.contact_details
        ])

    # =====================================================
    # FIND MISSING INFORMATION
    # =====================================================

    def missing_fields(self) -> list[str]:
        """
        Return a list containing all required fields
        that are still missing.
        """

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

    # =====================================================
    # RESET CONFIRMATION STATE
    # =====================================================

    def reset_confirmation(self):
        """
        Reset the confirmation workflow.

        This is used when the customer changes
        booking information.
        """

        self.awaiting_confirmation = False

        if self.booking_status != "confirmed":
            self.booking_status = "collecting"