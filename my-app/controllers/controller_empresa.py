from flask import Blueprint, session
from models.model_empresas import EmpresaModel
from conexion.conexionBD import connectionBD_invilara
from flask import Blueprint, session, request, flash, redirect, url_for
from flask import request, flash, redirect, url_for, session
import re

# Definimos el blueprint
empresa_bp = Blueprint('empresa_bp', __name__)

# --- LÓGICA DE GERENCIAS ---
def obtener_todas_las_empresas():
    return EmpresaModel().obtener_todas_las_empresas()

def obtener_empresa_por_rif(rif):
    conexion = None
    try:
        conexion = connectionBD_invilara()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM empresa WHERE rif = %s", (rif,))
        return cursor.fetchone()
    except Exception as e:
        print(f"--- [ERROR] {e} ---")
        return None
    finally:
        if conexion: conexion.close()

def procesar_registro_empresa(formulario):
    """
    Recibe el formulario, lo valida y lo envía al modelo.
    Retorna una tupla: (Boolean_Exito, String_Mensaje, String_Categoria_Flash)
    """
    # 1. Extraer los datos del formulario recibido
    rif = formulario.get('rif')
    nombre_empresa = formulario.get('nombre_empresa')
    telefono = formulario.get('telefono')
    domicilio_fiscal = formulario.get('domicilio_fiscal')

    # 2. VALIDACIONES DE BACKEND (Forma y estructura)
    
    # A. Verificar que no haya campos nulos
    if not all([rif, nombre_empresa, telefono, domicilio_fiscal]):
        return False, 'Error: Todos los campos son obligatorios.', 'error'

    # B. Validar Nombre (Mínimo 3 caracteres)
    if len(nombre_empresa.strip()) < 3:
        return False, 'Error: El nombre de la empresa debe tener al menos 3 caracteres.', 'error'

    # C. Validar RIF (J,V,G,E + guion + números)
    if not re.match(r'^[JVGE]-\d{1,9}$', rif):
        return False, 'Error: El formato del RIF es inválido o fue alterado.', 'error'

    # D. Validar Teléfono (Prefijos válidos + 7 dígitos)
    if not re.match(r'^(0414|0424|0412|0416|0426|0422)-\d{7}$', telefono):
        return False, 'Error: El prefijo o formato del teléfono es inválido.', 'error'

    # E. Validar Domicilio Fiscal (Letras, números, espacios, guiones, #, . y comas)
    if not re.match(r'^[a-zA-Z0-9\s#\-\.,ñÑáéíóúÁÉÍÓÚ]{3,78}$', domicilio_fiscal):
        return False, 'Error: El domicilio fiscal contiene caracteres no permitidos o longitud incorrecta.', 'error'

    # 3. Si todas las validaciones pasan, empaquetamos los datos limpios
    datos_limpios = {
        'rif': rif,
        'nombre_empresa': nombre_empresa.strip(),
        'telefono': telefono,
        'domicilio_fiscal': domicilio_fiscal.strip()
    }

    # 4. Enviar al modelo para guardar en Base de Datos
    resultado_db = EmpresaModel().registrar_Empresas(datos_limpios)

    # 5. Evaluar la respuesta del modelo y retornar al router
    if resultado_db == True:
        return True, '¡La empresa ha sido registrada con éxito!', 'success'
    elif resultado_db == "DUPLICADO":
        return False, f'Error: El RIF {rif} ya se encuentra registrado en el sistema.', 'error'
    else:
        return False, 'Error interno del servidor al intentar guardar la empresa.', 'error'

def update_empresa(datos):
    return EmpresaModel().update_empresa(datos)

def eliminar_empresa_por_rif(rif):
    try:
        # Esto usará la lógica que ya tienes en el modelo
        resultado = EmpresaModel().eliminar_empresa(rif)
        if not resultado:
            print(f"DEBUG: El modelo devolvió False para el RIF: {rif}")
        return resultado
    except Exception as e:
        # Esto imprimirá el error real en tu consola (terminal de Flask)
        print(f"DEBUG: ERROR CRÍTICO AL ELIMINAR -> {str(e)}")
        return False