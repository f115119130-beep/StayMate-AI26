"""Create local booking tables. Room information is loaded by app.py from CSV."""
from services.booking_service import initialize

if __name__ == "__main__":
    initialize()
    print("Booking tables initialized")
