import sys, os
sys.path.insert(0, '.')
from conexion.conexionBD import connectionBD_invilara, connectionBD_seguridad

conn = connectionBD_invilara()
cur = conn.cursor()

cur.execute('SELECT codigo_proyecto FROM proyecto LIMIT 3')
print('PROYECTOS:', cur.fetchall())

cur.execute('SELECT * FROM empresa LIMIT 1')
cols = [d[0] for d in cur.description]
print('EMPRESA cols:', cols)
cur.execute('SELECT * FROM empresa LIMIT 3')
print('EMPRESA rows:', cur.fetchall())

cur.execute('SELECT * FROM informe_avance_obra LIMIT 1')
cols2 = [d[0] for d in cur.description]
print('INFORME cols:', cols2)
cur.execute('SELECT * FROM informe_avance_obra LIMIT 3')
print('INFORME rows:', cur.fetchall())

cur.close(); conn.close()

conn2 = connectionBD_seguridad()
cur2 = conn2.cursor()
cur2.execute('SELECT * FROM roles LIMIT 1')
cols3 = [d[0] for d in cur2.description]
print('ROLES cols:', cols3)
cur2.execute('SELECT * FROM roles LIMIT 5')
print('ROLES rows:', cur2.fetchall())
cur2.close(); conn2.close()
