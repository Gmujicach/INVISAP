from conexion.conexionBD import connectionBD_invilara
from controllers.funciones_solicitud import crear_solicitud

print('Conectando...')
conn = connectionBD_invilara()
print('conn:', conn)
if conn is not None:
    print('is_connected:', conn.is_connected())
    conn.close()

form = {
    'tipo_solicitud': 'Particular',
    'estatus': 'Pendiente',
    'problematica': 'Necesito ayuda con un problema de infraestructura en la zona.',
    'tipo_problematica': 'Infraestructura y Vialidad',
    'part_nombre': 'Ana',
    'part_apellido': 'Perez',
    'part_cedula': '12345678',
    'part_correo': 'ana@test.com',
    'part_telefono': '04121234567',
    'part_municipio': 'Iribarren',
    'part_parroquia': 'Catedral',
    'part_direccion': 'Calle principal 123'
}

print(crear_solicitud(form, {'conectado': True, 'name_surname': 'Test'}))
