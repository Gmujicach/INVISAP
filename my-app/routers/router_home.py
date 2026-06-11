from app import app
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from mysql.connector.errors import Error

# Importando conexión a BD y controladores
from controllers.funciones_home import *
from controllers.UserController import user_bp 
from controllers.funciones_solicitud import *
from controllers.EmpleadoController import empleado_bp
from controllers.controller_reportesExcel import reporte_excel_bp
from controllers.controller_reportesPDF import reporte_pdf_bp

## Gerencias
from controllers.gerenciasController import gerencia_bp
app.register_blueprint(gerencia_bp)

# Crear Blueprint para manejar las rutas de home con la carpeta de vistas correcta
home_bp = Blueprint('home_bp', __name__, template_folder='../vista')

# Rutas de carpetas (Paths)
PATH_URL = "solicitudes"
PATH_URL_CONTRAT = "contratacion"
PATH_URLG = "gerencias"
PATH_URL_RES = "respaldo"
PATH_URL_INF = "inf_avance_obra"
PATH_URL_PROY = "proyectos"
PATH_URL_GEST_OBR = "obras"
PATH_URL_PUB = "publicaciones"
PATH_URL_IA = "ia"
PATH_URL_REG_EMPLEADOS = "registrar-empleado"
PATH_URL_LIST_EMPLEADOS = "empleados"
PATH_URL_REPORTE_EXCEL = "reportes"
PATH_URL_REPORTE_PDF = "reportes"
PATH_URL_REPORTE_ESTADISTICO = "reportes"

# Registrar blueprints
app.register_blueprint(user_bp)
app.register_blueprint(empleado_bp)
app.register_blueprint(reporte_excel_bp)
app.register_blueprint(reporte_pdf_bp)

@home_bp.route('/registrar-solicitud', methods=['GET'])
def viewFormSolicitud():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_solicitud.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/registrar-publicaciones', methods=['GET'])
def viewFormPublicaciones():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_PUB}/form_publicaciones.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/administrar-respaldos', methods=['GET'])
def viewFormRespaldos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_RES}/form_respaldo.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/registrar-maquinaria', methods=['GET'])
@home_bp.route('/maquinaria', methods=['GET'])
def viewFormMaquinaria():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_PROY}/form_maquinaria.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))    

@home_bp.route('/registrar-mortadela', methods=['GET'])
def viewFormMortadela():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_mortadela.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/gestionar-obras', methods=['GET'])
def viewFormGestionarObras():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_GEST_OBR}/form_gestionar_obras.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/gestionar-gravedad', methods=['GET'])
def viewFormGravedad():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_gestionar_gravedad.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@home_bp.route('/priorizar-solicitudes', methods=['GET'])
def viewPriorizarSolicitudes():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_priorizar_solicitudes.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/gestionar-prioridad', methods=['GET'])
def viewFormPrioridad():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_gestionar_prioridad.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/gestionar-proyectos', methods=['GET'])
def viewFormProyectos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_PROY}/proyectos.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/registrar-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_CONTRAT}/form_contratacion.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/inspectores', methods=['GET'])
def viewFormInspectores():
    if 'conectado' in session:
        return render_template('placeholder.html', title='Inspectores', message='Esta página está en desarrollo.', note='Contacto al administrador para habilitar esta función.')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

## Gerencias
@home_bp.route('/registrar-gerencias', methods=['GET'])
def viewFormGerencia():
    if 'conectado' in session:
        from models.model_gerencias import GerenciaModel
        modelo = GerenciaModel()
        informes = modelo.obtener_informes_disponibles()
        return render_template(f'{PATH_URLG}/form_gerencia.html', informes=informes)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/form-registrar-gerencias', methods=['POST'])
def procesar_registro():
    from controllers.gerenciasController import procesar_registro_gerencia
    if procesar_registro_gerencia(request.form):
        flash('Registro exitoso', 'success')
        return redirect(url_for('lista_gerencias'))
    return "Error al registrar"

@app.route('/lista-gerencias', methods=['GET'])
def lista_gerencias():
    if 'conectado' in session:
        from controllers.gerenciasController import obtener_todas_las_gerencias
        return render_template(f'{PATH_URLG}/lista_gerencias.html', gerencias=obtener_todas_las_gerencias())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/edi-gerencias/<int:id_gerencia>', methods=['GET'])
def viewEditarGerencia(id_gerencia):
    if 'conectado' in session:
        from controllers.gerenciasController import obtener_gerencia_por_id
        from models.model_gerencias import GerenciaModel
        
        gerencia = obtener_gerencia_por_id(id_gerencia)
        informes = GerenciaModel().obtener_informes_disponibles()
        
        if gerencia:
            return render_template(f'{PATH_URLG}/edi_gerencias.html', gerencia=gerencia, informes=informes)
        else:
            flash('La gerencia no existe.', 'error')
            return redirect(url_for('lista_gerencias'))
    return redirect(url_for('login_bp.inicio'))

