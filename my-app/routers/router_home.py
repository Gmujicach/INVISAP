from app import app
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from mysql.connector.errors import Error

# Importando conexión a BD y controladores
from controllers.funciones_home import *
from models.model_contratacion import ContratacionModel
from controllers.controller_contratacion import contrataciones_bp
from controllers.UserController import user_bp
from controllers.funciones_solicitud import (
    obtener_solicitudes, crear_solicitud, obtener_solicitud_por_id,
    actualizar_solicitud, eliminar_solicitud
)
from controllers.funciones_bitacora import obtener_bitacora, filtrar_bitacora, obtener_estadisticas_bitacora
from models.model_publicacion import PublicacionModel
from services.bitacora_service import BitacoraService
from controllers.controller_empleado import empleado_bp
from controllers.controller_reportesExcel import reporte_excel_bp
from controllers.controller_reportesPDF import reporte_pdf_bp
from controllers.funciones_proyecto import *
from controllers.funciones_maquinaria import *
from models.model_empresas import EmpresaModel

## Empresas
from controllers.controller_empresa import empresa_bp
app.register_blueprint(empresa_bp)
empresa_bp = Blueprint('empresa_bp', __name__)

# Contrataciones
home_bp = Blueprint('home_bp', __name__, template_folder='../vista')
contrataciones_bp = Blueprint('contrataciones_bp', __name__)
##app.register_blueprint(contrataciones_bp)

# Rutas de carpetas (Paths)
PATH_URL = "solicitudes"
PATH_URL_CONTRAT = "contratacion"
PATH_URLE = "empresas"
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
        modelo = PublicacionModel()
        publicaciones = modelo.obtener_todas_las_publicaciones()
        informes = modelo.obtener_informes_para_publicaciones()
        return render_template(f'{PATH_URL_PUB}/form_publicaciones.html', 
                               publicaciones=publicaciones, 
                               informes=informes)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/api/publicaciones/crear', methods=['POST'])
def api_crear_publicacion():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401
    
    try:
        data = request.form
        modelo = PublicacionModel()
        # Soportar ambos nombres posibles del campo (id_informe o evidencias)
        id_inf = data.get('id_informe') or data.get('evidencias')
        
        # Validación de existencia en tiempo real (Backend)
        if not modelo.validar_informe_activo(id_inf):
            return jsonify({'status': 'error', 'message': 'El informe seleccionado no existe o fue eliminado.'}), 400

        # Aplicación de setters con validación Regex integrada
        modelo.titulo = data.get('titulo_publicacion')
        modelo.responsable = data.get('nombre_responsable') or data.get('autor_publicacion')
        modelo.tipo = data.get('tipo_publicacion')
        modelo.id_informe = id_inf
        
        if modelo.guardar():
            return jsonify({'status': 'success', 'message': 'Publicación registrada correctamente'})
        return jsonify({'status': 'error', 'message': 'Error al guardar en BD'}), 500
        
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500

@home_bp.route('/api/publicaciones/validar-informe/<int:id_informe>', methods=['GET'])
def validar_informe(id_informe):
    modelo = PublicacionModel()
    existe = modelo.validar_informe_activo(id_informe)
    return jsonify({'existe': existe})

@home_bp.route('/api/publicaciones/eliminar/<int:id_pub>', methods=['DELETE'])
def api_eliminar_publicacion(id_pub):
    if 'conectado' in session:
        modelo = PublicacionModel(id_publicacion=id_pub)
        if modelo.eliminar():
            return jsonify({'status': 'success', 'message': 'Registro desactivado correctamente'})
        return jsonify({'status': 'error', 'message': 'No se pudo eliminar'}), 500
    return jsonify({'status': 'error', 'message': 'No autorizado'}), 403

@home_bp.route('/form-registrar-publicacion', methods=['POST'])
def formRegistrarPublicacion():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        data = request.form
        modelo = PublicacionModel()
        # Soportar ambos nombres posibles del campo (id_informe o evidencias)
        id_inf = data.get('id_informe') or data.get('evidencias')
        
        # Validación de existencia en tiempo real (Backend)
        if not modelo.validar_informe_activo(id_inf):
            flash('El informe seleccionado no existe o fue eliminado.', 'error')
            return redirect(url_for('home_bp.viewFormPublicaciones'))

        # Aplicación de setters con validación Regex integrada
        modelo.titulo = data.get('titulo_publicacion')
        modelo.responsable = data.get('nombre_responsable') or data.get('autor_publicacion')
        modelo.tipo = data.get('tipo_publicacion')
        modelo.id_informe = id_inf
        
        if modelo.guardar():
            flash('Publicación registrada correctamente', 'success')
        else:
            flash('Error al guardar la publicación en la base de datos.', 'error')
    except ValueError as ve:
        flash(f'Error de validación: {str(ve)}', 'error')
    except Exception as e:
        print(f"Error al registrar publicación: {e}")
        flash('Error interno del servidor al registrar la publicación.', 'error')
        
    return redirect(url_for('home_bp.viewFormPublicaciones'))

