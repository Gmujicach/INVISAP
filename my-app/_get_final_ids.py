import sys, os
sys.path.insert(0, '.')
from conexion.conexionBD import connectionBD_invilara, connectionBD_seguridad

conn = connectionBD_invilara()
cur = conn.cursor()

cur.execute('SELECT rif, nombre_empresa FROM empresa LIMIT 3')
print('EMPRESA (rif):', cur.fetchall())

cur2 = conn.cursor()
cur2.execute('SELECT * FROM informe_avance_obra LIMIT 1')
cols = [d[0] for d in cur2.description]
print('INFORME cols:', cols)
cur2.execute('SELECT * FROM informe_avance_obra LIMIT 3')
print('INFORME rows:', cur2.fetchall())
cur2.close()
cur.close()
conn.close()

conn2 = connectionBD_seguridad()
cur3 = conn2.cursor()
cur3.execute('SELECT * FROM roles LIMIT 1')
cols3 = [d[0] for d in cur3.description]
print('ROLES cols:', cols3)
cur3.execute('SELECT * FROM roles LIMIT 5')
print('ROLES rows:', cur3.fetchall())

cur4 = conn2.cursor()
cur4.execute('SELECT id_usuarios, nombre, contrasena FROM usuarios WHERE nombre="admin" LIMIT 1')
print('ADMIN hash:', cur4.fetchall())
cur4.close()
cur3.close()
conn2.close()
