from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.model_obra import ObraModel
from models.model_bitacora import BitacoraModel

obra_bp = Blueprint('obra_bp', __name__)


def _convertir_campos_numericos_obra(datos):
    try:
        datos['periodo_ejecucion'] = int(datos.get('periodo_ejecucion') or 0)
    except (TypeError, ValueError):
        return False, "Período de ejecución debe ser un número entero."
    try:
        datos['certificaciones_obras_ejecutadas'] = int(datos.get('certificaciones_obras_ejecutadas') or 0)
    except (TypeError, ValueError):
        return False, "Certificaciones ejecutadas debe ser un número entero."
    try:
        datos['porcentaje_avance_obra'] = int(datos.get('porcentaje_avance_obra') or 0)
    except (TypeError, ValueError):
        return False, "Porcentaje de avance debe ser un número entero."
    try:
        datos['semaforo_id_semaforo'] = int(datos.get('semaforo_id_semaforo') or 0)
    except (TypeError, ValueError):
        return False, "Semáforo inválido."
    try:
        datos['contratacion_id_contratacion'] = int(datos.get('contratacion_id_contratacion') or 0)
    except (TypeError, ValueError):
        return False, "Contratación inválida."
    return True, "OK"


@obra_bp.route('/gestionar-obras', methods=['GET'])
def vista_gestionar_obras():
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))

    modelo = ObraModel()
    obras = modelo.obtener_todas()

    return render_template('obras/form_gestionar_obras.html', obras=obras)


@obra_bp.route('/editar-obra/<int:id_obra>', methods=['GET'])
def vista_editar_obra(id_obra):
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))

    modelo = ObraModel()
    obra = modelo.obtener_obra_por_id(id_obra)
    if not obra:
        return redirect(url_for('obra_bp.vista_gestionar_obras'))

    return render_template('obras/form_obra_update.html', obra=obra)


