# AI Conversational Booking Agents

## Overview

This project implements two AI-powered booking agents for a car wash service:

1. WhatsApp Booking Agent
2. Voice Calling Booking Agent (Vapi)

Both agents collect:

- Customer Name
- Vehicle Type
- Preferred Date
- Preferred Time
- Contact Details

Bookings are stored in SQLite.

---

## Technologies Used

- Python
- FastAPI
- SQLite
- Groq LLM
- Vapi Voice AI
- WhatsApp Cloud API
- Cloudflare Tunnel

---

## Project Structure

backend/
├── ai_agent.py
├── booking.py
├── conversation.py
├── database.py
├── main.py
├── session_manager.py
├── storage.py
├── whatsapp.py

---

## WhatsApp Agent

The WhatsApp agent receives customer messages through the WhatsApp Cloud API webhook.

Workflow:

Customer Message
→ FastAPI Webhook
→ Conversation Manager
→ AI Booking Agent
→ WhatsApp Reply

---

## Voice Agent

The voice agent is built using Vapi.

Workflow:

Phone Call
→ Vapi Assistant
→ Booking Information Collection
→ Tool Call
→ FastAPI Backend
→ SQLite Storage

---

## Database

Bookings are stored in SQLite.

Fields:

- customer_name
- vehicle_type
- preferred_date
- preferred_time
- contact_details
- booking_status

---

## Running the Project

Install dependencies:

pip install -r requirements.txt

Start server:

uvicorn backend.main:app --reload

Expose locally:

cloudflared tunnel --url http://localhost:8000

---

## Author

Sarim