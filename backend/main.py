"""
main.py

FastAPI server for the car wash booking system.

This backend provides:

- Health checking
- Direct booking creation
- Booking retrieval
- Conversational booking
- Session-based conversation management
- Vapi voice webhook integration
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from backend.booking import Booking
from backend.conversation import Conversation
from backend.session_manager import SessionManager

from backend.database import (
    initialize_database,
    create_booking,
    get_booking,
    get_all_bookings
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Car Wash Booking API",
    description=(
        "Backend for WhatsApp and Voice car wash "
        "booking agents"
    ),
    version="1.0.0"
)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# REQUEST MODELS
# =========================================================

class BookingRequest(BaseModel):
    """
    Structure required when creating a booking directly.
    """

    customer_name: str
    vehicle_type: str
    preferred_date: str
    preferred_time: str
    contact_details: str


class ChatRequest(BaseModel):
    """
    Structure used by conversational agents.

    session_id identifies the customer conversation.
    message contains the customer's latest message.
    """

    session_id: str
    message: str


# =========================================================
# SESSION MANAGER
# =========================================================

session_manager = SessionManager()


# =========================================================
# HELPER FUNCTION
# =========================================================

def booking_to_dict(booking):
    """
    Convert a Booking object into a normal dictionary.

    This makes the API response easier to read.
    """

    return {
        "booking_id": booking.booking_id,
        "customer_name": booking.customer_name,
        "vehicle_type": booking.vehicle_type,
        "preferred_date": booking.preferred_date,
        "preferred_time": booking.preferred_time,
        "contact_details": booking.contact_details,
        "booking_status": booking.booking_status,
        "awaiting_confirmation": booking.awaiting_confirmation
    }


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Car Wash Booking API is running."
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# DIRECT BOOKING CREATION
# =========================================================

@app.post("/bookings")
def create_direct_booking(request: BookingRequest):

    booking = Booking(
        customer_name=request.customer_name,
        vehicle_type=request.vehicle_type,
        preferred_date=request.preferred_date,
        preferred_time=request.preferred_time,
        contact_details=request.contact_details
    )

    # Check whether all required fields exist.
    if not booking.is_complete():

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Booking is incomplete.",
                "missing_fields": booking.missing_fields()
            }
        )

    # Save confirmed booking into SQLite.
    booking_id = create_booking(
        session_id="direct_api",
        customer_name=booking.customer_name,
        vehicle_type=booking.vehicle_type,
        preferred_date=booking.preferred_date,
        preferred_time=booking.preferred_time,
        contact_details=booking.contact_details
    )

    booking.booking_id = booking_id
    booking.booking_status = "confirmed"

    return {
        "message": "Booking created successfully.",
        "booking": booking_to_dict(booking)
    }


# =========================================================
# CONVERSATIONAL CHAT ENDPOINT
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    """
    Main conversational endpoint.

    Example request:

    {
        "session_id": "user_123",
        "message": "My name is Ahmed"
    }
    """

    # Get the conversation belonging to this session.
    conversation = session_manager.get_conversation(
        request.session_id
    )

    # Process the customer's latest message.
    result = conversation.process_message(
        request.message
    )

    return {
        "message": result["response"],
        "booking": booking_to_dict(
            result["booking"]
        )
    }


# =========================================================
# GET ONE BOOKING
# =========================================================

@app.get("/bookings/{booking_id}")
def booking_details(booking_id: int):

    booking = get_booking(booking_id)

    if booking is None:

        return {
            "message": "Booking not found."
        }

    return {
        "booking": booking
    }


# =========================================================
# GET ALL BOOKINGS
# =========================================================

@app.get("/bookings")
def all_bookings():

    return {
        "bookings": get_all_bookings()
    }


# =========================================================
# VAPI WEBHOOK
# =========================================================

@app.post("/webhooks/vapi")
async def vapi_webhook(request: Request):

    # Read the raw request body
    body = await request.body()

    print("\n========== VAPI WEBHOOK ==========")
    print("Headers:", dict(request.headers))
    print("Raw body:", body.decode("utf-8", errors="replace"))
    print("==================================\n")

    return {
        "status": "received"
    }