import sys, os, traceback
sys.path.insert(0, '.')

OUT = open('_debug_output.txt', 'w', encoding='utf-8')

def p(msg):
    print(msg)
    OUT.write(msg + '\n')
    OUT.flush()

# 1. Query users
from conexion.conexionBD import connectionBD_seguridad
try:
    conn = connectionBD_seguridad()
    cur = conn.cursor()
    cur.execute('SELECT id_usuarios, nombre, rol, estado FROM usuarios LIMIT 10')
    p("=== USERS ===")
    for row in cur.fetchall():
        p(str(row))
    cur.close()
    conn.close()
except Exception as e:
    p('DB ERROR: ' + str(e))
    traceback.print_exc(file=OUT)

# 2. Flask test client to get real traceback
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
            p("\n=== LOGIN RESPONSE ===")
            p('STATUS: ' + str(r.status_code))
            p('DATA: ' + r.data[:3000].decode('utf-8', errors='replace'))
        except Exception as inner:
            p("\n=== LOGIN EXCEPTION ===")
            traceback.print_exc(file=OUT)
            traceback.print_exc()
except Exception as e:
    p("\n=== APP IMPORT ERROR ===")
    traceback.print_exc(file=OUT)
    traceback.print_exc()

OUT.close()
p("Done - see _debug_output.txt")
