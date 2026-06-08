from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *
from controllers.UserController import user_bp # Import the user blueprint
from controllers.funciones_solicitud import *
from controllers.EmpleadoController import empleado_bp
from controllers.controller_reportesExcel import reporte_excel_bp
from controllers.controller_reportesPDF import reporte_pdf_bp

PATH_URL = "solicitudes"
PATH_URL_CONTRAT = "contratacion"
PATH_URLG = "gerencias"
PATH_URL_RES = "respaldo"
PATH_URL_INF = "inf_avance_obra"
PATH_URL_PROY = "proyectos"
PATH_URL_GEST_OBR = "obras"
PATH_URL_PUB = "publicaciones"
PATH_URL_IA = "ia"
PATH_URL_EMPLEADOS = "empleados"
PATH_URL_REPORTE_EXCEL = "reportes"
PATH_URL_REPORTE_PDF = "reportes"
PATH_URL_REPORTE_ESTADISTICO = "reportes"


# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(empleado_bp)
app.register_blueprint(reporte_excel_bp)
app.register_blueprint(reporte_pdf_bp)

@app.route('/registrar-solicitud', methods=['GET'])
def viewFormSolicitud():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_solicitud.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/registrar-publicaciones', methods=['GET'])
def viewFormPublicaciones():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_PUB}/form_publicaciones.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/administrar-respaldos', methods=['GET'])
def viewFormRespaldos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_RES}/form_respaldo.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/registrar-maquinaria', methods=['GET'])
@app.route('/maquinaria', methods=['GET'])
def viewFormMaquinaria():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_PROY}/form_maquinaria.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))    


@app.route('/registrar-mortadela', methods=['GET'])
def viewFormMortadela():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_mortadela.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    
@app.route('/gestionar-obras', methods=['GET'])
def viewFormGestionarObras():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_GEST_OBR}/form_gestionar_obras.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    

@app.route('/gestionar-gravedad', methods=['GET'])
def viewFormGravedad():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_gestionar_gravedad.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@app.route('/priorizar-solicitudes', methods=['GET'])
def viewPriorizarSolicitudes():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_priorizar_solicitudes.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/gestionar-prioridad', methods=['GET'])
def viewFormPrioridad():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_gestionar_prioridad.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


@app.route('/gestionar-proyectos', methods=['GET'])
def viewFormProyectos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_PROY}/form_maquinaria.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


@app.route('/empresa', methods=['GET'])
def viewFormEmpresa():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_CONTRAT}/form_contratacion.html', empresas=[])
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


@app.route('/inspectores', methods=['GET'])
def viewFormInspectores():
    if 'conectado' in session:
        return render_template('placeholder.html', title='Inspectores', message='Esta página está en desarrollo.', note='Contacto al administrador para habilitar esta función.')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


@app.route('/registrar-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_CONTRAT}/form_contratacion.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/registrar-gerencias', methods=['GET'])
def viewFormGerencia():
    if 'conectado' in session:
        return render_template(f'{PATH_URLG}/form_gerencia.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


@app.route('/bitacora', methods=['GET'])
def viewBitacora():
    if 'conectado' in session:
        return render_template('placeholder.html', title='Bitacora', message='Esta página está en desarrollo.', note='Contacto al administrador para habilitar esta función.')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


@app.route('/inf_avance_obra', methods=['GET'])
def viewFormInforme_avan_obras():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_INF}/inf_avance_obra.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/form-registrar-solicitud', methods=['POST'])
def formSolicitud():
    # Verificar sesión
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

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
        return redirect(url_for('login_bp.inicio'))


@app.route("/detalles-solicitud/", methods=['GET'])
@app.route("/detalles-solicitud/<int:idSolicitud>", methods=['GET'])
def detalleSolicitud(idSolicitud=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idSolicitud es None o no está presente en la URL
        if idSolicitud is None:
            return redirect(url_for('login_bp.inicio'))
        else:
            from controllers.funciones_solicitud import obtener_solicitante_por_id
            detalle_solicitud = obtener_solicitante_por_id(idSolicitud) or []
            return render_template(f'{PATH_URL}/detalles_solicitud.html', detalle_solicitud=detalle_solicitud)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/empleados', methods=['GET'])
def viewFormEmpleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_EMPLEADOS}/empleados.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

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
            return redirect(url_for('login_bp.inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/reportes/reporte-excel', methods=['GET'])
def viewFormReportesExcel():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REPORTE_EXCEL}/reporteExcel.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@app.route('/reportes/reporte-pdf', methods=['GET'])
def viewFormReportesPDF():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REPORTE_PDF}/reportePDF.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@app.route('/reportes/reporte-estadistico', methods=['GET'])
def viewFormReportesEstadisticos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REPORTE_ESTADISTICO}/reporteEstadistico.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))