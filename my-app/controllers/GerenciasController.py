# my-app/controllers/funciones_solicitud.py

from flask import Blueprint, request, redirect, url_for, flash

from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from models.model_gerencias import GerenciaModel
from conexion.conexionBD import connectionBD_invilara

gerencia_bp = Blueprint('gerencia_bp', __name__)


@gerencia_bp.route('/registrar-gerencias', methods=['GET'])
def gestionar_gerencias():
    if 'conectado' in session:
        modelo = GerenciaModel()
        lista = modelo.obtener_todas_las_gerencias()
        return render_template('gerencias/lista_gerencias.html', gerencias=lista)
    return redirect(url_for('login_bp.inicio'))



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

@gerencia_bp.route('/form-registrar-gerencias', methods=['POST'])
def procesar_registro():
    print("ESTADO DE LA SESIÓN:", session) # Esto es vital
    
    if 'conectado' in session:
        print("¡USUARIO LOGUEADO! Intentando guardar...")
        datos = request.form
        modelo = GerenciaModel()
        if modelo.registrar_gerencias(datos):
            return "GUARDADO CON ÉXITO"
        else:
            return "ERROR EN EL MODELO"
    else:
        return "ERROR: ¡LA SESIÓN NO ESTÁ ACTIVA! No puedes registrar."

