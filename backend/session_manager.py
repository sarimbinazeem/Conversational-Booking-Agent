"""
session_manager.py

Manages separate conversation instances for different users.

Each user gets their own Conversation object so that booking
information does not leak between customers.
"""

from backend.conversation import Conversation


class SessionManager:

    def __init__(self):
        # Dictionary:
        #
        # session_id → Conversation
        #
        self.sessions = {}

    def get_conversation(self, session_id):

        # If the user doesn't have a conversation yet,
        # create one.
        if session_id not in self.sessions:

            self.sessions[session_id] = Conversation(session_id)

        return self.sessions[session_id]

    def delete_conversation(self, session_id):

        if session_id in self.sessions:

            del self.sessions[session_id]

    def has_conversation(self, session_id):

        return session_id in self.sessions