@app.route('/update-gerencia', methods=['POST'])
def update_gerencia():
    from controllers.gerenciasController import update_gerencia
    if update_gerencia(request.form):
        flash('Actualizado correctamente', 'success')
    else:
        flash('Error al actualizar', 'error')
    return redirect(url_for('lista_gerencias'))

@app.route('/eliminar-gerencia/<int:id_gerencia>', methods=['GET'])
def eliminar_gerencia(id_gerencia):
    if 'conectado' in session:
        from controllers.gerenciasController import eliminar_gerencia_por_id
        if eliminar_gerencia_por_id(id_gerencia):
            flash('Gerencia eliminada correctamente.', 'success')
        else:
            flash('Error al intentar eliminar la gerencia.', 'error')
        return redirect(url_for('lista_gerencias'))
    else:
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/bitacora', methods=['GET'])
def viewBitacora():
    if 'conectado' in session:
        return render_template('placeholder.html', title='Bitacora', message='Esta página está en desarrollo.', note='Contacto al administrador para habilitar esta función.')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/inf_avance_obra', methods=['GET'])
def viewFormInforme_avan_obras():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_INF}/inf_avance_obra.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/form-registrar-solicitud', methods=['POST'])
def formSolicitud():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

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
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/eliminar-solicitud/<int:id_solicitud>', methods=['GET'])
def eliminar_solicitud(id_solicitud):
    if 'conectado' in session:
        from controllers.funciones_solicitud import eliminar_solicitud_por_id
        
        if eliminar_solicitud_por_id(id_solicitud):
            flash('Solicitud eliminada correctamente.', 'success')
        else:
            flash('Error al intentar eliminar la solicitud.', 'error')
            
        return redirect(url_for('lista_solicitudes'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/editar-solicitud/<int:id_solicitud>', methods=['GET'])
def viewEditarSolicitud(id_solicitud):
    if 'conectado' in session:
        from controllers.funciones_solicitud import obtener_solicitante_por_id
        
        solicitud = obtener_solicitante_por_id(id_solicitud)
        
        if solicitud:
            # CORRECCIÓN: Apunta correctamente al archivo editar_solicitud.html
            return render_template(f'{PATH_URL}/editar_solicitud.html', solicitud=solicitud)
        else:
            flash('La solicitud no existe.', 'error')
            return redirect(url_for('lista_solicitudes'))
    return redirect(url_for('login_bp.inicio'))

@app.route('/update-solicitud', methods=['POST'])
def update_solicitud():
    if 'conectado' in session:
        from controllers.funciones_solicitud import actualizar_datos_solicitud
        
        id_solicitud = request.form.get('id_solicitud')
        
        if actualizar_datos_solicitud(id_solicitud, request.form):
            flash('Solicitud actualizada correctamente.', 'success')
        else:
            flash('Error al actualizar la solicitud.', 'error')
            
        return redirect(url_for('lista_solicitudes'))
    return redirect(url_for('login_bp.inicio'))

@app.route("/detalles-solicitud/", methods=['GET'])
@app.route("/detalles-solicitud/<int:idSolicitud>", methods=['GET'])
def detalleSolicitud(idSolicitud=None):
    if 'conectado' in session:
        if idSolicitud is None:
            return redirect(url_for('login_bp.inicio'))
        else:
            from controllers.funciones_solicitud import obtener_solicitante_por_id
            detalle_solicitud = obtener_solicitante_por_id(idSolicitud) or []
            return render_template(f'{PATH_URL}/detalles_solicitud.html', detalle_solicitud=detalle_solicitud)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/registrar-empleado', methods=['GET'])
def viewFormRegistrarEmpleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REG_EMPLEADOS}/form_empleado.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@app.route('/empleados', methods=['GET'])
def viewFormListarEmpleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_LIST_EMPLEADOS}/empleados.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

# Buscador de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        # CORRECCIÓN: Se cambió de PATH_URL a PATH_URL_LIST_EMPLEADOS
        return render_template(f'{PATH_URL_LIST_EMPLEADOS}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})

@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuestaEmpleado = buscarEmpleadoUnico(id)
        if respuestaEmpleado:
            # CORRECCIÓN: Se cambió de PATH_URL a PATH_URL_LIST_EMPLEADOS
            return render_template(f'{PATH_URL_LIST_EMPLEADOS}/form_empleado_update.html', respuestaEmpleado=respuestaEmpleado)
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('login_bp.inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/reportes/reporte-excel', methods=['GET'])
def viewFormReportesExcel():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REPORTE_EXCEL}/reporteExcel.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@home_bp.route('/reportes/reporte-pdf', methods=['GET'])
def viewFormReportesPDF():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REPORTE_PDF}/reportePDF.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
@home_bp.route('/reportes/reporte-estadistico', methods=['GET'])
def viewFormReportesEstadisticos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_REPORTE_ESTADISTICO}/reporteEstadistico.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

# Registrar el blueprint en la aplicación
app.register_blueprint(home_bp)