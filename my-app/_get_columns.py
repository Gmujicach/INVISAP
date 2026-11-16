import sys, os, traceback
sys.path.insert(0, '.')
from conexion.conexionBD import connectionBD_invilara, connectionBD_seguridad

def cols(conn, table):
    try:
        cur = conn.cursor()
        cur.execute(f'DESCRIBE {table}')
        rows = cur.fetchall()
        print(f'=== {table} columns ===')
        for r in rows:
            print(f'  {r[0]} ({r[1]})')
        # Also get first 3 rows
        cur.execute(f'SELECT * FROM {table} LIMIT 3')
        print(f'  -- sample rows --')
        for r in cur.fetchall():
            print(f'  {r}')
        cur.close()
    except Exception as e:
        print(f'ERROR {table}: {e}')

try:
    conn = connectionBD_invilara()
    cols(conn, 'proyecto')
    cols(conn, 'empresa')
    cols(conn, 'informe_avance_obra')
    conn.close()
except Exception as e:
    print('MAIN DB ERROR:', e)
    traceback.print_exc()

try:
    conn2 = connectionBD_seguridad()
    cols(conn2, 'roles')
    conn2.close()
except Exception as e:
    print('SEC DB ERROR:', e)
    traceback.print_exc()
