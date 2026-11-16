import sys, os, traceback
sys.path.insert(0, '.')
from conexion.conexionBD import connectionBD_invilara

try:
    conn = connectionBD_invilara()
    cur = conn.cursor()
    # List all tables in main DB
    cur.execute('SHOW TABLES')
    print('=== TABLES in invilara ===')
    for row in cur.fetchall():
        print(row[0])
    cur.close()
    conn.close()
except Exception as e:
    print('DB ERROR:', str(e))
    traceback.print_exc()
