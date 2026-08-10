"""
main.py

Starting the FAST API Server that have routers like /booking 
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.booking import Booking
from backend.storage import save_booking, load_booking
from backend.conversation import Conversation

#creating the application
app = FastAPI(
    title="Car Wash Booking API",
    description="Backend for WhatsApp and Voice car wash booking agents",
    version="1.0.0"
)

#BASE MODEL Class that gives a format of the booking 
class BookingRequest(BaseModel):
    customer_name: str
    vehicle_type: str
    preferred_date: str
    preferred_time: str
    contact_details: str

class ChatRequest(BaseModel):
    message: str

#only one user chat 
conversation = Conversation()

#================Routers====================================

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

#/POST endpoint to post bookings
@app.post("/bookings")
def create_booking(request: BookingRequest):

    #create a Booking Class and save it
    booking = Booking(
        customer_name=request.customer_name,
        vehicle_type=request.vehicle_type,
        preferred_date=request.preferred_date,
        preferred_time=request.preferred_time,
        contact_details=request.contact_details
    )
    
    #if the booking have missing details then raise an error 
    if not booking.is_complete():
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Booking is incomplete.",
                "missing_fields": booking.missing_fields()
            }
        )

    save_booking(booking)

    return {
        "message": "Booking created successfully.",
        "booking": booking
    }

#/GET endpoint to retreive bookings
@app.get("/bookings")
def get_bookings():
    return {
        "bookings": load_booking()
    }

@app.post("/chat")
def chat(request: ChatRequest):

    result = conversation.process_message(request.message)

    return {
        "message": result["response"],
        "booking": result["booking"]
    }