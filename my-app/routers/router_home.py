from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *
from controllers.UserController import user_bp # Import the user blueprint
from controllers.funciones_solicitud import *
from controllers.EmpleadoController import empleado_bp

PATH_URL = "vista/solicitudes"
PATH_URLG = "vista/gerencias"
PATH_URL_INF = "vista/inf_avance_obra"


# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(empleado_bp)

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
    
@app.route('/registrar-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_contratacion.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/registrar-gerencias', methods=['GET'])
def viewFormGerencias():
    if 'conectado' in session:
        return render_template(f'{PATH_URLG}/form_gerencia.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/inf_avance_obra', methods=['GET'])
def viewFormInforme_avan_obras():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_INF}/inf_avance_obra.html')
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

    # usar la función de creación de solicitante
    resultado = None
    try:
        from controllers.funciones_solicitud import crear_solicitante
        resultado = crear_solicitante(request.form)
    except Exception:
        resultado = 0

    if resultado:
        return redirect(url_for('lista_solicitudes'))
    else:
        flash('La solicitud NO fue registrada.', 'error')
        return render_template(f'{PATH_URL}/form_solicitud.html')


@app.route('/lista-de-solicitudes', methods=['GET'])
def lista_solicitudes():
    if 'conectado' in session:
        from controllers.funciones_solicitud import obtener_solicitantes
        return render_template(f'{PATH_URL}/lista_solicitudes.html', solicitudes=obtener_solicitantes())
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
            from controllers.funciones_solicitud import obtener_solicitante_por_id
            detalle_solicitud = obtener_solicitante_por_id(idSolicitud) or []
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
