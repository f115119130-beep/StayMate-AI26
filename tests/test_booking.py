"""Offline demo tests. Uses a temporary SQLite DB; never touches personal bookings."""
import tempfile
import unittest
from pathlib import Path
from datetime import date, timedelta

from services import booking_service as booking

class BookingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        booking.DB = Path(self.tmp.name) / 'test.db'
        booking.SESSIONS.clear()
        booking.initialize()
        self.start = (date.today() + timedelta(days=7)).isoformat()
        self.mid = (date.today() + timedelta(days=8)).isoformat()
        self.end = (date.today() + timedelta(days=10)).isoformat()
        self.assertIn('註冊成功', booking.register('alice', 'passphrase123', 'passphrase123'))
        self.assertIn('註冊成功', booking.register('bob', 'passphrase456', 'passphrase456'))
        self.alice, _ = booking.login('alice', 'passphrase123')
        self.bob, _ = booking.login('bob', 'passphrase456')

    def tearDown(self):
        booking.SESSIONS.clear()
        self.tmp.cleanup()

    def test_login_required_and_private_orders(self):
        self.assertIn('請先登入', booking.book(None, 'Standard Double', self.start, self.end, 2))
        self.assertIn('訂房成功', booking.book(self.alice, 'Standard Double', self.start, self.end, 2))
        self.assertEqual(len(booking.my_bookings(self.alice)[0]), 1)
        self.assertEqual(len(booking.my_bookings(self.bob)[0]), 0)
        self.assertFalse(booking.booking_details(None)['authenticated'])
        self.assertEqual(len(booking.booking_details(self.alice)['bookings']), 1)

    def test_nightly_inventory_and_cancellation(self):
        for i in range(3):
            self.assertIn('訂房成功', booking.book(self.alice, 'Standard Double', self.start, self.mid, 2))
        # Overlapping on only one night must still be rejected.
        self.assertIn('額滿', booking.book(self.bob, 'Standard Double', self.start, self.end, 2))
        self.assertEqual(booking.search(self.start, self.end, 2)[0][0][0] != 'Standard Double', True)
        booking_id = booking.my_bookings(self.alice)[0][0][0]
        self.assertIn('找不到可取消', booking.cancel(self.bob, booking_id))
        self.assertIn('已取消', booking.cancel(self.alice, booking_id))
        self.assertIn('訂房成功', booking.book(self.bob, 'Standard Double', self.start, self.end, 2))

    def test_password_hash(self):
        with booking.connect() as db:
            row = db.execute("SELECT password_hash FROM customers WHERE username='alice'").fetchone()
        self.assertNotEqual(row[0], 'passphrase123')

if __name__ == '__main__':
    unittest.main()
