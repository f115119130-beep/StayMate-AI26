-- Reference schema. services.booking_service.initialize() applies this automatically.
CREATE TABLE IF NOT EXISTS customers (
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, salt TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS bookings (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 customer_id INTEGER NOT NULL REFERENCES customers(id),
 room_name TEXT NOT NULL, room_label TEXT NOT NULL,
 check_in TEXT NOT NULL, check_out TEXT NOT NULL, guests INTEGER NOT NULL,
 nightly_price INTEGER NOT NULL, total_price INTEGER NOT NULL,
 status TEXT NOT NULL DEFAULT 'confirmed',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
