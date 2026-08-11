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

class VapiBookingRequest(BaseModel):
    """
    Structured booking data sent by the Vapi voice agent.
    """

    session_id: str
    customer_name: str
    vehicle_type: str
    preferred_date: str
    preferred_time: str
    contact_details: str

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

    data = await request.json()

    message = data.get("message", {})

    event_type = message.get("type", "unknown")

    # -----------------------------------------------------
    # Ignore events other than end-of-call reports
    # -----------------------------------------------------

    if event_type != "end-of-call-report":

        print(f"\n[VAPI] Event received: {event_type}")

        return {
            "status": "received",
            "event": event_type
        }

    # -----------------------------------------------------
    # Extract call information
    # -----------------------------------------------------

    call = message.get("call", {})

    call_id = call.get("id", "unknown")

    ended_reason = message.get(
        "endedReason",
        "unknown"
    )

    duration = message.get(
        "durationSeconds",
        0
    )

    # -----------------------------------------------------
    # Extract transcript
    # -----------------------------------------------------

    transcript = message.get(
        "transcript",
        ""
    )

    # -----------------------------------------------------
    # Display clean report
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("                 VAPI CALL REPORT")
    print("=" * 60)

    print(f"Call ID:       {call_id}")
    print(f"End reason:    {ended_reason}")
    print(f"Duration:      {duration} seconds")

    print("\n--- TRANSCRIPT ---")

    if transcript:
        print(transcript)
    else:
        print("No transcript available.")

    print("=" * 60)
    print()

    return {
        "status": "received",
        "event": event_type,
        "call_id": call_id
    }

# =========================================================
# VAPI BOOKING TOOL
# =========================================================

# =========================================================
# VAPI BOOKING TOOL
# =========================================================

@app.post("/vapi/tools/create-booking")
async def vapi_create_booking(request: Request):

    data = await request.json()

    print("\n")
    print("=" * 60)
    print("              VAPI TOOL CALL")
    print("=" * 60)

    print("Raw Vapi tool request:")
    print(data)

    message = data.get("message", {})

    # -----------------------------------------------------
    # Check event type
    # -----------------------------------------------------

    event_type = message.get("type")

    if event_type != "tool-calls":

        print(f"Unexpected Vapi event: {event_type}")
        print("=" * 60)

        # End-of-call and other events don't need a tool result.
        return {
            "results": []
        }

    # -----------------------------------------------------
    # Get tool calls
    # -----------------------------------------------------

    tool_calls = message.get("toolCallList", [])

    results = []

    # -----------------------------------------------------
    # Process each tool call
    # -----------------------------------------------------

    for tool_call in tool_calls:

        tool_call_id = tool_call.get("id")

        # Vapi normally sends name directly.
        # Some payload variants may expose it through function.
        tool_name = tool_call.get("name")

        if not tool_name:
            function_data = tool_call.get("function", {})
            tool_name = function_data.get("name")

        # -------------------------------------------------
        # Get arguments
        # -------------------------------------------------

        arguments = tool_call.get("arguments")

        if arguments is None:
            arguments = tool_call.get("parameters")

        if arguments is None:
            function_data = tool_call.get("function", {})
            arguments = function_data.get("arguments", {})

        # Arguments can sometimes arrive as a JSON string.
        if isinstance(arguments, str):

            try:
                import json
                arguments = json.loads(arguments)

            except Exception:

                print("Failed to parse tool arguments:")
                print(arguments)

                arguments = {}

        if not isinstance(arguments, dict):
            arguments = {}

        print("\nTool name:", tool_name)
        print("Tool call ID:", tool_call_id)
        print("Arguments:", arguments)

        # -------------------------------------------------
        # Make sure this is our booking tool
        # -------------------------------------------------

        if tool_name != "create_booking":

            results.append({
                "toolCallId": tool_call_id,
                "result": (
                    f"Unknown tool: {tool_name}"
                )
            })

            continue

        # -------------------------------------------------
        # Extract booking information
        # -------------------------------------------------

        session_id = arguments.get("session_id")

        if not session_id:
            session_id = message.get(
                "call",
                {}
            ).get(
                "id",
                "unknown"
            )

        customer_name = arguments.get(
            "customer_name"
        )

        vehicle_type = arguments.get(
            "vehicle_type"
        )

        preferred_date = arguments.get(
            "preferred_date"
        )

        preferred_time = arguments.get(
            "preferred_time"
        )

        contact_details = arguments.get(
            "contact_details"
        )

        # -------------------------------------------------
        # Print extracted information
        # -------------------------------------------------

        print("\nExtracted booking information:")
        print("Customer:", customer_name)
        print("Vehicle:", vehicle_type)
        print("Date:", preferred_date)
        print("Time:", preferred_time)
        print("Contact:", contact_details)
        print("Session:", session_id)

        # -------------------------------------------------
        # Create Booking object
        # -------------------------------------------------

        booking = Booking(
            customer_name=customer_name,
            vehicle_type=vehicle_type,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            contact_details=contact_details
        )

        # -------------------------------------------------
        # Validate booking
        # -------------------------------------------------

        if not booking.is_complete():

            missing_fields = booking.missing_fields()

            print(
                f"Booking incomplete. Missing: {missing_fields}"
            )

            results.append({
                "toolCallId": tool_call_id,
                "result": (
                    "Booking is incomplete. "
                    f"Missing fields: {', '.join(missing_fields)}"
                )
            })

            continue

        # -------------------------------------------------
        # Save booking
        # -------------------------------------------------

        try:

            booking_id = create_booking(
                session_id=session_id,
                customer_name=booking.customer_name,
                vehicle_type=booking.vehicle_type,
                preferred_date=booking.preferred_date,
                preferred_time=booking.preferred_time,
                contact_details=booking.contact_details
            )

        except Exception as e:

            print("\nBOOKING DATABASE ERROR:")
            print(str(e))

            results.append({
                "toolCallId": tool_call_id,
                "result": (
                    "Booking could not be created because "
                    "the backend encountered an error."
                )
            })

            continue

        # -------------------------------------------------
        # Update booking object
        # -------------------------------------------------

        booking.booking_id = booking_id
        booking.booking_status = "confirmed"
        booking.awaiting_confirmation = False

        # -------------------------------------------------
        # Print successful booking
        # -------------------------------------------------

        print("\n")
        print("-" * 60)
        print("             BOOKING CREATED")
        print("-" * 60)

        print(f"Booking ID:     {booking.booking_id}")
        print(f"Customer:       {booking.customer_name}")
        print(f"Vehicle:        {booking.vehicle_type}")
        print(f"Date:           {booking.preferred_date}")
        print(f"Time:           {booking.preferred_time}")
        print(f"Contact:        {booking.contact_details}")
        print(f"Status:         {booking.booking_status}")

        print("-" * 60)

        # -------------------------------------------------
        # Send result back to Vapi
        # -------------------------------------------------

        results.append({
            "toolCallId": tool_call_id,
            "result": (
                "Booking created successfully. "
                f"Booking ID: {booking.booking_id}. "
                f"Customer: {booking.customer_name}. "
                f"Vehicle: {booking.vehicle_type}. "
                f"Date: {booking.preferred_date}. "
                f"Time: {booking.preferred_time}."
            )
        })

    print("=" * 60)
    print()

    return {
        "results": results
    }