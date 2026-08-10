"""
database.py

SQLite database layer for the car wash booking system so that the bookings are remembered
"""

import sqlite3
from pathlib import Path


# Database will be created inside the backend folder.
DATABASE_PATH = Path(__file__).parent / "bookings.db"


def get_connection():
    """
    Create a connection to the SQLite database.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    # Allows us to access columns by name. (bookings["customer_name"] instead of booking[1])
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the bookings table if it does not already exist.
    """

    #connection between python and datbase
    connection = get_connection()

    #cursor sends command through conenction to SQLite
    cursor = connection.cursor()

    #SQL commands
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT NOT NULL,

            customer_name TEXT NOT NULL,

            vehicle_type TEXT NOT NULL,

            preferred_date TEXT NOT NULL,

            preferred_time TEXT NOT NULL,

            contact_details TEXT NOT NULL,

            booking_status TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    connection.commit()

    connection.close()

#save a confimed booking
def create_booking(
    session_id,
    customer_name,
    vehicle_type,
    preferred_date,
    preferred_time,
    contact_details
):
    """
    Create a new confirmed booking.
    """

    connection = get_connection()

    cursor = connection.cursor()

    #(?,?) are the placeholders for the below valuyes
    cursor.execute(
        """
        INSERT INTO bookings (
            session_id,
            customer_name,
            vehicle_type,
            preferred_date,
            preferred_time,
            contact_details,
            booking_status
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            customer_name,
            vehicle_type,
            preferred_date,
            preferred_time,
            contact_details,
            "confirmed"
        )
    )

    #the id of current booking
    booking_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return booking_id


def get_booking(booking_id):
    """
    Get one booking by its ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE id = ?
        """,
        (booking_id,)
    )

    #GIVE ME FIRST MATCHING ROW
    booking = cursor.fetchone()

    connection.close()

    if booking is None:
        return None

    #turn tuple into a dictionary
    return dict(booking)


def get_all_bookings():
    """
    Return all bookings.
    """

    connection = get_connection()

    cursor = connection.cursor()

    #ORDER BY -> sorts it in creaiton time order
    cursor.execute(
        """
        SELECT *
        FROM bookings
        ORDER BY created_at DESC
        """
    )

    bookings = cursor.fetchall()

    connection.close()

    return [dict(booking) for booking in bookings]


def update_booking_status(
    booking_id,
    status
):
    """
    Update the status of a booking.
    """

    connection = get_connection()

    cursor = connection.cursor()

    #update the timestamp status through booking id
    cursor.execute(
        """
        UPDATE bookings

        SET
            booking_status = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE id = ?
        """,
        (
            status,
            booking_id
        )
    )

    connection.commit()

    connection.close()