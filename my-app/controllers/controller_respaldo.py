from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_file, flash
import os
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara
from models.model_respaldo import RespaldoModel
from services.bitacora_service import BitacoraService

respaldo_bp = Blueprint('respaldo_bp', __name__, template_folder='../vista', url_prefix='/respaldo')
modelo_respaldo = RespaldoModel()
CARPETA_RESPALDOS = os.path.join('static', 'respaldos_bd')


def _serializar_respaldo(r):
    r = dict(r)
    r['tamano_formateado'] = modelo_respaldo._formatear_tamano(r.get('tamano', 0) or 0)
    if r.get('fecha_respaldo'):
        r['fecha_respaldo'] = r['fecha_respaldo'].isoformat()
    return r


@respaldo_bp.route('', methods=['GET'])
@respaldo_bp.route('/', methods=['GET'])
def listar_respaldos_view():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    respaldos = modelo_respaldo.listar_respaldos()
    return render_template('respaldo/form_respaldo.html', respaldos=respaldos)


@respaldo_bp.route('/api/listar-json', methods=['GET'])
def api_listar_respaldos():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    respaldos = modelo_respaldo.listar_respaldos()
    respaldos = [_serializar_respaldo(r) for r in respaldos]
    return jsonify({'status': 'success', 'respaldos': respaldos})


@respaldo_bp.route('/exportar', methods=['POST'])
def exportar_respaldo():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        descripcion = request.form.get('descripcion', '')
        resultado = modelo_respaldo.crear_respaldo(descripcion)
        BitacoraService.registrar_accion(
            session, 'Respaldos', 'CREAR',
            f'Generó un respaldo de la base de datos'
        )
        return jsonify({
            'status': 'success',
            'message': 'Respaldo generado correctamente.',
            'download_url': url_for('respaldo_bp.descargar_respaldo', nombre_archivo=resultado['nombre_archivo'])
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@respaldo_bp.route('/descargar/<string:nombre_archivo>', methods=['GET'])
def descargar_respaldo(nombre_archivo):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    ruta = os.path.join(CARPETA_RESPALDOS, nombre_archivo)
    if not os.path.exists(ruta):
        flash('El archivo de respaldo no existe.', 'error')
        return redirect(url_for('respaldo_bp.listar_respaldos_view'))

    return send_file(ruta, as_attachment=True, download_name=nombre_archivo)


@respaldo_bp.route('/importar', methods=['POST'])
def importar_respaldo():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    archivo = request.files.get('archivo')
    if not archivo or archivo.filename == '':
        return jsonify({'status': 'error', 'message': 'Debe seleccionar un archivo .sql'}), 400

    if not archivo.filename.lower().endswith('.sql'):
        return jsonify({'status': 'error', 'message': 'El archivo debe tener extensión .sql'}), 400

    descripcion = request.form.get('descripcion', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"importado_{timestamp}.sql"
    ruta_temporal = os.path.join(CARPETA_RESPALDOS, nombre_archivo)

    try:
        if not os.path.exists(CARPETA_RESPALDOS):
            os.makedirs(CARPETA_RESPALDOS, exist_ok=True)

        archivo.save(ruta_temporal)
        modelo_respaldo.importar_respaldo(ruta_temporal, descripcion)
        BitacoraService.registrar_accion(
            session, 'Respaldos', 'EDITAR',
            f'Importó un respaldo de la base de datos'
        )
        return jsonify({
            'status': 'success',
            'message': 'Respaldo importado correctamente.'
        })
    except Exception as e:
        if os.path.exists(ruta_temporal):
            try:
                os.remove(ruta_temporal)
            except Exception:
                pass
        return jsonify({'status': 'error', 'message': str(e)}), 500


@respaldo_bp.route('/eliminar/<int:id_respaldo>', methods=['DELETE'])
def eliminar_respaldo(id_respaldo):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        exito = modelo_respaldo.eliminar_respaldo(id_respaldo)
        if exito:
            BitacoraService.registrar_accion(
                session, 'Respaldos', 'ELIMINAR',
                f'Eliminó el respaldo ID: {id_respaldo}'
            )
            return jsonify({'status': 'success', 'message': 'Respaldo eliminado correctamente.'})
        return jsonify({'status': 'error', 'message': 'No se encontró el respaldo o no se pudo eliminar.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
