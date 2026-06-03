from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *
from controllers.funciones_solicitud import *

PATH_URL = "public/solicitudes"


@app.route('/registrar-solicitud', methods=['GET'])
def viewFormSolicitud():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_solicitud.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/registrar-mortadela', methods=['GET'])
def viewFormMortadela():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_mortadela.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/form-registrar-solicitud', methods=['POST'])
def formSolicitud():
    # Verificar sesión
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    # Aceptar envío con o sin archivo 'foto_solicitud'
    foto_perfil = None
    if 'foto_solicitud' in request.files and request.files['foto_solicitud'].filename != '':
        foto_perfil = request.files['foto_solicitud']

    resultado = procesar_form_solicitud(request.form, foto_perfil)
    if resultado:
        return redirect(url_for('lista_solicitudes'))
    else:
        flash('La solicitud NO fue registrada.', 'error')
        return render_template(f'{PATH_URL}/form_solicitud.html')


@app.route('/lista-de-solicitudes', methods=['GET'])
def lista_solicitudes():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/lista_solicitudes.html', solicitudes=sql_lista_solicitudesBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/detalles-solicitud/", methods=['GET'])
@app.route("/detalles-solicitud/<int:idSolicitud>", methods=['GET'])
def detalleSolicitud(idSolicitud=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idSolicitud es None o no está presente en la URL
        if idSolicitud is None:
            return redirect(url_for('inicio'))
        else:
            detalle_solicitud = sql_detalles_solicitudesBD(idSolicitud) or []
            return render_template(f'{PATH_URL}/detalles_solicitud.html', detalle_solicitud=detalle_solicitud)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Buscadon de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})


@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuestaEmpleado = buscarEmpleadoUnico(id)
        if respuestaEmpleado:
            return render_template(f'{PATH_URL}/form_empleado_update.html', respuestaEmpleado=respuestaEmpleado)
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Recibir formulario para actulizar informacion de empleado
@app.route('/actualizar-empleado', methods=['POST'])
def actualizarEmpleado():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_empleados'))


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))

@app.route('/registrar-usuario', methods=['GET'])
def viewFormUsuario():
    if 'conectado' in session:
        return render_template('public/usuarios/form_usuario.html')
    else:
        return redirect(url_for('inicio'))

@app.route('/form-registrar-usuario', methods=['POST'])
def formUsuario():
    if 'conectado' in session:
        if registrarUsuarioBD(request.form):
            flash('El usuario fue registrado correctamente.', 'success')
            return redirect(url_for('usuarios'))
        else:
            flash('Error al registrar el usuario.', 'error')
            return render_template('public/usuarios/form_usuario.html')
    else:
        return redirect(url_for('inicio'))

@app.route('/editar-usuario/<string:id>', methods=['GET'])
def viewEditarUsuario(id):
    if 'conectado' in session:
        usuario = buscarUsuarioUnico(id)
        if usuario:
            return render_template('public/usuarios/form_usuario_update.html', usuario=usuario)
        else:
            flash('El usuario no existe.', 'error')
            return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('inicio'))

@app.route('/actualizar-usuario', methods=['POST'])
def actualizarUsuario():
    if 'conectado' in session:
        if actualizarUsuarioBD(request.form):
            flash('El usuario fue actualizado correctamente.', 'success')
            return redirect(url_for('usuarios'))
        else:
            flash('Error al actualizar el usuario.', 'error')
            return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('inicio'))


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


@app.route('/borrar-empleado/<string:id_empleado>/<string:foto_empleado>', methods=['GET'])
def borrarEmpleado(id_empleado, foto_empleado):
    resp = eliminarEmpleado(id_empleado, foto_empleado)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_empleados'))


@app.route("/descargar-informe-empleados/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
