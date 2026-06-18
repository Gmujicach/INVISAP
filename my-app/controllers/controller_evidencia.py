from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models.model_evidencia import EvidenciaModel

evidencia_bp = Blueprint('evidencia_bp', __name__, template_folder='../vista')

@evidencia_bp.route('/evidencias/registrar', methods=['GET'])
def show_registrar_evidencia():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('evidencia/evidencia.html')

@evidencia_bp.route('/evidencias/listar', methods=['GET'])
def show_listar_evidencias():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    modelo = EvidenciaModel()
    evidencias = modelo.get_all_evidencias()
    return render_template('evidencia/lista_evidencias.html', evidencias=evidencias)

@evidencia_bp.route('/api/evidencias/subir', methods=['POST'])
def api_subir_evidencias():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        files = request.files.getlist('fotos')
        form_data = request.form
        modelo = EvidenciaModel()
        nuevo_id = modelo.registrar_informe_con_evidencias(files, form_data)

        if nuevo_id:
            return jsonify({'status': 'success', 'message': f'Informe de Avance de Obra #{nuevo_id} y sus evidencias han sido registrados.'})
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo guardar el informe.'}), 500

    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        print(f"Error en api_subir_evidencias: {e}") # Log para desarrollo
        return jsonify({'status': 'error', 'message': 'Error interno del servidor.'}), 500