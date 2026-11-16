import sys, os, traceback
sys.path.insert(0, '.')

# 1. Query users from security DB
from conexion.conexionBD import connectionBD_seguridad
try:
    conn = connectionBD_seguridad()
    cur = conn.cursor()
    cur.execute('SELECT id_usuarios, nombre, rol, estado FROM usuarios LIMIT 10')
    print('=== USERS ===')
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()
except Exception as e:
    print('DB ERROR:', str(e))
    traceback.print_exc()

# 2. Get login traceback via Flask test client
import traceback as tb
os.environ['FLASK_DEBUG'] = 'true'
try:
    from app import app
    app.config['TESTING'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    with app.test_client() as c:
        try:
            r = c.post('/login', data={
                'nombre': 'test',
                'pass_user': 'test',
                'g-recaptcha-response': 'test'
            })
            print('\n=== LOGIN RESPONSE ===')
            print('STATUS:', r.status_code)
            print('BODY:', r.data[:3000].decode('utf-8', errors='replace'))
        except Exception as inner:
            print('\n=== LOGIN EXCEPTION ===')
            tb.print_exc()
except Exception as e:
    print('\n=== APP IMPORT ERROR ===')
    tb.print_exc()
