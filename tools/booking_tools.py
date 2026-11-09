"""Public availability and authenticated personal booking tools."""
from services.booking_service import search, booking_details

def check_room_availability(check_in, check_out, guests):
    rows, message = search(check_in, check_out, guests)
    return {"message": message, "rooms": [
        {"room_name": r[0], "room_zh": r[1], "nightly_price_ntd": r[2],
         "remaining_rooms": r[3], "total_price_ntd": r[4]} for r in rows]}

def get_my_bookings(session_token):
    return booking_details(session_token)