@home_bp.route('/editar-publicacion/<int:id_publicacion>', methods=['GET'])
def viewEditarPublicacion(id_publicacion):
    if 'conectado' in session:
        modelo = PublicacionModel()
        publicacion = modelo.obtener_publicacion_por_id(id_publicacion)
        informes = modelo.obtener_informes_para_publicaciones()
        if publicacion:
            return render_template(f'{PATH_URL_PUB}/form_publicaciones_update.html', publicacion=publicacion, informes=informes)
        flash('La publicación no existe.', 'error')
        return redirect(url_for('home_bp.viewFormPublicaciones'))
    return redirect(url_for('login_bp.inicio'))

@home_bp.route('/actualizar-publicacion', methods=['POST'])
def formActualizarPublicacion():
    if 'conectado' in session:
        try:
            data = request.form
            modelo = PublicacionModel(id_publicacion=data.get('id_publicaciones'))
            modelo.titulo = data.get('titulo_publicacion')
            modelo.responsable = data.get('nombre_responsable') or data.get('autor_publicacion')
            modelo.tipo = data.get('tipo_publicacion', 'Noticia')
            modelo.id_informe = data.get('id_informe') or data.get('evidencias')
            
            if modelo.actualizar():
                flash('Publicación actualizada correctamente', 'success')
            else:
                flash('Error al actualizar', 'error')
        except ValueError as ve:
            flash(str(ve), 'error')
        return redirect(url_for('home_bp.viewFormPublicaciones'))
    return redirect(url_for('login_bp.inicio'))

@home_bp.route('/eliminar-publicacion/<int:id_publicacion>', methods=['GET'])
def eliminarPublicacion(id_publicacion):
    """Maneja la eliminación lógica desde enlaces GET."""
    if 'conectado' in session:
        modelo = PublicacionModel(id_publicacion=id_publicacion)
        if modelo.eliminar():
            flash('Publicación eliminada (Desactivada) correctamente.', 'success')
        else:
            flash('No se pudo eliminar la publicación.', 'error')
        return redirect(url_for('home_bp.viewFormPublicaciones'))
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
        return jsonify(obtener_solicitudes())
    else:
        return jsonify([]), 401


### Contratacion

@contrataciones_bp.route('/contrataciones', methods=['GET'])
def gestionar_contrataciones():
    if 'conectado' in session:
        modelo = ContratacionModel()
        lista = modelo.obtener_todas_las_contrataciones()
        
        return render_template('contratacion/form_contratacion.html', contrataciones=lista)
        
    return redirect(url_for('login_bp.inicio'))

@contrataciones_bp.route('/api/obtener-empresas-json', methods=['GET'])
def obtener_empresas_json():
    if 'conectado' in session:
        modelo = ContratacionModel()
        empresas = modelo.obtener_empresas()
        return jsonify(empresas)
    return jsonify([]), 401

@contrataciones_bp.route('/registrar-contratacion', methods=['POST'])
def procesar_registro():
    if 'conectado' in session:
        modelo = ContratacionModel()
        if modelo.registrar_contrataciones(request.form):
            flash('Contratacion Registrada correctamente', 'success')
        else:
            flash('Error al guardar', 'error')
            

        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
        
    return redirect(url_for('login_bp.inicio'))


@contrataciones_bp.route('/editar-contratacion/<int:id>', methods=['GET'])
def vista_editar(id):
    if 'conectado' in session:
        modelo = ContratacionModel()
        contratacion_data = modelo.obtener_contratacion_por_id(id)
        
        if contratacion_data:
            
            campos_fecha = ['fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro']
            
            for campo in campos_fecha:
                if contratacion_data.get(campo):
                    if hasattr(contratacion_data[campo], 'strftime'):
                        contratacion_data[campo] = contratacion_data[campo].strftime('%Y-%m-%d')
                    else:
                        contratacion_data[campo] = str(contratacion_data[campo])[:10]
            
            return render_template('contratacion/form_contratacionM.html', contratacion=contratacion_data)
        
        flash('Contratación no encontrada', 'error')
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
    return redirect(url_for('login_bp.inicio'))


