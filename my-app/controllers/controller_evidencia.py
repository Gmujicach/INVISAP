"""
Controller de Evidencias - Implementa comunicación asíncrona con Fetch/Ajax.
Rutas de vistas y API.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models.model_evidencia import EvidenciaModel

evidencia_bp = Blueprint('evidencia_bp', __name__, template_folder='../vista')


# ========== RUTAS DE VISTAS (GET) ==========
@evidencia_bp.route('/evidencias/registrar', methods=['GET'])
def show_registrar_evidencia():
    """Muestra el formulario de registro de evidencias."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesiÃ³n.', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('evidencia/evidencia.html')


@evidencia_bp.route('/evidencias/listar', methods=['GET'])
def show_listar_evidencias():
    """Muestra el listado de evidencias activas."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesiÃ³n.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    modelo = EvidenciaModel()
    evidencias = modelo.obtener_todas_evidencias()
    return render_template('evidencia/lista_evidencias.html', evidencias=evidencias)


@evidencia_bp.route('/evidencias/modificar/<int:id_evidencia>', methods=['GET'])
def show_modificar_evidencia(id_evidencia):
    """Muestra el formulario de modificaciÃ³n de evidencia."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesiÃ³n.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    modelo = EvidenciaModel()
    evidencia = modelo.obtener_evidencia_por_id(id_evidencia)
    
    if not evidencia:
        flash('La evidencia no existe o fue eliminada.', 'error')
        return redirect(url_for('evidencia_bp.show_listar_evidencias'))
    
    return render_template('evidencia/evidencia_modificar.html', evidencia=evidencia)


# ========== RUTAS API (POST/DELETE) - ComunicaciÃ³n AsÃncrona ==========
@evidencia_bp.route('/api/evidencias/subir', methods=['POST'])
def api_subir_evidencias():
    """
    API para subir evidencias mediante Fetch/Ajax.
    Evita recargas de pÃ¡gina segÃºn instrucciones del profesor.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        files = request.files.getlist('fotos')
        form_data = request.form

        if not files:
            return jsonify({'status': 'error', 'message': 'No se recibieron archivos.'}), 400

        modelo = EvidenciaModel()
        nuevo_id = modelo.registrar_evidencias(files, form_data)

        if nuevo_id:
            return jsonify({
                'status': 'success',
                'message': f'Evidencias registradas correctamente (ID: {nuevo_id}).',
                'id': nuevo_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo guardar las evidencias en la base de datos.'
            }), 500

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
        form_data = request.form

        if not files:
            return jsonify({
                'status': 'error',
                'message': 'Debe seleccionar al menos una imagen nueva.'
            }), 400

        modelo = EvidenciaModel()
        
        # ValidaciÃ³n de existencia en tiempo real
        if not modelo.validar_evidencia_activa(id_evidencia):
            return jsonify({
                'status': 'error',
                'message': 'La evidencia no existe o fue eliminada.'
            }), 404
        
        exito = modelo.actualizar_evidencia(id_evidencia, files, form_data)

        if exito:
            return jsonify({
                'status': 'success',
                'message': 'Evidencia actualizada correctamente.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo actualizar la evidencia.'
            }), 500

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
    Ruta para borrado lÃ³gico de evidencias.
    Cambia el estado a 0 sin eliminar fÃsicamente.
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesiÃ³n.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = EvidenciaModel()
        
        if modelo.eliminar_evidencia(id_evidencia):
            flash('Evidencia desactivada correctamente (Borrado LÃ³gico).', 'success')
        else:
            flash('No se pudo desactivar la evidencia.', 'error')
            
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        flash('Error interno del servidor.', 'error')
    
    return redirect(url_for('evidencia_bp.show_listar_evidencias'))
