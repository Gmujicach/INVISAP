"""
Controller de Evidencias - Implementa comunicación asíncrona con Fetch/Ajax.
Rutas de vistas y API.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models.model_evidencia import EvidenciaModel
from services.bitacora_service import BitacoraService

evidencia_bp = Blueprint('evidencia_bp', __name__, template_folder='../vista')

@evidencia_bp.route('/evidencias/registrar', methods=['GET'])
def show_registrar_evidencia():
    """Muestra el formulario de registro de evidencias."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('evidencia/evidencia.html')

@evidencia_bp.route('/evidencias/listar', methods=['GET'])
def show_listar_evidencias():
    """Muestra el listado de evidencias activas paginadas."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    modelo = EvidenciaModel()
    evidencias = modelo.obtener_todas_evidencias(page=page, per_page=per_page)
    total_evidencias = modelo.contar_evidencias()
    total_pages = (total_evidencias + per_page - 1) // per_page
    
    return render_template('evidencia/lista_evidencias.html', 
                           evidencias=evidencias,
                           page=page,
                           per_page=per_page,
                           total_evidencias=total_evidencias,
                           total_pages=total_pages)

@evidencia_bp.route('/evidencias/modificar/<int:id_evidencia>', methods=['GET'])
def show_modificar_evidencia(id_evidencia):
    """Muestra el formulario de modificación de evidencia."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    modelo = EvidenciaModel()
    evidencia = modelo.obtener_evidencia_por_id(id_evidencia)
    if not evidencia:
        flash('La evidencia no existe', 'error')
        return redirect(url_for('evidencia_bp.show_listar_evidencias'))
    return render_template('evidencia/evidencia_modificar.html', evidencia=evidencia)

@evidencia_bp.route('/evidencias/detalle/<int:id_evidencia>', methods=['GET'])
def show_detalle_evidencia(id_evidencia):
    """Muestra el detalle de una evidencia."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    modelo = EvidenciaModel()
    evidencia = modelo.obtener_evidencia_por_id(id_evidencia)
    if not evidencia:
        flash('La evidencia no existe', 'error')
        return redirect(url_for('evidencia_bp.show_listar_evidencias'))
    return render_template('evidencia/detalle_evidencia.html', evidencia=evidencia)

@evidencia_bp.route('/api/evidencias/subir', methods=['POST'])
def api_subir_evidencias():
    """
    API para subir evidencias mediante Fetch/Ajax.
    Evita recargas de página según instrucciones del profesor.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401
    try:
        files = request.files.getlist('fotos')
        etapas = request.form.getlist('etapas[]')
        
        modelo = EvidenciaModel()
        ids_insertados = modelo.registrar_evidencias(files, etapas)
        
        if ids_insertados and len(ids_insertados) > 0:
            BitacoraService.registrar_accion(
                session, 'Evidencias', 'CREAR',
                f'Subió {len(ids_insertados)} evidencia(s)'
            )
            return jsonify({'status': 'success', 'message': f'{len(ids_insertados)} evidencias registradas correctamente'})
        else:
            return jsonify({'status': 'error', 'message': 'Fallo en base de datos'}), 500
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}'}), 500

@evidencia_bp.route('/api/evidencias/actualizar/<int:id_evidencia>', methods=['POST'])
def api_actualizar_evidencia(id_evidencia):
    """
    API para actualizar evidencias mediante Fetch/Ajax.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401
    try:
        files = request.files.getlist('fotos')
        etapas = request.form.getlist('etapas[]')
        
        modelo = EvidenciaModel()
        exito = modelo.actualizar_evidencia(id_evidencia, files, etapas)
        
        if exito:
            BitacoraService.registrar_accion(
                session, 'Evidencias', 'EDITAR',
                f'Actualizó la evidencia ID: {id_evidencia}'
            )
            return jsonify({'status': 'success', 'message': 'Evidencia actualizada correctamente'})
        else:
            return jsonify({'status': 'error', 'message': 'Fallo al actualizar'}), 500
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}'}), 500

@evidencia_bp.route('/api/evidencias/validar/<int:id_evidencia>', methods=['GET'])
def api_validar_evidencia(id_evidencia):
    """
    API para validar existencia de evidencia en tiempo real.
    Usado por eventos 'change' en selectores (Ajax).
    """
    modelo = EvidenciaModel()
    existe = modelo.validar_evidencia_activa(id_evidencia)
    return jsonify({'existe': existe, 'id': id_evidencia})

@evidencia_bp.route('/evidencias/eliminar/<int:id_evidencia>', methods=['GET'])
def eliminar_evidencia(id_evidencia):
    """
    Ruta para borrado lógico de evidencias.
    Cambia el estado a 0 sin eliminar físicamente.
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    try:
        modelo = EvidenciaModel()
        if modelo.eliminar_evidencia(id_evidencia):
            BitacoraService.registrar_accion(
                session, 'Evidencias', 'ELIMINAR',
                f'Desactivó la evidencia ID: {id_evidencia}'
            )
            flash('Evidencia desactivada correctamente', 'success')
        else:
            flash('No se pudo desactivar', 'error')
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception:
        flash('Error interno', 'error')
    return redirect(url_for('evidencia_bp.show_listar_evidencias'))
