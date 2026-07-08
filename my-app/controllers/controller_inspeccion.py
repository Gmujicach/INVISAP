"""
Controller de Inspecciones - Implementa comunicacion asincrona con Fetch/Ajax.
Rutas de vistas y API.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models.model_inspeccion import InspeccionModel

inspeccion_bp = Blueprint('inspeccion_bp', __name__, template_folder='../vista', url_prefix='/inspecciones')

PATH_URL_INSPECCION = "inspeccion"

# ========== RUTAS DE VISTAS (GET) ==========

@inspeccion_bp.route('', methods=['GET'])
@inspeccion_bp.route('/', methods=['GET'])
def list_inspecciones():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion.', 'error')
        return redirect(url_for('login_bp.inicio'))

    try:
        modelo = InspeccionModel()
        inspecciones = modelo.obtener_todas_inspecciones()
        tipos_inspeccion = modelo.obtener_catalogo_tipos_inspeccion()
        print(f'[LISTADO] Renderizando listado con {len(inspecciones)} inspecciones')
        if inspecciones:
            print(f'[LISTADO] Ultima inspeccion: id={inspecciones[0].get("id_inspeccion")} fecha={inspecciones[0].get("fecha_inspeccion")}')
        return render_template(f'{PATH_URL_INSPECCION}/inspeccion_lista.html',
                               inspecciones=inspecciones,
                               tipos_inspeccion=tipos_inspeccion)
    except Exception as e:
        print(f"[LISTADO] Error al cargar listado: {e}")
        flash('Error al cargar las inspecciones. Por favor, intente nuevamente.', 'error')
        return render_template(f'{PATH_URL_INSPECCION}/inspeccion_lista.html',
                               inspecciones=[],
                               tipos_inspeccion=[])


@inspeccion_bp.route('/crear', methods=['GET'])
def view_form_inspeccion():
    """Muestra el formulario de registro de inspecciones."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion.', 'error')
        return redirect(url_for('login_bp.inicio'))

    modelo = InspeccionModel()
    tipos_inspeccion = modelo.obtener_catalogo_tipos_inspeccion()
    return render_template(f'{PATH_URL_INSPECCION}/inspeccion.html',
                           tipos_inspeccion=tipos_inspeccion)


@inspeccion_bp.route('/editar/<int:id_inspeccion>', methods=['GET'])
def view_editar_inspeccion(id_inspeccion):
    """Muestra el formulario de edicion de inspeccion."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion.', 'error')
        return redirect(url_for('login_bp.inicio'))

    modelo = InspeccionModel()
    inspeccion = modelo.obtener_inspeccion_por_id(id_inspeccion)

    if not inspeccion:
        flash('La inspeccion no existe o fue eliminada.', 'error')
        return redirect(url_for('inspeccion_bp.list_inspecciones'))

    tipos_inspeccion = modelo.obtener_catalogo_tipos_inspeccion()
    return render_template(f'{PATH_URL_INSPECCION}/inspeccion_editar.html',
                           inspeccion=inspeccion,
                           tipos_inspeccion=tipos_inspeccion)


# ========== RUTAS API (POST/DELETE/GET) - Comunicacion Asincrona ==========

@inspeccion_bp.route('/api/crear', methods=['POST'])
def api_crear_inspeccion():
    """
    API para crear inspecciones mediante Fetch/Ajax.
    Evita recargas de pagina segun instrucciones del profesor.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        data = request.form
        print('[API] /inspecciones/api/crear called', dict(data))
        modelo = InspeccionModel()
        nuevo_id = modelo.registrar_inspeccion(data)
        print('[API] nuevo_id:', nuevo_id)

        if nuevo_id:
            return jsonify({
                'status': 'success',
                'message': 'Inspeccion registrada correctamente.',
                'id': nuevo_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo guardar la inspeccion en la base de datos.'
            }), 500

    except ValueError as ve:
        print('[API] ValueError:', ve)
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        print(f'[API] Error en api_crear_inspeccion: {e}')
        mensaje = 'Error interno del servidor.'
        if 'cedula_UNIQUE' in str(e):
            mensaje = 'Error de integridad en la base de datos (cedula_UNIQUE). Ejecute el script SQL de limpieza de la tabla inspeccion.'
        elif 'Unknown column' in str(e):
            mensaje = 'Error de estructura en la base de datos. Faltan columnas en la tabla inspeccion.'
        return jsonify({
            'status': 'error',
            'message': mensaje
        }), 500


