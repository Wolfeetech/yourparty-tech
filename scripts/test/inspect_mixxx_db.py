import sqlite3

conn = sqlite3.connect(r'C:\Users\StudioPC\AppData\Local\Mixxx\mixxxdb.sqlite')
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Get schema for library table
for table in tables:
    if 'library' in table.lower() or 'crate' in table.lower() or 'playlist' in table.lower():
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        print(f"\n{table}:")
        for col in cols:
            print(f"  {col[1]} ({col[2]})")

conn.close()
