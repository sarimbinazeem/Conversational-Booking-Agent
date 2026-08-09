"""
storage.py

stores the booking in json format so that it can be retrieved later on

"""

import json
from pathlib import Path
from dataclasses import asdict
from backend.booking import Booking

#the json that have the conversational states
BOOKINGS_FILE = Path(__file__).parent / "bookings.json"

def load_booking():
    if not BOOKINGS_FILE.exists():
        return []

    with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_booking(booking: Booking):
    bookings = load_booking()

    #store the booking as a dictironary 
    bookings.append(asdict(booking))

    with open(BOOKINGS_FILE,"w",encoding="utf-8") as file:
        json.dump(bookings,file,indent=4)

    return booking