@inspeccion_bp.route('/api/actualizar/<int:id_inspeccion>', methods=['POST'])
def api_actualizar_inspeccion(id_inspeccion):
    """
    API para actualizar inspecciones mediante Fetch/Ajax.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        data = request.form
        data = data.copy()
        data['id_inspeccion'] = id_inspeccion

        modelo = InspeccionModel()
        exito = modelo.actualizar_inspeccion(data)

        if exito:
            return jsonify({
                'status': 'success',
                'message': 'Inspeccion actualizada correctamente.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo actualizar la inspeccion.'
            }), 500

    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        print(f"Error en api_actualizar_inspeccion: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor.'
        }), 500


@inspeccion_bp.route('/api/validar/<int:id_inspeccion>', methods=['GET'])
def api_validar_inspeccion(id_inspeccion):
    """
    API para validar existencia de inspeccion en tiempo real.
    Usado por eventos 'change' en selectores (Ajax).
    """
    modelo = InspeccionModel()
    existe = modelo.validar_inspeccion_activa(id_inspeccion)
    return jsonify({'existe': existe, 'id': id_inspeccion})


@inspeccion_bp.route('/api/validar-obra/<int:obra_id>', methods=['GET'])
def api_validar_obra(obra_id):
    """Valida que la obra exista en la base de datos."""
    if 'conectado' not in session:
        return jsonify({'existe': False}), 401

    modelo = InspeccionModel()
    existe = modelo.obra_existe(obra_id)
    return jsonify({'existe': existe, 'id_obra': obra_id})


@inspeccion_bp.route('/api/validar-evidencia/<int:evidencia_id>', methods=['GET'])
def api_validar_evidencia(evidencia_id):
    """Valida que la evidencia exista en la base de datos."""
    if 'conectado' not in session:
        return jsonify({'existe': False}), 401

    modelo = InspeccionModel()
    existe = modelo.evidencia_existe(evidencia_id)
    return jsonify({'existe': existe, 'id_evidencia': evidencia_id})


@inspeccion_bp.route('/api/obras/listar', methods=['GET'])
def api_listar_obras():
    """Devuelve el listado de obras para poblar selects."""
    if 'conectado' not in session:
        return jsonify([]), 401

    modelo = InspeccionModel()
    return jsonify(modelo.obtener_obras())


@inspeccion_bp.route('/api/evidencias/listar', methods=['GET'])
def api_listar_evidencias():
    """Devuelve el listado de evidencias para poblar selects."""
    if 'conectado' not in session:
        return jsonify([]), 401

    try:
        modelo = InspeccionModel()
        evidencias = modelo.obtener_evidencias()
        return jsonify(evidencias)
    except Exception as e:
        print(f"Error al listar evidencias: {e}")
        return jsonify([]), 500


@inspeccion_bp.route('/api/inspectores/listar', methods=['GET'])
def api_listar_inspectores():
    if 'conectado' not in session:
        return jsonify([]), 401

    try:
        modelo = InspeccionModel()
        inspectores = modelo.obtener_inspectores()
        return jsonify(inspectores)
    except Exception as e:
        print(f"Error al listar inspectores: {e}")
        return jsonify({'error': str(e)}), 500


@inspeccion_bp.route('/eliminar/<int:id_inspeccion>', methods=['GET'])
def eliminar_inspeccion(id_inspeccion):
    """
    Ruta para borrado logico de inspecciones.
    Cambia el estado a 0 sin eliminar fisicamente.
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion.', 'error')
        return redirect(url_for('login_bp.inicio'))

    try:
        modelo = InspeccionModel()
        if modelo.eliminar_inspeccion(id_inspeccion):
            flash('Inspeccion desactivada correctamente (Borrado Logico).', 'success')
        else:
            flash('No se pudo desactivar la inspeccion.', 'error')
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        print(f"Error al eliminar inspeccion: {e}")
        flash('Error interno del servidor.', 'error')

    return redirect(url_for('inspeccion_bp.list_inspecciones'))
