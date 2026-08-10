"""
ai_agent.py

Handles communication with Groq's LLM and extracts
structured booking information from customer messages.
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


SYSTEM_PROMPT = """
You are a friendly AI booking assistant for a car wash service.

Your job is to help customers book a car wash appointment.

The booking requires these five pieces of information:

1. customer_name
2. vehicle_type
3. preferred_date
4. preferred_time
5. contact_details

Your responsibilities:

- Understand natural human language.
- Extract booking information from the customer's message.
- If the customer provides multiple pieces of information,
  extract all of them.
- Do not ask for information that has already been provided.
- Never invent booking information.
- If a date or time is unclear, do not guess.
- Ask the customer to clarify unclear information.
- If the customer corrects previously provided information,
  use the new information.

Important:

You are extracting information for the application.
Do not confirm a booking yourself.
The application will handle booking confirmation.
"""


def extract_booking_information(user_message, current_booking):

    """
    Extract booking information from the customer's latest message.

    user_message:
        The customer's latest message.

    current_booking:
        Information already collected during this conversation.

    Returns:
        A dictionary containing booking fields.
    """


    prompt = f"""
    You are a STRICT information extraction system.

    Your ONLY job is to extract booking information that is
    EXPLICITLY stated in the customer's LATEST message.

    The customer needs to provide:

    - customer_name
    - vehicle_type
    - preferred_date
    - preferred_time
    - contact_details

    Current booking state:

    {json.dumps(current_booking, indent=2)}

    LATEST CUSTOMER MESSAGE:

    {user_message}

    IMPORTANT RULES:

    1. Look ONLY at the LATEST CUSTOMER MESSAGE when deciding
    which values to extract.

    2. NEVER invent, guess, assume, or create information.

    3. If the customer says something unrelated such as:
    "hello", "hi", "thanks", "okay", "yes", or "goodbye",
    return null for EVERY field.

    4. If a piece of information is NOT explicitly present
    in the latest message, return null for that field.

    5. "tomorrow", "today", "Monday", "Friday", etc. are DATE
    information and MUST go into preferred_date.

    6. "5 PM", "at noon", "10:30 AM", etc. are TIME
    information and MUST go into preferred_time.

    7. A vehicle such as "Toyota Corolla", "Honda Civic",
    "SUV", or "sedan" belongs in vehicle_type.

    8. A person's name belongs in customer_name.

    9. A phone number, email address, or other contact information
    belongs in contact_details.

    10. If the customer corrects something, return the corrected
        value.

    11. Do NOT copy values from the current booking into the
        response unless the customer mentions or corrects that
        information in the latest message.

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

    # Groq returns the model's JSON response as a string.
    # Convert that string into a Python dictionary.
    return json.loads(
        response.choices[0].message.content
    )