from app import app

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from mysql.connector.errors import Error

# Importando conexión a BD y controladores
from controllers.funciones_home import *
from models.contratacion import ContratacionModel
from controllers.contratacion import contrataciones_bp
from controllers.UserController import user_bp
from controllers.funciones_solicitud import (
    obtener_solicitudes, crear_solicitud, obtener_solicitud_por_id,
    actualizar_solicitud, eliminar_solicitud
)
from controllers.funciones_bitacora import obtener_bitacora, filtrar_bitacora, obtener_estadisticas_bitacora
from services.bitacora_service import BitacoraService
from controllers.EmpleadoController import empleado_bp
from controllers.controller_reportesExcel import reporte_excel_bp
from controllers.controller_reportesPDF import reporte_pdf_bp
from controllers.funciones_publicaciones import *
from controllers.funciones_proyecto import *
from controllers.funciones_maquinaria import *
from models.model_empresa import EmpresaModel

## Gerencias
from controllers.gerenciasController import gerencia_bp
app.register_blueprint(gerencia_bp)

# Crear Blueprint para manejar las rutas de home con la carpeta de vistas correcta
home_bp = Blueprint('home_bp', __name__, template_folder='../vista')
contrataciones_bp = Blueprint('contrataciones_bp', __name__)
##app.register_blueprint(contrataciones_bp)

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
PATH_URL_REG_EMPLEADOS = "empleados"
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
        maquinarias = listar_maquinarias_controller()
        return render_template(f'{PATH_URL_PROY}/form_maquinaria.html', maquinarias=maquinarias)
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))    

@home_bp.route('/form-registrar-maquinaria', methods=['POST'])
def formRegistrarMaquinaria():
    if 'conectado' in session:
        if registrar_maquinaria_controller(request.form):
            flash('Maquinaria registrada con éxito.', 'success')
        else:
            flash('Error al intentar registrar la maquinaria. Verifique los datos.', 'error')
        return redirect(url_for('home_bp.viewFormMaquinaria'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))    

