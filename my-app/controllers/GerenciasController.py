from flask import Blueprint, request, redirect, url_for, flash
from models.model_gerencias import GerenciaModel
from conexion.conexionBD import connectionBD_invilara

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