import sys, os, traceback
sys.path.insert(0, '.')
from conexion.conexionBD import connectionBD_invilara, connectionBD_seguridad

def q(conn, sql, label):
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        print(f'=== {label} ===')
        for r in rows:
            print(r)
        cur.close()
        return rows
    except Exception as e:
        print(f'ERROR {label}: {e}')
        return []

try:
    conn = connectionBD_invilara()
    q(conn, 'SELECT codigo_proyecto, nombre_proyecto FROM proyecto LIMIT 5', 'PROYECTOS')
    q(conn, 'SELECT rif_empresa, nombre_empresa FROM empresa LIMIT 5', 'EMPRESAS')
    q(conn, 'SELECT id_evidencia FROM evidencia LIMIT 5', 'EVIDENCIAS')
    q(conn, 'SELECT id_informe_avance_obra FROM informe_avance_obra LIMIT 5', 'INFORMES')
    conn.close()
except Exception as e:
    print('MAIN DB ERROR:', e)
    traceback.print_exc()

try:
    conn2 = connectionBD_seguridad()
    q(conn2, 'SELECT id_usuarios, nombre, rol FROM usuarios WHERE estado=1 LIMIT 10', 'USUARIOS')
    q(conn2, 'SELECT id_rol, nombre_rol FROM roles LIMIT 10', 'ROLES')
    conn2.close()
except Exception as e:
    print('SEC DB ERROR:', e)
    traceback.print_exc()
