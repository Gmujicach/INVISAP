from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.model_empleados import EmpleadoModel

# Se corrige template_folder para que apunte a la carpeta raíz de vistas
empleado_bp = Blueprint('empleado_bp', __name__, template_folder='../vista', url_prefix='/empleados')

model = EmpleadoModel()


@empleado_bp.route('', methods=['GET'])
@empleado_bp.route('/', methods=['GET'])
def list_empleados():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    empleados = model.get_all_empleados()
    return render_template('empleados/empleados.html', resp_empleadosBD=empleados)


@empleado_bp.route('/create', methods=['GET'])
def create_form():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('empleados/form_empleado.html')


@empleado_bp.route('/create', methods=['POST'])
def create_empleado():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        # El modelo ahora maneja la validación y la persistencia
        res = model.registrar_empleado(request.form)
        if res:
            return jsonify({'status': 'success', 'message': 'Empleado registrado correctamente.'})
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo registrar el empleado. Verifique los datos.'}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        print(f"Error en create_empleado: {e}") # Para depuración
        return jsonify({'status': 'error', 'message': 'Error interno del servidor.'}), 500


@empleado_bp.route('/edit/<int:id_empleado>', methods=['GET'])
def edit_form(id_empleado):
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    empleado = model.get_empleado_by_id(id_empleado)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleado_bp.list_empleados'))
    return render_template('empleados/form_empleado_update.html', empleado=empleado)


@empleado_bp.route('/update', methods=['POST']) # Este endpoint recibirá la petición Fetch
def update_empleado():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        res = model.actualizar_empleado(request.form)
        if res:
            return jsonify({'status': 'success', 'message': 'Empleado actualizado correctamente.'})
        else:
            return jsonify({'status': 'error', 'message': 'No se pudo actualizar el empleado. Verifique los datos.'}), 400
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        print(f"Error en update_empleado: {e}") # Para depuración
        return jsonify({'status': 'error', 'message': 'Error interno del servidor.'}), 500


@empleado_bp.route('/delete/<int:id_empleado>', methods=['GET'])
def delete_empleado(id_empleado):
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    res = model.eliminar_empleado_logico(id_empleado)
    if res:
        flash('Empleado eliminado correctamente', 'success')
    else:
        flash('Error al eliminar empleado', 'error')
    return redirect(url_for('empleado_bp.list_empleados'))
