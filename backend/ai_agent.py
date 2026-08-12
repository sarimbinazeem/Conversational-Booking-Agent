"""
ai_agent.py

AI logic for the car wash booking assistant.

This file handles:

1. Extracting structured booking information.
2. Generating natural conversational responses.

The AI does NOT directly create bookings.
Booking creation is controlled by conversation.py.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# AI CLIENT
# =========================================================

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a friendly AI booking assistant for a car wash service.

Your job is to help customers collect the information required
to book a car wash appointment.

A booking requires exactly these five pieces of information:

1. customer_name
2. vehicle_type
3. preferred_date
4. preferred_time
5. contact_details

Rules:

- Be friendly and conversational.
- Understand natural human language.
- Never invent booking information.
- Never guess a customer's name.
- Never change a customer's name.
- Preserve customer-provided information exactly whenever possible.
- Ask only for information that is still missing.
- Do not repeatedly ask for information already provided.
- If the customer corrects information, use the corrected information.
- If a date or time is unclear, ask for clarification.
- Once all required information is collected, provide a concise summary.
- Never claim that a booking has been confirmed.
- Only the application backend can confirm a booking.
"""


# =========================================================
# EXTRACT BOOKING INFORMATION
# =========================================================

def extract_booking_information(user_message, current_booking):
    """
    Extract booking information explicitly present
    in the customer's latest message.

    The current booking is provided only as context.
    It must NOT be copied into the extraction result
    unless the customer explicitly mentions it again.
    """

    prompt = f"""
You are a STRICT booking information extraction system.

Extract ONLY information explicitly stated in the customer's
LATEST message.

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

1. Look ONLY at the latest customer message.

2. NEVER invent, guess, infer, or assume information.

3. Do not copy values from the current booking.

4. If a value is not explicitly stated in the latest message,
   return null.

5. If the customer explicitly corrects an existing value,
   return the new corrected value.

6. A person's name belongs in customer_name.

7. Vehicle names and types belong in vehicle_type.

8. Dates such as:
   today
   tomorrow
   Monday
   Friday
   this Friday
   next Friday

   belong in preferred_date.

9. Times such as:
   3 PM
   5 PM
   10:30 AM
   noon
   afternoon

   belong in preferred_time.

10. If date and time occur together, extract both.

Example:

"I want to come Friday at 3 PM."

Return:

"preferred_date": "Friday"
"preferred_time": "3 PM"

11. Do not include "at" in the time.

12. Phone numbers and email addresses belong in
    contact_details.

13. Preserve names exactly as provided.

Example:

Customer:
"Arin"

Return:

"customer_name": "Arin"

NOT:

"Aaron"

14. Preserve phone numbers exactly as provided.

Example:

"03361251259"

Return:

"03361251259"

15. Greetings such as:
   hello
   hi
   thanks
   okay
   goodbye

   should return null for every field unless
   booking information is also explicitly included.

16. Return ONLY valid JSON.

Use exactly these keys:

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

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "AI returned an empty extraction response."
        )

    return json.loads(content)


# =========================================================
# GENERATE CONVERSATIONAL RESPONSE
# =========================================================

def generate_booking_response(user_message, booking):
    """
    Generate the conversational response after
    the latest customer message.

    This function does not create or confirm bookings.
    """

    booking_data = {
        "customer_name": booking.customer_name,
        "vehicle_type": booking.vehicle_type,
        "preferred_date": booking.preferred_date,
        "preferred_time": booking.preferred_time,
        "contact_details": booking.contact_details
    }

    prompt = f"""
The customer just sent:

"{user_message}"

Current booking information:

{json.dumps(booking_data, indent=2)}

Required information:

1. customer_name
2. vehicle_type
3. preferred_date
4. preferred_time
5. contact_details

Your job is to continue the conversation naturally.

Rules:

1. If customer_name is missing, ask for the customer's name.

2. If vehicle_type is missing, ask what type of vehicle
   they have.

3. If preferred_date is missing, ask what day they want
   the car wash.

4. If preferred_time is missing, ask what time they prefer.

5. If contact_details is missing, ask for a phone number
   or email.

6. Ask ONLY for missing information.

7. Never ask again for information already present.

8. If multiple pieces of information were provided,
   acknowledge them naturally and ask only for the
   remaining missing information.

9. If the customer simply says hello and no booking
   information exists, greet them and explain that
   you can help book a car wash.

10. If all five fields are available, DO NOT say that
    the booking is confirmed.

11. The application will separately generate the final
    confirmation summary.

12. Keep responses concise and natural.

Return ONLY the message to send to the customer.
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

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "AI returned an empty conversational response."
        )

    return content.strip()