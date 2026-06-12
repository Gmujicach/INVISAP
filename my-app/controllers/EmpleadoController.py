from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.empleados import EmpleadoModel

# Se corrige template_folder para que apunte a la carpeta raíz de vistas
empleado_bp = Blueprint('empleado_bp', __name__, template_folder='../vista', url_prefix='/empleados')

model = EmpleadoModel()


@empleado_bp.route('', methods=['GET'])
@empleado_bp.route('/', methods=['GET'])
def list_empleados():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    empleados = model.all()
    # Se ajusta la ruta del template y el nombre de la variable para compatibilidad con JS
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
    file = request.files.get('foto_empleado')
    res = model.create(request.form, file)
    if res:
        flash('Empleado creado correctamente', 'success')
    else:
        flash('Error al crear empleado', 'error')
    return redirect(url_for('empleado_bp.list_empleados'))


@empleado_bp.route('/edit/<int:id_empleado>', methods=['GET'])
def edit_form(id_empleado):
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    empleado = model.get(id_empleado)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleado_bp.list_empleados'))
    return render_template('empleados/form_empleado_update.html', empleado=empleado)


@empleado_bp.route('/update', methods=['POST'])
def update_empleado():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    file = request.files.get('foto_empleado')
    res = model.update(request.form, file)
    if res:
        flash('Empleado actualizado correctamente', 'success')
    else:
        flash('Error al actualizar empleado', 'error')
    return redirect(url_for('empleado_bp.list_empleados'))


@empleado_bp.route('/delete/<int:id_empleado>', methods=['GET'])
@empleado_bp.route('/delete/<int:id_empleado>/<path:foto>', methods=['GET'])
def delete_empleado(id_empleado, foto=None):
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    res = model.delete(id_empleado, foto)
    if res:
        flash('Empleado eliminado correctamente', 'success')
    else:
        flash('Error al eliminar empleado', 'error')
    return redirect(url_for('empleado_bp.list_empleados'))
