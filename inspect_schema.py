import sqlite3

conn = sqlite3.connect(r"C:\AI\ORACLE-X\data\oracle_x.db")

for row in conn.execute("""
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'table'
      AND name IN ('simulation_events', 'current_simulated_state')
"""):
    print(row[0])
    print(row[1])
    print()

conn.close()
