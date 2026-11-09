"""Sunny Stay demo booking service. Persistent SQLite, hashed passwords, server-side sessions."""
import hashlib
import hmac
import secrets
import sqlite3
import threading
from datetime import date
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / 'bookings.db'
LOCK = threading.RLock()
SESSIONS = {}
INVENTORY = 3  # fictional rooms per type; change to match a real inventory source
CAPACITY = {'Single Room': 1, 'Standard Double': 2, 'Twin Room': 2,
            'Deluxe Double': 2, 'Family Room': 4, 'Suite': 2}


def connect():
    conn = sqlite3.connect(DB, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def initialize():
    with LOCK, connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            room_name TEXT NOT NULL, room_label TEXT NOT NULL,
            check_in TEXT NOT NULL, check_out TEXT NOT NULL,
            guests INTEGER NOT NULL, nightly_price INTEGER NOT NULL,
            total_price INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'confirmed',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')


def _hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 260000).hex()


def register(username, password, confirm):
    username = (username or '').strip()
    if not 3 <= len(username) <= 40 or not all(c.isalnum() or c in '_-' for c in username):
        return '帳號需為 3–40 個英數字、底線或連字號。'
    if len(password or '') < 8:
        return '密碼至少需要 8 個字元。'
    if password != confirm:
        return '兩次輸入的密碼不一致。'
    salt = secrets.token_hex(16)
    try:
        with LOCK, connect() as db:
            db.execute('INSERT INTO customers(username,password_hash,salt) VALUES(?,?,?)',
                       (username, _hash(password, salt), salt))
    except sqlite3.IntegrityError:
        return '此帳號已存在，請改用其他帳號。'
    return '註冊成功，請前往登入。'


def login(username, password):
    with LOCK, connect() as db:
        row = db.execute('SELECT * FROM customers WHERE username=?', ((username or '').strip(),)).fetchone()
    if not row or not hmac.compare_digest(_hash(password or '', row['salt']), row['password_hash']):
        return None, '帳號或密碼錯誤。'
    token = secrets.token_urlsafe(32)
    with LOCK:
        SESSIONS[token] = row['id']
    return token, f'登入成功，歡迎 {row["username"]}！'


def logout(token):
    with LOCK:
        SESSIONS.pop(token, None)
    return None, '已安全登出。'


def user_id(token):
    with LOCK:
        return SESSIONS.get(token)


def _dates(check_in, check_out):
    start = date.fromisoformat((check_in or '').strip())
    end = date.fromisoformat((check_out or '').strip())
    if start < date.today() or end <= start:
        raise ValueError('入住日期不可早於今天，退房日期必須晚於入住日期。')
    if (end - start).days > 30:
        raise ValueError('一次最多預訂 30 晚。')
    return start, end


def _rooms():
    # Read authoritative room definitions from the existing CSV, not user input.
    import csv
    with open(Path(__file__).resolve().parent.parent / 'hotel_items.csv', encoding='utf-8-sig', newline='') as f:
        return {r['name']: r for r in csv.DictReader(f) if r['category'] == 'room' and r['available'] == '1'}


def _remaining(db, name, check_in, check_out):
    """The minimum nightly availability over the entire requested stay."""
    start, end = date.fromisoformat(check_in), date.fromisoformat(check_out)
    rows = db.execute("""SELECT check_in,check_out FROM bookings
        WHERE room_name=? AND status='confirmed' AND check_in < ? AND check_out > ?""",
        (name, check_out, check_in)).fetchall()
    from datetime import timedelta
    remaining = INVENTORY
    day = start
    while day < end:
        used = sum(date.fromisoformat(r['check_in']) <= day < date.fromisoformat(r['check_out']) for r in rows)
        remaining = min(remaining, INVENTORY - used)
        day += timedelta(days=1)
    return max(0, remaining)


def booking_details(token):
    rows, message = my_bookings(token)
    if user_id(token) is None:
        return {'authenticated': False, 'message': message, 'bookings': []}
    return {'authenticated': True, 'message': message, 'bookings': [
        {'booking_id': r[0], 'room': r[1], 'check_in': r[2], 'check_out': r[3],
         'guests': r[4], 'total_price_ntd': r[5], 'status': r[6]} for r in rows]}


def search(check_in, check_out, guests):
    try:
        start, end = _dates(check_in, check_out)
        guests = int(guests)
        if not 1 <= guests <= 4:
            return [], '入住人數請填 1～4 人。'
    except (ValueError, TypeError) as e:
        return [], f'日期或人數錯誤：{e}'
    results = []
    with LOCK, connect() as db:
        for name, r in _rooms().items():
            if CAPACITY.get(name, 0) < guests:
                continue
            left = _remaining(db, name, start.isoformat(), end.isoformat())
            if left:
                results.append([name, r['name_zh'], int(r['price']), left,
                                int(r['price']) * (end-start).days])
    return results, f'找到 {len(results)} 種可訂房型（{(end-start).days} 晚，模擬庫存每房型 {INVENTORY} 間）。'


def book(token, room_name, check_in, check_out, guests):
    uid = user_id(token)
    if uid is None:
        return '請先登入會員，才能建立訂單。'
    try:
        start, end = _dates(check_in, check_out)
        guests = int(guests)
        rooms = _rooms()
        if room_name not in rooms:
            return '找不到這個可訂房型，請重新查詢。'
        if not 1 <= guests <= CAPACITY[room_name]:
            return '入住人數超過此房型容量，請重新選擇。'
        with LOCK, connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if _remaining(db, room_name, start.isoformat(), end.isoformat()) <= 0:
                return '此日期的房間已額滿，請更換日期或房型。'
            r = rooms[room_name]
            nightly = int(r['price'])
            total = nightly * (end-start).days
            cursor = db.execute('''INSERT INTO bookings
                (customer_id,room_name,room_label,check_in,check_out,guests,nightly_price,total_price)
                VALUES (?,?,?,?,?,?,?,?)''',
                (uid,room_name,r['name_zh'],start.isoformat(),end.isoformat(),guests,nightly,total))
            booking_id = cursor.lastrowid
        return f'訂房成功！訂單編號 #{booking_id}｜{r["name_zh"]}｜{start} 至 {end}｜{guests} 人｜總計 NT${total:,}。這是課程模擬訂單，沒有實際付款。'
    except (ValueError, TypeError) as e:
        return f'訂房失敗：{e}'


def my_bookings(token):
    uid = user_id(token)
    if uid is None:
        return [], '請先登入查看自己的訂單。'
    with LOCK, connect() as db:
        rows = db.execute('''SELECT id,room_label,check_in,check_out,guests,total_price,status
            FROM bookings WHERE customer_id=? ORDER BY id DESC''', (uid,)).fetchall()
    return [[r['id'],r['room_label'],r['check_in'],r['check_out'],r['guests'],r['total_price'],r['status']] for r in rows], f'共有 {len(rows)} 筆訂單。'


def cancel(token, booking_id):
    uid = user_id(token)
    if uid is None:
        return '請先登入。'
    try:
        bid = int(booking_id)
    except (ValueError, TypeError):
        return '請輸入有效的訂單編號。'
    with LOCK, connect() as db:
        cursor = db.execute('''UPDATE bookings SET status='cancelled'
            WHERE id=? AND customer_id=? AND status='confirmed' AND check_in > ?''',
            (bid, uid, date.today().isoformat()))
    if cursor.rowcount:
        return f'訂單 #{bid} 已取消，房間庫存已釋出。這是課程模擬訂單，不涉及退款。'
    return '找不到可取消的訂單，或訂單已取消／已開始入住。'

initialize()
