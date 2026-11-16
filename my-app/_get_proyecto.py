import sys, os, traceback
sys.path.insert(0, '.')
from conexion.conexionBD import connectionBD_invilara

try:
    conn = connectionBD_invilara()
    cur = conn.cursor()
    cur.execute('SELECT codigo_proyecto, nombre_proyecto FROM proyectos LIMIT 5')
    print('=== PROYECTOS ===')
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()
except Exception as e:
    print('DB ERROR:', str(e))
    traceback.print_exc()
