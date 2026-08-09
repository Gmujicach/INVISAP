"""
Controller de Empleados - Implementa comunicación asíncrona con Fetch/Ajax.
"""
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models.model_empleados import EmpleadoModel
from services.bitacora_service import BitacoraService

empleado_bp = Blueprint('empleado_bp', __name__, template_folder='../vista', url_prefix='/empleados')


# ========== RUTAS DE VISTAS (GET) ==========

@empleado_bp.route('', methods=['GET'])
@empleado_bp.route('/', methods=['GET'])
def list_empleados():
    """Muestra el listado de empleados activos paginados."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    modelo = EmpleadoModel()
    empleados = modelo.obtener_empleados_paginados(page=page, per_page=per_page)
    total_empleados = modelo.contar_empleados()
    total_pages = (total_empleados + per_page - 1) // per_page
    
    return render_template('empleados/empleados.html', 
                           resp_empleadosBD=empleados,
                           page=page,
                           per_page=per_page,
                           total_empleados=total_empleados,
                           total_pages=total_pages)


@empleado_bp.route('/create', methods=['GET'])
def viewFormEmpleado():
    """Muestra el formulario de registro de empleados."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    modelo = EmpleadoModel()
    cargos = modelo.obtener_catalogo_cargos()
    return render_template('empleados/form_empleado.html', cargos=cargos)


@empleado_bp.route('/edit/<int:id_empleado>', methods=['GET'])
def viewEditarEmpleado(id_empleado):
    """Muestra el formulario de edición de empleado."""
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    modelo = EmpleadoModel()
    empleado = modelo.obtener_empleado_por_id(id_empleado)
    
    if not empleado:
        flash('El empleado no existe o fue eliminado.', 'error')
        return redirect(url_for('empleado_bp.list_empleados'))
    
    cargos = modelo.obtener_catalogo_cargos()
    return render_template('empleados/form_empleado_update.html', empleado=empleado, cargos=cargos)


# ========== RUTAS API (POST/DELETE) - Comunicación Asíncrona ==========

@empleado_bp.route('/api/create', methods=['POST'])
def api_crear_empleado():
    """
    API para crear empleados mediante Fetch/Ajax.
    Evita recargas de página según instrucciones del profesor.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        data = request.form
        modelo = EmpleadoModel()
        nuevo_id = modelo.registrar_empleado(data)

        if nuevo_id:
            BitacoraService.registrar_accion(
                session, 'Empleados', 'CREAR',
                f'Registró un nuevo empleado con ID: {nuevo_id}'
            )
            return jsonify({
                'status': 'success',
                'message': 'Empleado registrado correctamente.',
                'id': nuevo_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo guardar el empleado en la base de datos.'
            }), 500

    except ValueError as ve:
        # Errores de validación (Regex, cargo inválido, etc.)
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        print(f"Error en api_crear_empleado: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor.'
        }), 500


@empleado_bp.route('/api/update', methods=['POST'])
def api_actualizar_empleado():
    """
    API para actualizar empleados mediante Fetch/Ajax.
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        data = request.form
        modelo = EmpleadoModel()
        
        # Validación de existencia en tiempo real
        id_empleado = int(data.get('id_empleado'))
        if not modelo.validar_empleado_activo(id_empleado):
            return jsonify({
                'status': 'error',
                'message': 'El empleado no existe o fue eliminado.'
            }), 404
        
        exito = modelo.actualizar_empleado(data)

        if exito:
            BitacoraService.registrar_accion(
                session, 'Empleados', 'EDITAR',
                f'Actualizó el empleado ID: {id_empleado}'
            )
            return jsonify({
                'status': 'success',
                'message': 'Empleado actualizado correctamente.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo actualizar el empleado.'
            }), 500

    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        print(f"Error en api_actualizar_empleado: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor.'
        }), 500


@empleado_bp.route('/api/validar/<int:id_empleado>', methods=['GET'])
def api_validar_empleado(id_empleado):
    """
    API para validar existencia de empleado en tiempo real.
    Usado por eventos 'change' en selectores (Ajax).
    """
    modelo = EmpleadoModel()
    existe = modelo.validar_empleado_activo(id_empleado)
    return jsonify({'existe': existe, 'id': id_empleado})


@empleado_bp.route('/api/por-cargo/<string:cargo>', methods=['GET'])
def api_empleados_por_cargo(cargo):
    """
    API para obtener empleados filtrados por cargo.
    Usado por otros módulos (inspecciones, proyectos, etc.)
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401
    
    modelo = EmpleadoModel()
    empleados = modelo.obtener_empleados_por_cargo(cargo)
    return jsonify({'status': 'success', 'empleados': empleados})


@empleado_bp.route('/delete/<int:id_empleado>', methods=['GET'])
def eliminar_empleado(id_empleado):
    """
    Ruta para borrado lógico de empleados.
    Cambia el estado a 0 sin eliminar físicamente.
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = EmpleadoModel()
        
        if modelo.eliminar_empleado_logico(id_empleado):
            BitacoraService.registrar_accion(
                session, 'Empleados', 'ELIMINAR',
                f'Desactivó el empleado ID: {id_empleado}'
            )
            flash('Empleado desactivado correctamente (Borrado Lógico).', 'success')
        else:
            flash('No se pudo desactivar el empleado.', 'error')
            
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        print(f"Error al eliminar empleado: {e}")
        flash('Error interno del servidor.', 'error')
    
    return redirect(url_for('empleado_bp.list_empleados'))