@contrataciones_bp.route('/actualizar-contratacion', methods=['POST'])
def procesar_actualizacion():
    if 'conectado' in session:
        modelo = ContratacionModel()
        if modelo.actualizar_contratacion(request.form):
            flash('Contratación modificada correctamente', 'success')
        else:
            flash('Error al intentar actualizar el registro', 'error')
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
    return redirect(url_for('login_bp.inicio'))

@contrataciones_bp.route('/eliminar-contratacion/<int:id>', methods=['GET'])
def eliminar_contratacion(id):
    if 'conectado' in session:
        modelo = ContratacionModel()
        
        if modelo.eliminar_contratacion(id):
            flash('Contratación eliminada correctamente', 'success')
        else:
            flash('No se pudo eliminar la contratación o está vinculada a otro registro', 'error')
            
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
        
    return redirect(url_for('login_bp.inicio'))

@home_bp.route('/inspectores', methods=['GET'])
def viewFormInspectores():
    if 'conectado' in session:
        return render_template('placeholder.html', title='Inspectores', message='Esta página está en desarrollo.', note='Contacto al administrador para habilitar esta función.')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

## Empresas
@home_bp.route('/registrar-empresas', methods=['GET'])
def viewFormEmpresa():
    if 'conectado' in session:
        # Sacamos los datos de la sesión (si los hay)
        datos_formulario = session.pop('form_empresa', None)
        
        from models.model_empresas import EmpresaModel
        modelo = EmpresaModel()
        
        # AQUÍ ESTÁ EL CAMBIO: Le pasamos la variable al HTML
        return render_template(f'{PATH_URLE}/form_empresa.html', datos_form=datos_formulario)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/form-registrar-empresas', methods=['POST'])
def procesar_registro():
    from controllers.controller_empresa import procesar_registro_empresa
    
    exito, mensaje, categoria = procesar_registro_empresa(request.form)
    flash(mensaje, categoria)
    
    if exito:
        # Si todo salió bien, nos aseguramos de limpiar la sesión por si acaso
        session.pop('form_empresa', None)
        return redirect(url_for('lista_empresas'))
    else:
        # 1. Convertimos los datos enviados en un diccionario normal de Python
        datos_viejos = request.form.to_dict()
        
        # 2. OPCIÓN: Borrar el RIF y mantener el resto (como solicitaste)
        # Si prefieres mantener el RIF también, simplemente comenta o borra la siguiente línea:
        datos_viejos['rif'] = '' 
        
        # 3. Guardamos el resto de los datos en la sesión y redirigimos
        session['form_empresa'] = datos_viejos
        return redirect(url_for('home_bp.viewFormEmpresa'))

@app.route('/lista-empresas', methods=['GET'])
def lista_empresas():
    if 'conectado' in session:
        from controllers.controller_empresa import obtener_todas_las_empresas
        return render_template(f'{PATH_URLE}/lista_empresas.html', empresas=obtener_todas_las_empresas())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/edi-empresas/<string:rif>', methods=['GET'])
def viewEditarEmpresa(rif):
    if 'conectado' in session:
        from controllers.controller_empresa import obtener_empresa_por_rif
        from models.model_empresas import EmpresaModel
        
        empresa = obtener_empresa_por_rif(rif)
        
        if empresa:
            return render_template(f'{PATH_URLE}/edi_empresas.html', empresa=empresa)
        else:
            flash('La empresa no existe.', 'error')
            return redirect(url_for('lista_empresas'))
    return redirect(url_for('login_bp.inicio'))

@app.route('/update-empresa', methods=['POST'])
def update_empresa():
    from controllers.controller_empresa import update_empresa
    if update_empresa(request.form):
        flash('Actualizado correctamente', 'success')
    else:
        flash('Error al actualizar', 'error')
    return redirect(url_for('lista_empresas'))

@app.route('/eliminar-empresa/<string:rif>', methods=['GET'])
def eliminar_empresa(rif):
    if 'conectado' in session:
        from controllers.controller_empresa import eliminar_empresa_por_rif
        if eliminar_empresa_por_rif(rif):
            flash('Empresa eliminada correctamente.', 'success')
        else:
            flash('Error al intentar eliminar la empresa.', 'error')
        return redirect(url_for('lista_empresas'))
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