@home_bp.route('/editar-maquinaria/<int:id_maquinaria>', methods=['GET'])
def viewEditarMaquinaria(id_maquinaria):
    if 'conectado' in session:
        # Se asume que obtener_maquinaria_controller existe en funciones_maquinaria.py
        maquinaria = obtener_maquinaria_controller(id_maquinaria)
        if maquinaria:
            return render_template(f'{PATH_URL_PROY}/form_maquinaria-update.html', maquinaria=maquinaria)
        else:
            flash('La maquinaria no existe.', 'error')
            return redirect(url_for('home_bp.viewFormMaquinaria'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/actualizar-maquinaria', methods=['POST'])
def formActualizarMaquinaria():
    if 'conectado' in session:
        id_maquinaria = request.form.get('id_maquinaria')
        if actualizar_maquinaria_controller(id_maquinaria, request.form):
            flash('Maquinaria actualizada con éxito.', 'success')
        else:
            flash('Error al intentar actualizar la maquinaria.', 'error')
        return redirect(url_for('home_bp.viewFormMaquinaria'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/eliminar-maquinaria/<int:id_maquinaria>', methods=['GET'])
def eliminarMaquinaria(id_maquinaria):
    if 'conectado' in session:
        res = eliminar_maquinaria_controller(id_maquinaria)
        if res == "utilizada":
            flash('No se puede eliminar: Esta maquinaria está asignada a uno o más proyectos.', 'warning')
        elif res:
            flash('Maquinaria eliminada correctamente.', 'success')
        else:
            flash('Error al intentar eliminar la maquinaria.', 'error')
        return redirect(url_for('home_bp.viewFormMaquinaria'))
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
        proyectos = listar_proyectos_controller()
        maquinarias = listar_maquinarias_controller()
        return render_template(f'{PATH_URL_PROY}/proyectos.html', proyectos=proyectos, maquinarias=maquinarias)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/form-registrar-proyecto', methods=['POST'])
def formRegistrarProyecto():
    if 'conectado' in session:
        try:
            if registrar_proyecto_controller(request.form):
                flash('Proyecto registrado satisfactoriamente.', 'success')
            else:
                flash('Error al registrar el proyecto en la base de datos.', 'error')
        except Exception as e:
            print(f"Excepción en router: {e}")
            flash(f'Ocurrió un error inesperado: {e}', 'error')
        return redirect(url_for('home_bp.viewFormProyectos'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/editar-proyecto/<int:id_proyecto>', methods=['GET'])
def viewEditarProyecto(id_proyecto):
    if 'conectado' in session:
        from models.model_proyecto import ProyectoModel
        modelo = ProyectoModel()
        proyecto = modelo.obtener_proyecto_por_id(id_proyecto)
        maquinarias = listar_maquinarias_controller()
        if proyecto:
            return render_template(f'{PATH_URL_PROY}/form_proyecto_update.html', proyecto=proyecto, maquinarias=maquinarias)
        else:
            flash('El proyecto no existe.', 'error')
            return redirect(url_for('home_bp.viewFormProyectos'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/actualizar-proyecto', methods=['POST'])
def formActualizarProyecto():
    if 'conectado' in session:
        from models.model_proyecto import ProyectoModel
        id_proyecto = request.form.get('id_proyectos')
        modelo = ProyectoModel()
        if modelo.actualizar_proyecto(id_proyecto, request.form):
            flash('Proyecto actualizado satisfactoriamente.', 'success')
        else:
            flash('Error al actualizar el proyecto.', 'error')
        return redirect(url_for('home_bp.viewFormProyectos'))
    return redirect(url_for('login_bp.inicio'))

@home_bp.route('/eliminar-proyecto/<int:id_proyecto>', methods=['GET'])
def eliminarProyecto(id_proyecto):
    if 'conectado' in session:
        from models.model_proyecto import ProyectoModel
        modelo = ProyectoModel()
        if modelo.eliminar_proyecto(id_proyecto):
            flash('Proyecto eliminado correctamente.', 'success')
        else:
            flash('Error al intentar eliminar el proyecto.', 'error')
        return redirect(url_for('home_bp.viewFormProyectos'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/api/obtener-solicitudes-json', methods=['GET'])
def api_obtener_solicitudes_json():
    if 'conectado' in session:
        return jsonify(obtener_solicitudes() or [])
    else:
        return jsonify([]), 401


### Contratacion

@contrataciones_bp.route('/contrataciones', methods=['GET'])
def gestionar_contrataciones():
    if 'conectado' in session:
        # Importamos la maquinaria (ajusta esto si tu modelo está en otra parte)
        from models.model_maquinaria import MaquinariaModel
        
        lista_proyectos = ProyectoModel().obtener_proyectos()
        lista_maquinarias = MaquinariaModel().obtener_maquinarias()
        lista_empresas = EmpresaModel().obtener_empresas()
        lista_contrataciones = ContratacionModel().obtener_todas_las_contrataciones()
        
        # Enviamos a form_contratacion.html (Asegúrate de que la carpeta se llame 'contratacion')
        return render_template('contratacion/form_contratacion.html', 
                               contrataciones=lista_contrataciones,
                               proyectos=lista_proyectos,
                               maquinarias=lista_maquinarias,
                               empresas=lista_empresas)
    return redirect(url_for('login_bp.inicio'))
    
@contrataciones_bp.route('/registrar-contratacion', methods=['POST'])
def procesar_registro():
    if 'conectado' in session:
        modelo = ContratacionModel()
        
        if modelo.registrar_contrataciones(request.form):
            flash('Contratación registrada correctamente', 'success')
        else:
            flash('Error al guardar en la base de datos', 'error')
            
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
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
        flash('¡La gerencia ha sido registrada con éxito!', 'success')
        return redirect(url_for('lista_gerencias'))
    else:
        flash('Error: No se pudo registrar la gerencia.', 'error')
        return redirect(url_for('viewFormGerencia'))

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
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    # Obtener filtros opcionales
    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_modulo = request.args.get('modulo', '').strip()
    filtro_accion = request.args.get('accion', '').strip()

    registros = filtrar_bitacora(
        usuario=filtro_usuario or None,
        modulo=filtro_modulo or None,
        accion=filtro_accion or None
    )
    estadisticas = obtener_estadisticas_bitacora()

    return render_template(
        'bitacora/lista_bitacora.html',
        registros=registros,
        estadisticas=estadisticas,
        filtro_usuario=filtro_usuario,
        filtro_modulo=filtro_modulo,
        filtro_accion=filtro_accion
    )

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

    nuevo_id = False
    try:
        nuevo_id = crear_solicitud(request.form)
    except Exception as e:
        print(f"[Router] Error al crear solicitud: {e}")
        nuevo_id = False

    if nuevo_id:
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'CREAR',
            f'Solicitud #{nuevo_id} creada por {session.get("nombre", "")}'
        )
        flash('Solicitud registrada exitosamente.', 'success')
        return redirect(url_for('lista_solicitudes'))
    else:
        flash('La solicitud NO fue registrada. Verifique los datos ingresados.', 'error')
        return redirect(url_for('home_bp.viewFormSolicitud'))

@app.route('/lista-de-solicitudes', methods=['GET'])
def lista_solicitudes():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    solicitudes = obtener_solicitudes()
    estadisticas = {}
    try:
        from models.model_solicitudes import SolicitudModel
        estadisticas = SolicitudModel().obtener_estadisticas()
    except Exception:
        pass
    return render_template(f'{PATH_URL}/lista_solicitudes.html',
                           solicitudes=solicitudes, estadisticas=estadisticas)

@app.route('/eliminar-solicitud/<int:id_solicitud>', methods=['GET'])
def eliminar_solicitud_route(id_solicitud):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    if eliminar_solicitud(id_solicitud):
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'ELIMINAR',
            f'Solicitud #{id_solicitud} eliminada'
        )
        flash('Solicitud eliminada correctamente.', 'success')
    else:
        flash('Error al intentar eliminar la solicitud.', 'error')
    return redirect(url_for('lista_solicitudes'))

@app.route('/editar-solicitud/<int:id_solicitud>', methods=['GET'])
def viewEditarSolicitud(id_solicitud):
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))
    solicitud = obtener_solicitud_por_id(id_solicitud)
    if solicitud:
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'VER',
            f'Accedió a editar Solicitud #{id_solicitud}'
        )
        return render_template(f'{PATH_URL}/editar_solicitud.html', solicitud=solicitud)
    else:
        flash('La solicitud no existe.', 'error')
        return redirect(url_for('lista_solicitudes'))

@app.route('/update-solicitud', methods=['POST'])
def update_solicitud():
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))
    id_solicitud = request.form.get('id_solicitud')
    if actualizar_solicitud(id_solicitud, request.form):
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'EDITAR',
            f'Solicitud #{id_solicitud} actualizada'
        )
        flash('Solicitud actualizada correctamente.', 'success')
    else:
        flash('Error al actualizar la solicitud. Verifique los datos.', 'error')
    return redirect(url_for('lista_solicitudes'))

@app.route("/detalles-solicitud/", methods=['GET'])
@app.route("/detalles-solicitud/<int:idSolicitud>", methods=['GET'])
def detalleSolicitud(idSolicitud=None):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if idSolicitud is None:
        return redirect(url_for('lista_solicitudes'))
    detalle_solicitud = obtener_solicitud_por_id(idSolicitud)
    if detalle_solicitud:
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'VER',
            f'Detalles de Solicitud #{idSolicitud}'
        )
    return render_template(f'{PATH_URL}/detalles_solicitud.html',
                           detalle_solicitud=detalle_solicitud or {})

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
        resp_empleadosBD = sql_lista_empleadosBD()
        return render_template(f'{PATH_URL_LIST_EMPLEADOS}/empleados.html', resp_empleadosBD=resp_empleadosBD)
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
            return render_template(f'{PATH_URL_LIST_EMPLEADOS}/form_empleado_update.html', empleado=respuestaEmpleado)
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
app.register_blueprint(contrataciones_bp)