<<<<<<< HEAD
# my-app/controllers/funciones_solicitud.py
=======
from flask import Blueprint, request, redirect, url_for, flash
>>>>>>> b891557d060839a299cc4c198bb7e81b5bf459b0
from models.model_gerencias import GerenciaModel
from conexion.conexionBD import connectionBD_invilara

<<<<<<< HEAD

def obtener_gerencias():
    """
    Devuelve todas las solicitudes registradas en la base de datos invilara.
    """
    modelo = GerenciaModel()
    return modelo.obtener_todas_las_Gerencias()


def crear_gerencia(datos_formulario):
    """
    Crea el solicitante o lo recupera y registra la solicitud en invilara.
    """
    if not datos_formulario.get('tipo_gerencia') or not datos_formulario.get('problematica'):
        return False

    modelo = GerenciaModel()
    return modelo.crear_nueva_gerencia(datos_formulario)


def obtener_gerencia_por_id(id_gerencia):
    """
    Recupera los datos de una solicitud por su identificador.
    """
    modelo = GerenciaModel()
    return modelo.obtener_gerencia_por_id(id_gerencia)
=======
# Definimos el blueprint solo para organizarnos, pero no le pegamos rutas aquí
gerencia_bp = Blueprint('gerencia_bp', __name__)

# --- FUNCIONES DE LÓGICA (No rutas) ---

def obtener_todas_las_gerencias():
    return GerenciaModel().obtener_todas_las_gerencias()

def obtener_gerencia_por_id(id_gerencia):
    modelo = GerenciaModel()
    conexion = None
    try:
        conexion = connectionBD_invilara()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gerencias WHERE id_gerencias = %s", (id_gerencia,))
        return cursor.fetchone()
    except Exception as e:
        print(f"--- [ERROR] {e} ---")
        return None
    finally:
        if conexion: conexion.close()

def update_gerencia(datos):
    return GerenciaModel().update_gerencia(datos)

def procesar_registro_gerencia(datos):
    return GerenciaModel().registrar_gerencias(datos)

def eliminar_gerencia_por_id(id_gerencia):
    modelo = GerenciaModel()
    return modelo.eliminar_gerencia(id_gerencia)
>>>>>>> b891557d060839a299cc4c198bb7e81b5bf459b0
