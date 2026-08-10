"""
ai_agent.py

AI logic for the car wash booking assistant.

This file handles:
1. Extracting structured booking information.
2. Generating natural conversational responses.
"""

import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()


# Groq provides an OpenAI-compatible API.
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a friendly AI booking assistant for a car wash service.

Your job is to help customers book a car wash appointment.

A booking requires these five pieces of information:

1. customer_name
2. vehicle_type
3. preferred_date
4. preferred_time
5. contact_details

You should:

- Be friendly and conversational.
- Understand natural human language.
- Extract information from customer messages.
- Never invent booking information.
- Ask only for information that is still missing.
- Do not repeatedly ask for information already provided.
- If a date or time is unclear, ask the customer to clarify.
- If the customer corrects information, use the corrected information.
- Once all required information is collected, show a summary.
- Ask the customer for confirmation before considering the booking confirmed.
- Never claim a booking is confirmed unless the customer explicitly confirms it.
"""


# ---------------------------------------------------------
# EXTRACT BOOKING INFORMATION
# ---------------------------------------------------------

def extract_booking_information(user_message, current_booking):
    """
    Extract booking information from the customer's latest message.

    Only information explicitly provided in the latest message
    should be extracted.
    """

    prompt = f"""
You are a STRICT information extraction system.

Your ONLY job is to extract booking information that is
EXPLICITLY stated in the customer's LATEST message.

Current booking state:

{json.dumps(current_booking, indent=2)}

LATEST CUSTOMER MESSAGE:

{user_message}

The booking fields are:

- customer_name
- vehicle_type
- preferred_date
- preferred_time
- contact_details

IMPORTANT RULES:

1. Look ONLY at the latest customer message when deciding
   what information was provided.

2. NEVER invent, guess, assume, or create information.

3. If the customer says something unrelated such as
   "hello", "hi", "thanks", "okay", or "goodbye",
   return null for every field.

4. If information is not explicitly present in the latest
   message, return null for that field.

5. Words and phrases such as "tomorrow", "today", "Monday",
   "Friday", "this Friday", or "next Friday" represent DATE
   information and belong in preferred_date.

6. Expressions such as "5 PM", "at 5 PM", "3 PM",
   "around 10:30 AM", "at noon", or "in the afternoon"
   represent TIME information and belong in preferred_time.

7. When date and time appear together in the same sentence,
   extract BOTH.

   Example:
   "I'd like to come Friday at 3 PM."

   MUST produce:

   "preferred_date": "Friday"
   "preferred_time": "3 PM"

8. Do not treat the word "at" as part of the time value.
   Store "3 PM", not "at 3 PM".

9. Vehicle names such as "Toyota Corolla", "Honda Civic",
   "SUV", or "sedan" belong in vehicle_type.

10. A person's name belongs in customer_name.

11. A phone number or email belongs in contact_details.

12. If the customer corrects something, return the corrected value.

13. Do not copy information from the current booking unless
    the customer explicitly mentions or corrects it in the latest message.

Return ONLY valid JSON.

Use EXACTLY these keys:

{{
    "customer_name": null,
    "vehicle_type": null,
    "preferred_date": null,
    "preferred_time": null,
    "contact_details": null
}}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    return json.loads(
        response.choices[0].message.content
    )

# GENERATE CONVERSATIONAL RESPONSE


def generate_booking_response(user_message, booking):
    """
    Generate the natural language response that the customer
    should receive after their latest message.
    """

    booking_data = {
        "customer_name": booking.customer_name,
        "vehicle_type": booking.vehicle_type,
        "preferred_date": booking.preferred_date,
        "preferred_time": booking.preferred_time,
        "contact_details": booking.contact_details
    }

    prompt = f"""
The customer just sent this message:

"{user_message}"

The current booking information is:

{json.dumps(booking_data, indent=2)}

Your job is to continue the conversation naturally.

The required booking information is:

1. customer_name
2. vehicle_type
3. preferred_date
4. preferred_time
5. contact_details

Follow these rules:

1. If customer_name is missing, ask for the customer's name.

2. If customer_name is available but vehicle_type is missing,
   ask what type of vehicle they have.

3. If customer_name and vehicle_type are available but
   preferred_date is missing, ask what day they want the wash.

4. If the date is available but preferred_time is missing,
   ask what time they prefer.

5. If everything except contact_details is available,
   ask for a phone number or email.

6. If all five fields are available, provide a short booking
   summary and ask the customer to confirm it.

7. Do not claim that the appointment is confirmed yet.

8. Do not ask for information that is already available.

9. Be friendly and concise.

10. If the customer simply says hello and no booking information
    exists, greet them and explain that you can help book a car wash.

11. If the customer says something like "thanks", respond naturally
    while keeping the booking conversation moving if necessary.

Return ONLY the message that should be sent to the customer.
Do not return JSON.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()