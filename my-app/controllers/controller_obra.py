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
        
        semaforo_ok = modelo.validar_semaforo(id_semaforo)
        if not semaforo_ok:
            return jsonify({'status': 'error', 'message': 'El semáforo seleccionado no existe.'}), 400
        contratacion_ok = modelo.validar_contratacion(id_contratacion)
        if not contratacion_ok:
            return jsonify({'status': 'error', 'message': 'La contratación seleccionada no existe.'}), 400
        proyecto_ok = modelo.validar_proyecto(codigo_proyecto)
        if not proyecto_ok:
            return jsonify({'status': 'error', 'message': 'El proyecto seleccionado no existe o está inactivo.'}), 400
        
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


@obra_bp.route('/form-editar-obra', methods=['POST'])
def actualizar_obra():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401
    
    try:
        data = request.form
        id_obra = data.get('id_obra')
        
        if not id_obra:
            return jsonify({'status': 'error', 'message': 'ID de obra no proporcionado.'}), 400
        
        modelo = ObraModel()
        
        id_semaforo = data.get('semaforo_id_semaforo')
        id_contratacion = data.get('contratacion_id_contratacion')
        codigo_proyecto = data.get('gestionar_proyectos_codigo_proyecto')
        
        if not id_semaforo or not id_contratacion or not codigo_proyecto:
            return jsonify({'status': 'error', 'message': 'Debe seleccionar semáforo, contratación y proyecto.'}), 400
        
        if not modelo.validar_semaforo(id_semaforo):
            return jsonify({'status': 'error', 'message': 'El semáforo seleccionado no existe.'}), 400
        if not modelo.validar_contratacion(id_contratacion):
            return jsonify({'status': 'error', 'message': 'La contratación seleccionada no existe.'}), 400
        if not modelo.validar_proyecto(codigo_proyecto):
            return jsonify({'status': 'error', 'message': 'El proyecto seleccionado no existe.'}), 400
        
        datos_actualizar = {
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
        
        ok, msg = _convertir_campos_numericos_obra(datos_actualizar)
        if not ok:
            return jsonify({'status': 'error', 'message': msg}), 400
        
        if modelo.actualizar_obra(id_obra, datos_actualizar):
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='EDITAR',
                descripcion=f"Actualizó la obra: {datos_actualizar['titulo_obra']} (ID: {id_obra})"
            )
            return jsonify({'status': 'success', 'message': 'Obra actualizada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No se realizaron cambios o la obra no existe.'}), 400
            
    except Exception as e:
        print(f"Error en controlador actualizar: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500


@obra_bp.route('/eliminar-obra/<int:id_obra>', methods=['GET', 'POST'])
def eliminar_obra(id_obra):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401
    
    try:
        modelo = ObraModel()
        obra = modelo.obtener_obra_por_id(id_obra)
        
        if not obra:
            return jsonify({'status': 'error', 'message': 'Obra no encontrada.'}), 404
        
        titulo = obra.get('titulo_obra', 'Desconocida')
        
        if modelo.eliminar_obra(id_obra):
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='ELIMINAR',
                descripcion=f"Desactivó la obra: {titulo} (ID: {id_obra})"
            )
            return jsonify({'status': 'success', 'message': f'Obra "{titulo}" eliminada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo eliminar la obra.'}), 400
            
    except Exception as e:
        print(f"Error en controlador eliminar: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500