@obra_bp.route('/form-registrar-obra', methods=['POST'])
def registrar_obra():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401

    try:
        data = request.form
        modelo = ObraModel()

        id_semaforo = data.get('semaforo_id_semaforo')
        id_contratacion = data.get('contratacion_id_contratacion')
        codigo_proyecto = data.get('gestionar_proyectos_codigo_proyecto')

        if not id_semaforo or not id_contratacion or not codigo_proyecto:
            return jsonify({'status': 'error', 'message': 'Debe seleccionar semáforo, contratación y proyecto.'}), 400

        datos_insertar = {
            'titulo_obra': data.get('titulo_obra'),
            'ubicacion_obra': data.get('ubicacion_obra'),
            'periodo_ejecucion': data.get('periodo_ejecucion'),
            'fecha_inicio': data.get('fecha_inicio'),
            'fecha_fin': data.get('fecha_fin'),
            'mediciones_obra': data.get('mediciones_obra'),
            'valuaciones': data.get('valuaciones'),
            'modificaciones_contrato': data.get('modificaciones_contrato'),
            'certificaciones_obras_ejecutadas': data.get('certificaciones_obras_ejecutadas'),
            'numero_contrato': data.get('numero_contrato'),
            'porcentaje_avance_obra': data.get('porcentaje_avance_obra'),
            'semaforo_id_semaforo': id_semaforo,
            'contratacion_id_contratacion': id_contratacion,
            'gestionar_proyectos_codigo_proyecto': codigo_proyecto
        }

        ok, msg = _convertir_campos_numericos_obra(datos_insertar)
        if not ok:
            return jsonify({'status': 'error', 'message': msg}), 400

        resultado, extra = modelo.registrar_obra(datos_insertar)
        if resultado:
            id_obra = extra
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='CREAR',
                descripcion=f"Registró la obra: {datos_insertar['titulo_obra']} (ID: {id_obra})"
            )
            return jsonify({'status': 'success', 'message': 'Obra registrada exitosamente.', 'id_obra': id_obra}), 200
        else:
            return jsonify({'status': 'error', 'message': extra}), 400

    except Exception as e:
        print(f"Error en controlador: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500


@obra_bp.route('/api/obra/obtener/<int:id_obra>', methods=['GET'])
def api_obtener_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida o expirada.'}), 401

    try:
        modelo = ObraModel()
        obra = modelo.obtener_obra_por_id(id_obra)
        if obra:
            return jsonify({'status': 'success', 'data': obra})
        return jsonify({'status': 'error', 'message': f'Obra ID {id_obra} no encontrada.'}), 404
    except Exception as e:
        print(f"Error en api_obtener_obra id={id_obra}: {e}")
        return jsonify({'status': 'error', 'message': f'Error interno: {e}'}), 500


@obra_bp.route('/api/obra/semaforos', methods=['GET'])
def api_listar_semaforos():
    if 'conectado' not in session:
        return jsonify([]), 401
    try:
        modelo = ObraModel()
        return jsonify(modelo.listar_semaforos())
    except Exception as e:
        print(f"Error en api_listar_semaforos: {e}")
        return jsonify([])


@obra_bp.route('/api/obra/contrataciones', methods=['GET'])
def api_listar_contrataciones():
    if 'conectado' not in session:
        return jsonify([]), 401
    try:
        modelo = ObraModel()
        return jsonify(modelo.listar_contrataciones())
    except Exception as e:
        print(f"Error en api_listar_contrataciones: {e}")
        return jsonify([])


@obra_bp.route('/api/obra/proyectos', methods=['GET'])
def api_listar_proyectos():
    if 'conectado' not in session:
        return jsonify([]), 401
    try:
        modelo = ObraModel()
        return jsonify(modelo.listar_proyectos())
    except Exception as e:
        print(f"Error en api_listar_proyectos: {e}")
        return jsonify([])


@obra_bp.route('/obra/detalle/<int:id_obra>', methods=['GET'])
def detalle_obra(id_obra):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesion.', 'error')
        return redirect(url_for('login_bp.inicio'))

    modelo = ObraModel()
    obra = modelo.obtener_obra_por_id(id_obra)
    if not obra:
        flash('La obra no existe o fue eliminada.', 'error')
        return redirect(url_for('obra_bp.vista_gestionar_obras'))

    avances = modelo.obtener_avances_por_obra(id_obra)
    return render_template('obras/detalle_obra.html', obra=obra, avances=avances)


@obra_bp.route('/obra/editar/<int:id_obra>', methods=['GET'])
def editar_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401

    modelo = ObraModel()
    obra = modelo.obtener_obra_por_id(id_obra)
    if not obra:
        return jsonify({'status': 'error', 'message': 'La obra no existe o fue eliminada.'}), 404

    return jsonify({'status': 'success', 'data': obra})


# Compatibility wrapper: support form POSTs that submit id_obra in form action
@obra_bp.route('/form-editar-obra', methods=['POST'])
def actualizar_obra_form():
    id_from_form = request.form.get('id_obra')
    if not id_from_form:
        return jsonify({'status': 'error', 'message': 'ID de obra no proporcionado.'}), 400
    try:
        return actualizar_obra(int(id_from_form))
    except Exception as e:
        print(f"Error en controlador actualizar_obra_form: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500


@obra_bp.route('/obra/actualizar/<int:id_obra>', methods=['POST'])
def actualizar_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401

    try:
        data = request.form
        modelo = ObraModel()

        # Aceptar id_obra por URL o por formulario (compatibilidad)
        if id_obra is None:
            id_obra = data.get('id_obra')
        if not id_obra:
            return jsonify({'status': 'error', 'message': 'ID de obra no proporcionado.'}), 400
        try:
            id_obra = int(id_obra)
        except (TypeError, ValueError):
            return jsonify({'status': 'error', 'message': 'ID de obra inválido.'}), 400

        id_semaforo = data.get('semaforo_id_semaforo')
        id_contratacion = data.get('contratacion_id_contratacion')
        codigo_proyecto = data.get('gestionar_proyectos_codigo_proyecto')

        if not id_semaforo or not id_contratacion or not codigo_proyecto:
            return jsonify({'status': 'error', 'message': 'Debe seleccionar semáforo, contratación y proyecto.'}), 400

        def to_int(value, default=0):
            if value is None or value == '':
                return default
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        datos_actualizar = {
            'titulo_obra': data.get('titulo_obra'),
            'ubicacion_obra': data.get('ubicacion_obra'),
            'periodo_ejecucion': to_int(data.get('periodo_ejecucion'), 0),
            'fecha_inicio': data.get('fecha_inicio'),
            'fecha_fin': data.get('fecha_fin'),
            'mediciones_obra': data.get('mediciones_obra'),
            'valuaciones': data.get('valuaciones'),
            'modificaciones_contrato': data.get('modificaciones_contrato'),
            'certificaciones_obras_ejecutadas': data.get('certificaciones_obras_ejecutadas'),
            'numero_contrato': data.get('numero_contrato'),
            'porcentaje_avance_obra': data.get('porcentaje_avance_obra'),
            'semaforo_id_semaforo': id_semaforo,
            'contratacion_id_contratacion': id_contratacion,
            'gestionar_proyectos_codigo_proyecto': codigo_proyecto
        }

        ok, msg = _convertir_campos_numericos_obra(datos_actualizar)
        if not ok:
            return jsonify({'status': 'error', 'message': msg}), 400

        resultado, extra = modelo.actualizar_obra(id_obra, datos_actualizar)
        if resultado:
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='EDITAR',
                descripcion=f"Actualizó la obra: {datos_actualizar['titulo_obra']} (ID: {id_obra})"
            )
            return jsonify({'status': 'success', 'message': 'Obra actualizada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': extra}), 400

    except Exception as e:
        print(f"Error en controlador actualizar_obra: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500


@obra_bp.route('/obra/eliminar/<int:id_obra>', methods=['GET'])
@obra_bp.route('/eliminar-obra/<int:id_obra>', methods=['GET', 'POST'])
def eliminar_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401

    try:
        modelo = ObraModel()
        obra = modelo.obtener_obra_por_id(id_obra)
        if not obra:
            return jsonify({'status': 'error', 'message': 'Obra no encontrada.'}), 404

        titulo = obra.get('titulo_obra', 'Desconocida')

        resultado, msg = modelo.eliminar_obra(id_obra)
        if resultado:
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='ELIMINAR',
                descripcion=f"Desactivó la obra: {titulo} (ID: {id_obra})"
            )
            return jsonify({'status': 'success', 'message': f'Obra "{titulo}" eliminada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': msg}), 400

    except Exception as e:
        print(f"Error en controlador eliminar_obra: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500
