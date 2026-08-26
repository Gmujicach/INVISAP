from flask import Blueprint, session, request, flash, redirect, url_for
from models.model_empresas import EmpresaModel
from services.bitacora_service import BitacoraService
from conexion.conexionBD import connectionBD_invilara
from flask import Blueprint, session, request, flash, redirect, url_for
from flask import request, flash, redirect, url_for, session
import re

# Definir blueprint
empresa_bp = Blueprint('empresa_bp', __name__)

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
    rif = formulario.get('rif')
    nombre_empresa = formulario.get('nombre_empresa')
    telefono = formulario.get('telefono')
    domicilio_fiscal = formulario.get('domicilio_fiscal')

    # VALIDACIONES DE BACKEND
    if not all([rif, nombre_empresa, telefono, domicilio_fiscal]):
        return False, 'Error: Todos los campos son obligatorios.', 'error'

    # Nombre (Mínimo 3 caracteres)
    if len(nombre_empresa.strip()) < 3:
        return False, 'Error: El nombre de la empresa debe tener al menos 3 caracteres.', 'error'

    # Validar RIF
    if not re.match(r'^[JVGE]-\d{1,9}$', rif):
        return False, 'Error: El formato del RIF es inválido o fue alterado.', 'error'

    # Teléfono
    if not re.match(r'^(0414|0424|0412|0416|0426|0422)-\d{7}$', telefono):
        return False, 'Error: El prefijo o formato del teléfono es inválido.', 'error'

    # Domicilio Fiscal
    if not re.match(r'^[a-zA-Z0-9\s#\-\.,ñÑáéíóúÁÉÍÓÚ/()]{3,78}$', domicilio_fiscal):
        return False, 'Error: El domicilio fiscal contiene caracteres no permitidos o longitud incorrecta.', 'error'

    datos_limpios = {
        'rif': rif,
        'nombre_empresa': nombre_empresa.strip(),
        'telefono': telefono,
        'domicilio_fiscal': domicilio_fiscal.strip()
    }

    resultado_db = EmpresaModel().registrar_Empresas(datos_limpios)

    if resultado_db == True:
        BitacoraService.registrar_accion(
            session, 'Empresas', 'CREAR',
            f'Registró la empresa con RIF: {rif}'
        )
        return True, '¡La empresa ha sido registrada con éxito!', 'success'
    elif resultado_db == "DUPLICADO":
        return False, f'Error: El RIF {rif} ya se encuentra registrado en el sistema.', 'error'
    else:
        return False, 'Error interno del servidor al intentar guardar la empresa.', 'error'

def update_empresa(datos):
    resultado = EmpresaModel().update_empresa(datos)
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Empresas', 'EDITAR',
            f'Actualizó la empresa con RIF: {datos.get("rif")}'
        )
    return resultado

def eliminar_empresa_por_rif(rif):
    try:
        resultado = EmpresaModel().eliminar_empresa(rif)
        if resultado:
            BitacoraService.registrar_accion(
                session, 'Empresas', 'ELIMINAR',
                f'Eliminó la empresa con RIF: {rif}'
            )
        if not resultado:
            print(f"DEBUG: El modelo devolvió False para el RIF: {rif}")
        return resultado
    except Exception as e:
        print(f"DEBUG: ERROR CRÍTICO AL ELIMINAR -> {str(e)}")
        return False

def marcar_cumple_requisitos(rif, valor):
    try:
        resultado = EmpresaModel().actualizar_cumple_requisitos(rif, valor)
        if resultado:
            BitacoraService.registrar_accion(
                session, 'Empresas', 'EDITAR',
                f'{"Marcó" if valor else "Desmarcó"} cumplimiento de requisitos legales para el RIF: {rif}'
            )
        return resultado
    except Exception as e:
        print(f"DEBUG: ERROR AL MARCAR CUMPLE REQUISITOS -> {str(e)}")
        return False