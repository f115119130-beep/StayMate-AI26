"""Hotel tool contracts: runtime functions are registered in app.py.

These names are documented here for independent module development; the original
app.py remains the source of truth for tool registration during migration.
"""
HOTEL_TOOLS = (
    "get_hotel_info", "get_room_info", "list_rooms", "compare_rooms",
    "calculate_stay_total", "transfer_to_human", "search_hotel_rules",
)
