"""
Script de corrección de BD para INVISAP.
- Amplía la columna `contraseña` de VARCHAR(8) a VARCHAR(255)
- Elimina el UNIQUE incorrecto sobre contraseña
- Inserta el usuario de prueba admin/admin123
"""
import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host='db',
    user='root',
    password='root_password',
    database='invilara',
    charset='utf8mb4',
    use_unicode=True,
)
cur = conn.cursor()

# Nombre real de la columna con ñ
col = 'contraseña'

# 1. Ampliar columna a VARCHAR(255)
alter_sql = f'ALTER TABLE usuarios MODIFY COLUMN `{col}` VARCHAR(255) NOT NULL'
print(f"Ejecutando: {alter_sql}")
cur.execute(alter_sql)
conn.commit()
print("✅ Columna ampliada a VARCHAR(255)")

# 2. Eliminar UNIQUE sobre contraseña (sin sentido en hashes)
try:
    cur.execute(f'ALTER TABLE usuarios DROP INDEX `{col}_UNIQUE`')
    conn.commit()
    print("✅ UNIQUE eliminado")
except Exception as e:
    print(f"  (Sin UNIQUE que eliminar: {e})")

# 3. Insertar usuario de prueba
h = generate_password_hash('admin123')
insert_sql = f'INSERT INTO usuarios (cedula_usuario, nombre, `{col}`, correo, rol) VALUES (%s,%s,%s,%s,%s)'
cur.execute(insert_sql, ('12345678', 'admin', h, 'admin@invisap.com', 'Administrador'))
conn.commit()
print(f"✅ Usuario admin creado (hash: {h[:40]}...)")

# 4. Verificar resultado
cur.execute('SELECT id_usuarios, nombre, correo, rol FROM usuarios')
print("\n📋 Usuarios en BD:")
for row in cur.fetchall():
    print(f"   {row}")

cur.close()
conn.close()
print("\n✅ Corrección completada")
