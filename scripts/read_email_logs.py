import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'
if not DB.exists():
    print('DB not found at', DB)
    raise SystemExit(1)

con = sqlite3.connect(str(DB))
cur = con.cursor()
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files_emaillog'")
    if not cur.fetchone():
        print('EmailLog table not found')
        raise SystemExit(1)
    cur.execute('SELECT id, subject, recipients, sent, error, created_at FROM files_emaillog ORDER BY created_at DESC LIMIT 20')
    rows = cur.fetchall()
    if not rows:
        print('No EmailLog entries')
    else:
        for r in rows:
            print(r)
finally:
    con.close()
