from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.model_obra import ObraModel
from models.model_bitacora import BitacoraModel

obra_bp = Blueprint('obra_bp', __name__)

@obra_bp.route('/gestionar-obras', methods=['GET'])
def vista_gestionar_obras():
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))
        
    modelo = ObraModel()
    obras = modelo.obtener_todas()
    
    return render_template('obras/form_gestionar_obras.html', obras=obras)

@obra_bp.route('/form-registrar-obra', methods=['POST'])
def registrar_obra():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401
    
    try:
        data = request.form
        modelo = ObraModel()
        
        # Mapeo actualizado de las claves exactas de la tabla
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
            'semaforo_id_semaforo': data.get('semaforo_id_semaforo'),
            'contratacion_id_contratacion': data.get('contratacion_id_contratacion'),
            'gestionar_proyectos_codigo_proyecto': data.get('gestionar_proyectos_codigo_proyecto')
        }
        
        if modelo.registrar_obra(datos_insertar):
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='CREAR',
                descripcion=f"Registró la obra: {datos_insertar['titulo_obra']}"
            )
            return jsonify({'status': 'success', 'message': 'Obra registrada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Rechazado por Base de Datos. Revisa referencias.'}), 400
            
    except Exception as e:
        print(f"Error en controlador: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500


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


@obra_bp.route('/obra/actualizar/<int:id_obra>', methods=['POST'])
def actualizar_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401

    try:
        data = request.form
        modelo = ObraModel()

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
            'certificaciones_obras_ejecutadas': to_int(data.get('certificaciones_obras_ejecutadas'), 0),
            'numero_contrato': data.get('numero_contrato'),
            'porcentaje_avance_obra': to_int(data.get('porcentaje_avance_obra'), 0),
        }

        if modelo.actualizar_obra(id_obra, datos_actualizar):
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='EDITAR',
                descripcion=f"Actualizó la obra #{id_obra}: {datos_actualizar['titulo_obra']}"
            )
            return jsonify({'status': 'success', 'message': 'Obra actualizada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo actualizar la obra en la base de datos.'}), 400

    except Exception as e:
        print(f"Error en controlador actualizar_obra: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500


@obra_bp.route('/obra/eliminar/<int:id_obra>', methods=['GET'])
def eliminar_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401

    try:
        modelo = ObraModel()
        obra = modelo.obtener_obra_por_id(id_obra)
        if not obra:
            return jsonify({'status': 'error', 'message': 'La obra no existe o fue eliminada.'}), 404

        if modelo.eliminar_obra(id_obra):
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='ELIMINAR',
                descripcion=f"Eliminó la obra #{id_obra}: {obra.get('titulo_obra')}"
            )
            return jsonify({'status': 'success', 'message': 'Obra eliminada correctamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo eliminar la obra.'}), 400

    except Exception as e:
        print(f"Error en controlador eliminar_obra: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500
