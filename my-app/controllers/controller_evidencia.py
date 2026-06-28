from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models.model_evidencia import EvidenciaModel

evidencia_bp = Blueprint('evidencia_bp', __name__, template_folder='../vista')

@evidencia_bp.route('/evidencias/registrar', methods=['GET'])
def show_registrar_evidencia():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('evidencia/evidencia.html')

@evidencia_bp.route('/evidencias/listar', methods=['GET'])
def show_listar_evidencias():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    modelo = EvidenciaModel()
    evidencias = modelo.obtener_todas_evidencias()
    return render_template('evidencia/lista_evidencias.html', evidencias=evidencias)

@evidencia_bp.route('/evidencias/modificar/<int:id_evidencia>', methods=['GET'])
def show_modificar_evidencia(id_evidencia):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    modelo = EvidenciaModel()
    evidencia = modelo.obtener_evidencia_por_id(id_evidencia)
    if not evidencia:
        flash('La evidencia no existe', 'error')
        return redirect(url_for('evidencia_bp.show_listar_evidencias'))
    return render_template('evidencia/evidencia_modificar.html', evidencia=evidencia)

@evidencia_bp.route('/api/evidencias/subir', methods=['POST'])
def api_subir_evidencias():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401
    try:
        files = request.files.getlist('fotos')
        etapas = request.form.getlist('etapas[]')
        
        if not files or len(files) == 0:
            return jsonify({'status': 'error', 'message': 'No se recibieron archivos'}), 400
        if not etapas or len(etapas) == 0:
            return jsonify({'status': 'error', 'message': 'No se recibieron etapas'}), 400
            
        modelo = EvidenciaModel()
        ids_insertados = modelo.registrar_evidencias(files, etapas)
        
        if ids_insertados and len(ids_insertados) > 0:
            return jsonify({'status': 'success', 'message': f'{len(ids_insertados)} evidencias registradas correctamente'})
        else:
            return jsonify({'status': 'error', 'message': 'Fallo en base de datos'}), 500
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}'}), 500

@evidencia_bp.route('/api/evidencias/actualizar/<int:id_evidencia>', methods=['POST'])
def api_actualizar_evidencia(id_evidencia):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401
    try:
        files = request.files.getlist('fotos')
        etapas = request.form.getlist('etapas[]')
        
        if not files or len(files) == 0:
            return jsonify({'status': 'error', 'message': 'Debe seleccionar una imagen nueva'}), 400
        if not etapas or len(etapas) == 0:
            return jsonify({'status': 'error', 'message': 'Debe seleccionar una etapa'}), 400
            
        modelo = EvidenciaModel()
        exito = modelo.actualizar_evidencia(id_evidencia, files, etapas)
        
        if exito:
            return jsonify({'status': 'success', 'message': 'Evidencia actualizada correctamente'})
        else:
            return jsonify({'status': 'error', 'message': 'Fallo al actualizar'}), 500
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}'}), 500

@evidencia_bp.route('/api/evidencias/validar/<int:id_evidencia>', methods=['GET'])
def api_validar_evidencia(id_evidencia):
    modelo = EvidenciaModel()
    existe = modelo.validar_evidencia_activa(id_evidencia)
    return jsonify({'existe': existe, 'id': id_evidencia})

@evidencia_bp.route('/evidencias/eliminar/<int:id_evidencia>', methods=['GET'])
def eliminar_evidencia(id_evidencia):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion', 'error')
        return redirect(url_for('login_bp.inicio'))
    try:
        modelo = EvidenciaModel()
        if modelo.eliminar_evidencia(id_evidencia):
            flash('Evidencia desactivada correctamente', 'success')
        else:
            flash('No se pudo desactivar', 'error')
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception:
        flash('Error interno', 'error')
    return redirect(url_for('evidencia_bp.show_listar_evidencias'))