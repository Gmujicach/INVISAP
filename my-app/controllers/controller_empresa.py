from flask import Blueprint, session
from models.model_empresas import EmpresaModel
from conexion.conexionBD import connectionBD_invilara

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

def procesar_registro_empresa(datos):
    return EmpresaModel().registrar_Empresas(datos)

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