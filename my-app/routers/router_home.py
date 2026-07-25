from app import app
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, Response
from mysql.connector.errors import Error
from flask import jsonify
from conexion.conexionBD import connectionBD


# Importando conexión a BD y controladores
from controllers.funciones_home import *
from controllers.controller_informe_avance import informe_avance_bp
from models.model_contratacion import ContratacionModel
from controllers.controller_contratacion import contrataciones_bp
from controllers.UserController import user_bp
from controllers.funciones_solicitud import (
    obtener_solicitudes, crear_solicitud, obtener_solicitud_por_id,
    actualizar_solicitud, eliminar_solicitud, obtener_solicitudes_pendientes
)
from controllers.funciones_maquinaria import (
    registrar_maquinaria_controller, listar_maquinarias_controller, 
    obtener_maquinaria_controller, listar_maquinarias_eliminadas_controller,
    restaurar_maquinaria_controller, actualizar_maquinaria_controller,
    eliminar_maquinaria_controller, contar_maquinarias_controller
)
from controllers.funciones_bitacora import filtrar_bitacora, obtener_estadisticas_bitacora, contar_bitacora_filtrada
from models.model_publicacion import PublicacionModel
from models.model_informe_avance import InformeAvanceModel
from models.model_solicitudes import SolicitudModel
from models.model_prioridad import PrioridadModel
from services.bitacora_service import BitacoraService
from controllers.controller_empleado import empleado_bp
from controllers.controller_evidencia import evidencia_bp
from controllers.controller_reportesExcel import reporte_excel_bp
from controllers.controller_reportesPDF import reporte_pdf_bp
from controllers.controller_reportesEstadistico import reporte_estadistico_bp
from controllers.funciones_proyecto import *
from controllers.funciones_maquinaria import *
from controllers.controller_obra import obra_bp
from models.model_empresas import EmpresaModel

## Informe de Avance de Obra
from controllers.controller_informe_avance import informe_avance_bp

## Empresas
from controllers.controller_empresa import empresa_bp
from controllers.controller_inspeccion import inspeccion_bp
from controllers.controller_gravedad import (
    registrar_gravedad_controller, listar_gravedades_controller,
    obtener_gravedad_controller, actualizar_gravedad_controller,
    eliminar_gravedad_controller
)
## Seguridad: Roles y Permisos (módulos, roles, roles_permisos)
from controllers.controller_seguridad import (
    registrar_modulo_controller, listar_modulos_controller, obtener_modulo_controller,
    actualizar_modulo_controller, eliminar_modulo_controller,
    registrar_rol_controller, listar_roles_controller, obtener_rol_controller,
    actualizar_rol_controller, eliminar_rol_controller,
    obtener_permisos_rol_controller, guardar_permisos_controller
)
from controllers.UserController import verificar_permiso
app.register_blueprint(empresa_bp)
app.register_blueprint(inspeccion_bp)
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
PATH_URL_SEG = "seguridad"
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
app.register_blueprint(reporte_estadistico_bp)
app.register_blueprint(evidencia_bp)
app.register_blueprint(informe_avance_bp)
app.register_blueprint(obra_bp)

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
        id_inf = data.get('informe_avance_obra_id_informe') or data.get('id_informe') or data.get('evidencias')
        
        if not id_inf:
            return jsonify({'status': 'error', 'message': 'Debe seleccionar un informe válido.'}), 400

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
    # Importamos datetime aquí para asegurar que funcione sin modificar la cabecera del archivo
    from datetime import datetime 

    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        data = request.form
        modelo = PublicacionModel()
        
        id_inf = data.get('informe_avance_obra_id_informe') or data.get('id_informe') or data.get('evidencias')
        
        if not id_inf:
            flash('Debe seleccionar un Informe de Avance de Obra válido.', 'warning')
            return redirect(url_for('home_bp.viewFormPublicaciones'))

        # Validación 2: Verificar que el informe existe en la BD
        if not modelo.validar_informe_activo(id_inf):
            flash('El informe seleccionado no existe o fue eliminado.', 'error')
            return redirect(url_for('home_bp.viewFormPublicaciones'))

        # Armamos el diccionario con las llaves que espera nuestro modelo SQL corregido
        datos_insertar = {
            'titulo_publicacion': data.get('titulo_publicacion'),
            'nombre_responsable': data.get('nombre_responsable') or data.get('autor_publicacion'),
            'tipo_publicacion': data.get('tipo_publicacion', 'General'),
            'fecha_publicacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'informe_avance_obra_id_informe': id_inf,
            'cuerpo_publicacion': data.get('cuerpo_publicacion', 'Contenido pendiente')
        }
        
        # Llamamos a la BD
        resultado = modelo.registrar_publicacion(datos_insertar)
        
        if resultado:
            flash('Publicación registrada correctamente', 'success')
        else:
            flash('Error al guardar la publicación. Revisa la consola para más detalles.', 'error')
            
    except Exception as e:
        # Imprimimos en consola para ti como desarrollador
        print(f"Error CRÍTICO al registrar publicación: {e}")
        # Mostramos el error real en la pantalla para no tener que adivinar
        flash(f'Error del sistema: {str(e)}', 'error')
        
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
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))

    try:
        data = request.form
        id_pub = data.get('id_publicacion')

        if not id_pub:
            flash('Error: No se pudo identificar la publicación a actualizar.', 'error')
            return redirect(url_for('home_bp.viewFormPublicaciones'))

        modelo = PublicacionModel()

        if modelo.actualizar_publicacion(id_pub, data):
            flash('Publicación actualizada correctamente', 'success')
        else:
            flash('No se realizaron cambios o hubo un error en la base de datos.', 'warning')

    except Exception as e:
        print(f"Error técnico en actualización: {e}")
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('home_bp.viewFormPublicaciones'))
    
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

@home_bp.route('/lista-publicaciones', methods=['GET'])
def lista_publicaciones():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    # Instanciamos el modelo para obtener los datos
    modelo = PublicacionModel()
    publicaciones = modelo.obtener_todas_las_publicaciones()
    
    # Calculamos las estadísticas leyendo los resultados
    activas = 0
    inactivas = 0
    
    for p in publicaciones:
        # El estado 1 representa Activo en la BD
        if p.get('estado') == 1 or str(p.get('estado')).lower() == 'activo':
            activas += 1
        else:
            inactivas += 1
            
    estadisticas = {
        'Activas': activas,
        'Inactivas': inactivas
    }
    
    return render_template(f'{PATH_URL_PUB}/lista_publicaciones.html', 
                           publicaciones=publicaciones, 
                           estadisticas=estadisticas)

@home_bp.route('/detalles-publicacion/', methods=['GET'])
@home_bp.route('/detalles-publicacion/<int:id_publicacion>', methods=['GET'])
def viewDetallesPublicacion(id_publicacion=None):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    if id_publicacion is None:
        return redirect(url_for('home_bp.lista_publicaciones'))
    
    modelo = PublicacionModel()
    detalle_publicacion = modelo.obtener_publicacion_por_id(id_publicacion)
    
    informe_evidencias = []
    if detalle_publicacion and detalle_publicacion.get('id_informe'):
        try:
            informe_modelo = InformeAvanceModel()
            informe = informe_modelo.obtener_informe_por_id(detalle_publicacion['id_informe'])
            if informe:
                informe_evidencias = informe.get('evidencias', [])
        except Exception as e:
            print(f"Error al cargar evidencias del informe: {e}")
    
    if detalle_publicacion:
        BitacoraService.registrar_accion(
            session, 'Publicaciones', 'VER',
            f'Detalles de Publicación #{id_publicacion}'
        )
    
    return render_template(f'{PATH_URL_PUB}/detalles_publicacion.html',
                           detalle_publicacion=detalle_publicacion or {},
                           informe_evidencias=informe_evidencias)

@home_bp.route('/administrar-respaldos', methods=['GET'])
def viewFormRespaldos():
    return redirect(url_for('respaldo_bp.listar_respaldos_view'))

@home_bp.route('/registrar-maquinaria', methods=['GET'])
@home_bp.route('/api/maquinaria/listar', methods=['GET'])
def api_listar_maquinarias():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        maquinarias = listar_maquinarias_controller(page, per_page)
        total = contar_maquinarias_controller()
        total_pages = (total + per_page - 1) // per_page
        return jsonify({'success': True, 'data': maquinarias, 'total': total, 'page': page, 'total_pages': total_pages})
    except Exception as e:
        print(f"Error en api_listar_maquinarias: {e}")
        return jsonify({'success': False, 'message': 'Error al listar maquinarias'})

@home_bp.route('/maquinaria', methods=['GET'])
def viewFormMaquinaria():
    if 'conectado' in session:
        maquinarias = listar_maquinarias_controller(1, 1000)
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

@home_bp.route('/api/maquinaria/crear', methods=['POST'])
def api_crear_maquinaria():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401

    try:
        resultado = registrar_maquinaria_controller(request.form)
        if resultado.get('success'):
            return jsonify({'success': True, 'message': resultado.get('message', 'Maquinaria registrada correctamente'), 'id': resultado.get('id')})
        return jsonify({'success': False, 'message': resultado.get('message', 'No se pudo registrar')})
    except Exception as e:
        print(f"Error en api_crear_maquinaria: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'})

@home_bp.route('/api/maquinaria/<int:id_maquinaria>/eliminar', methods=['DELETE'])
def api_eliminar_maquinaria(id_maquinaria):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401

    res = eliminar_maquinaria_controller(id_maquinaria)
    if res == "utilizada":
        return jsonify({'success': False, 'message': 'No se puede eliminar: Esta maquinaria está asignada a uno o más proyectos.'}), 400
    elif res == "eliminada":
        return jsonify({'success': True, 'message': 'Maquinaria eliminada correctamente'}), 200
    return jsonify({'success': False, 'message': 'Error al eliminar la maquinaria'}), 400

@home_bp.route('/api/maquinaria/eliminadas', methods=['GET'])
def api_maquinarias_eliminadas():
    if 'conectado' not in session:
        return jsonify([]), 401
    
    try:
        resultado = listar_maquinarias_eliminadas_controller()
        return jsonify(resultado)
    except Exception as e:
        print(f"Error en api_maquinarias_eliminadas: {e}")
        return jsonify([])

@home_bp.route('/api/maquinaria/<int:id_maquinaria>/restaurar', methods=['POST'])
def api_restaurar_maquinaria(id_maquinaria):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401

    resultado = restaurar_maquinaria_controller(id_maquinaria)
    if resultado.get('success'):
        return jsonify({'success': True, 'message': resultado.get('message')}), 200
    return jsonify({'success': False, 'message': resultado.get('message', 'Error al restaurar')}), 400

@home_bp.route('/gestionar-gravedad', methods=['GET'])
def viewFormGravedad():
        return render_template(f'{PATH_URL_IA}/form_gestionar_gravedad.html')


# ===================== API MÓDULO GRAVEDAD (Catálogo) =====================
@home_bp.route('/api/gravedad/registrar', methods=['POST'])
def api_registrar_gravedad():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(registrar_gravedad_controller(data)), 200


@home_bp.route('/api/gravedad/listar', methods=['GET'])
def api_listar_gravedades():
    if 'conectado' not in session:
        return jsonify([]), 401
    return jsonify(listar_gravedades_controller())


@home_bp.route('/api/gravedad/obtener/<int:id_gravedad>', methods=['GET'])
def api_obtener_gravedad(id_gravedad):
    if 'conectado' not in session:
        return jsonify(None), 401
    return jsonify(obtener_gravedad_controller(id_gravedad) or None)


@home_bp.route('/api/gravedad/actualizar/<int:id_gravedad>', methods=['PUT', 'POST'])
def api_actualizar_gravedad(id_gravedad):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(actualizar_gravedad_controller(id_gravedad, data)), 200


@home_bp.route('/api/gravedad/eliminar/<int:id_gravedad>', methods=['DELETE', 'POST'])
def api_eliminar_gravedad(id_gravedad):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    return jsonify(eliminar_gravedad_controller(id_gravedad)), 200


@home_bp.route('/api/gravedad/validar-nivel', methods=['GET'])
def api_validar_nivel_gravedad():
    if 'conectado' not in session:
        return jsonify({'existe': False, 'error': 'Sesión no válida'}), 401
    nivel = request.args.get('nivel', '').strip()
    excluir = request.args.get('excluir', '').strip()
    from models.model_gravedad import GravedadObraModel
    existe = GravedadObraModel(nivel_gravedad=nivel).validar_nivel_existente(excluir)
    return jsonify({'existe': bool(existe)})

# ===================== MÓDULO PERMISOS POR ROL (Seguridad) =====================
@home_bp.route('/gestionar-permisos', methods=['GET'])
def viewFormPermisos():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('roles_permisos'):
        flash('No tienes permiso para gestionar roles y permisos.', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template(f'{PATH_URL_SEG}/form_gestionar_permisos.html')


# ---- API Módulos ----
@home_bp.route('/api/seguridad/modulos/listar', methods=['GET'])
def api_listar_modulos():
    if 'conectado' not in session:
        return jsonify([]), 401
    return jsonify(listar_modulos_controller())


@home_bp.route('/api/seguridad/modulos/registrar', methods=['POST'])
def api_registrar_modulo():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(registrar_modulo_controller(data)), 200


@home_bp.route('/api/seguridad/modulos/obtener/<int:id_modulo>', methods=['GET'])
def api_obtener_modulo(id_modulo):
    if 'conectado' not in session:
        return jsonify(None), 401
    return jsonify(obtener_modulo_controller(id_modulo) or None)


@home_bp.route('/api/seguridad/modulos/actualizar/<int:id_modulo>', methods=['PUT', 'POST'])
def api_actualizar_modulo(id_modulo):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(actualizar_modulo_controller(id_modulo, data)), 200


@home_bp.route('/api/seguridad/modulos/eliminar/<int:id_modulo>', methods=['DELETE', 'POST'])
def api_eliminar_modulo(id_modulo):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    return jsonify(eliminar_modulo_controller(id_modulo)), 200


# ---- API Roles ----
@home_bp.route('/api/seguridad/roles/listar', methods=['GET'])
def api_listar_roles():
    if 'conectado' not in session:
        return jsonify([]), 401
    return jsonify(listar_roles_controller())


@home_bp.route('/api/seguridad/roles/registrar', methods=['POST'])
def api_registrar_rol():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(registrar_rol_controller(data)), 200


@home_bp.route('/api/seguridad/roles/obtener/<int:id_rol>', methods=['GET'])
def api_obtener_rol(id_rol):
    if 'conectado' not in session:
        return jsonify(None), 401
    return jsonify(obtener_rol_controller(id_rol) or None)


@home_bp.route('/api/seguridad/roles/actualizar/<int:id_rol>', methods=['PUT', 'POST'])
def api_actualizar_rol(id_rol):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(actualizar_rol_controller(id_rol, data)), 200


@home_bp.route('/api/seguridad/roles/eliminar/<int:id_rol>', methods=['DELETE', 'POST'])
def api_eliminar_rol(id_rol):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    return jsonify(eliminar_rol_controller(id_rol)), 200


# ---- API Permisos por Rol ----
@home_bp.route('/api/seguridad/permisos/obtener/<int:id_rol>', methods=['GET'])
def api_obtener_permisos_rol(id_rol):
    if 'conectado' not in session:
        return jsonify([]), 401
    return jsonify(obtener_permisos_rol_controller(id_rol))


@home_bp.route('/api/seguridad/permisos/guardar', methods=['POST'])
def api_guardar_permisos_rol():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    id_rol = data.get('id_rol')
    permisos = data.get('permisos') or []
    # Si llega como form o JSON anidado, normalizar
    if isinstance(permisos, str):
        import json as _json
        try:
            permisos = _json.loads(permisos)
        except Exception:
            permisos = []
    return jsonify(guardar_permisos_controller(id_rol, permisos)), 200


@home_bp.route('/gestionar-prioridad', methods=['GET'])
def viewFormPrioridad():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_IA}/form_gestionar_prioridad.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


# ===================== API MÓDULO PRIORIDAD (IA + Paginación) =====================
@home_bp.route('/api/prioridad/listar', methods=['GET'])
def api_listar_prioridad():
    if 'conectado' not in session:
        return jsonify({'data': [], 'total': 0, 'page': 1, 'per_page': 10}), 401
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        page, per_page = 1, 10
    filas, total = PrioridadModel.listar_priorizadas(page=page, per_page=per_page)
    return jsonify({'data': filas, 'total': total, 'page': page, 'per_page': per_page})


@home_bp.route('/api/prioridad/obtener/<int:id_prioridad>', methods=['GET'])
def api_obtener_prioridad(id_prioridad):
    if 'conectado' not in session:
        return jsonify(None), 401
    return jsonify(PrioridadModel.obtener_por_id(id_prioridad) or None)


@home_bp.route('/api/prioridad/actualizar/<int:id_prioridad>', methods=['PUT', 'POST'])
def api_actualizar_prioridad(id_prioridad):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    data = request.get_json(silent=True) or request.form.to_dict()
    try:
        modelo = PrioridadModel(
            id_prioridad=id_prioridad,
            rango_prioridad=data.get('rango_prioridad'),
            justificacion=data.get('justificacion'),
            estado=int(data.get('estado', 1))
        )
        if modelo.actualizar():
            BitacoraService.registrar_accion(
                session, 'Prioridad', 'EDITAR',
                f'Ajustó prioridad ID: {id_prioridad} a {modelo.get_rango()}'
            )
            return jsonify({'success': True, 'message': 'Prioridad actualizada.'})
        return jsonify({'success': False, 'message': 'No se realizaron cambios.'})
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)})


@home_bp.route('/api/prioridad/eliminar/<int:id_prioridad>', methods=['DELETE', 'POST'])
def api_eliminar_prioridad(id_prioridad):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    modelo = PrioridadModel(id_prioridad=id_prioridad)
    if modelo.eliminar_logico():
        BitacoraService.registrar_accion(
            session, 'Prioridad', 'ELIMINAR',
            f'Desactivó prioridad ID: {id_prioridad}'
        )
        return jsonify({'success': True, 'message': 'Prioridad desactivada.'})
    return jsonify({'success': False, 'message': 'Error al desactivar.'})


@home_bp.route('/api/prioridad/clasificar-ia/<int:id_solicitud>', methods=['POST'])
def api_clasificar_ia(id_solicitud):
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
    datos = PrioridadModel.obtener_datos_solicitud(id_solicitud)
    if not datos:
        return jsonify({'success': False, 'message': 'Solicitud no encontrada.'})
    responsable = session.get('name_surname', 'IA')
    resultado = PrioridadModel.clasificar_solicitud_con_ia(
        id_solicitud,
        datos.get('descripcion') or '',
        datos.get('nivel_gravedad'),
        datos.get('color_semaforo'),
        responsable
    )
    BitacoraService.registrar_accion(
        session, 'Prioridad', 'EDITAR',
        f'IA clasificó la solicitud ID {id_solicitud} con prioridad {resultado.get("rango")}'
    )
    return jsonify({'success': True, 'message': 'Solicitud clasificada por la IA.', 'data': resultado})


@home_bp.route('/api/prioridad/solicitudes-ids', methods=['GET'])
def api_solicitudes_ids():
    if 'conectado' not in session:
        return jsonify([]), 401
    conexion = connectionBD()
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_solicitudes FROM solicitudes WHERE estado = 1")
        ids = [f[0] for f in cursor.fetchall()]
        return jsonify(ids)
    finally:
        cursor.close()
        conexion.close()


@home_bp.route('/gestionar-proyectos', methods=['GET'])
def viewFormProyectos():
    if 'conectado' in session:
       
        proyectos, contadores = listar_proyectos_controller(session)
        
        
        maquinarias = listar_maquinarias_controller()
        solicitudes = obtener_solicitudes()  
        
        
        return render_template(
            f'{PATH_URL_PROY}/proyectos.html', 
            proyectos=proyectos, 
            maquinarias=maquinarias, 
            solicitudes=solicitudes,
            contadores=contadores
        )
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@home_bp.route('/form-registrar-proyecto', methods=['POST'])
def formRegistrarProyecto():
    if 'conectado' not in session:
        return jsonify({'success': False, 'message': 'Sesión no iniciada'}), 401
    
    resultado = registrar_proyecto_controller(request.form, session)
    
    if resultado.get('success'):
        modelo = ProyectoModel()
        nuevo_proyecto = modelo.obtener_proyecto_por_id(request.form.get('Codigo_p'))
        
        return jsonify({
            'success': True, 
            'message': resultado.get('message', 'Proyecto registrado correctamente'),
            'data': nuevo_proyecto 
        })
    else:
        return jsonify({'success': False, 'message': resultado.get('message', 'Error al procesar el registro')})

@home_bp.route('/api/proyecto/validar-codigo/<string:codigo>', methods=['GET'])
def api_validar_codigo_proyecto(codigo):
    if 'conectado' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    modelo = ProyectoModel()
    resultado = modelo.validar_codigo_proyecto(codigo)
    return jsonify(resultado)

@home_bp.route('/editar-proyecto/<string:codigo_proyecto>', methods=['GET'])
def viewEditarProyecto(codigo_proyecto):
    if 'conectado' in session:
        from models.model_proyecto import ProyectoModel
        modelo = ProyectoModel()
        proyecto = modelo.obtener_proyecto_por_id(codigo_proyecto)
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
        
        from controllers.funciones_proyecto import actualizar_proyecto_controller
        
        codigo_proyecto_actual = request.form.get('codigo_proyecto_actual')

        if actualizar_proyecto_controller(codigo_proyecto_actual, request.form, session):
            flash('Proyecto actualizado satisfactoriamente.', 'success')
        else:
            flash('Error al actualizar el proyecto.', 'error')
            
        return redirect(url_for('home_bp.viewFormProyectos'))
    return redirect(url_for('login_bp.inicio'))
@home_bp.route('/eliminar-proyecto/<string:codigo_proyecto>', methods=['GET'])
def eliminarProyecto(codigo_proyecto):
    if 'conectado' in session:
        
        from controllers.funciones_proyecto import eliminar_proyecto_controller
        
        
        if eliminar_proyecto_controller(codigo_proyecto, session):
            flash('Proyecto eliminado correctamente.', 'success')
        else:
            flash('Error al intentar eliminar el proyecto.', 'error')
            
        return redirect(url_for('home_bp.viewFormProyectos'))
    return redirect(url_for('login_bp.inicio'))
@home_bp.route('/api/obtener-solicitudes-json', methods=['GET'])
def api_obtener_solicitudes_json():
    if 'conectado' in session:
        return jsonify(obtener_solicitudes())
    else:
        return jsonify([]), 401

@home_bp.route('/api/obtener-solicitudes-pendientes-json', methods=['GET'])
def api_obtener_solicitudes_pendientes_json():
    if 'conectado' in session:
        return jsonify(obtener_solicitudes_pendientes())
    else:
        return jsonify([]), 401

@home_bp.route('/api/obtener-bitacora-json', methods=['GET'])
def api_obtener_bitacora_json():
    if 'conectado' in session:
        from controllers.funciones_bitacora import filtrar_bitacora
        from flask import request
        usuario = request.args.get('usuario', '').strip() or None
        modulo = request.args.get('modulo', '').strip() or None
        accion = request.args.get('accion', '').strip() or None
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        return jsonify(filtrar_bitacora(usuario=usuario, modulo=modulo, accion=accion, page=page, per_page=per_page))
    else:
        return jsonify([]), 401



### Solicitudes

@home_bp.route('/api/solicitudes/crear', methods=['POST'])
def api_crear_solicitud():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401

    resultado = crear_solicitud(request.form, session)
    if resultado.get('success'):
        nuevo_id = resultado.get('id')
        nombre_usr = session.get('name_surname') or session.get('nombre') or session.get('email_user') or ''
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'CREAR',
            f'Solicitud #{nuevo_id} creada por {nombre_usr}'
        )
        return jsonify({'status': 'success', 'message': resultado.get('message', 'Solicitud creada'), 'id': nuevo_id}), 200
    return jsonify({'status': 'error', 'message': resultado.get('message', 'No se pudo crear la solicitud')}), 400

@home_bp.route('/api/solicitudes/<int:id_solicitud>', methods=['GET'])
def api_obtener_solicitud(id_solicitud):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401

    solicitud = obtener_solicitud_por_id(id_solicitud)
    if solicitud:
        return jsonify({'status': 'success', 'data': solicitud}), 200
    return jsonify({'status': 'error', 'message': 'Solicitud no encontrada'}), 404

@home_bp.route('/api/solicitudes/actualizar', methods=['PUT', 'POST'])
def api_actualizar_solicitud():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401

    datos = request.form if request.form else request.get_json(silent=True) or {}
    id_solicitud = datos.get('id_solicitud') or datos.get('id')
    if not id_solicitud:
        return jsonify({'status': 'error', 'message': 'ID de solicitud requerido'}), 400

    resultado = actualizar_solicitud(id_solicitud, datos, session)
    if resultado.get('success'):
        return jsonify({'status': 'success', 'message': resultado.get('message', 'Solicitud actualizada')}), 200
    return jsonify({'status': 'error', 'message': resultado.get('message', 'No se pudo actualizar la solicitud')}), 400

@home_bp.route('/api/solicitudes/<int:id_solicitud>/actualizar-estatus', methods=['POST'])
def api_actualizar_estatus_solicitud(id_solicitud):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401

    datos = request.get_json(silent=True) or {}
    nuevo_estatus = datos.get('estatus', 'En Proceso')
    
    resultado = SolicitudModel.actualizar_estatus(id_solicitud, nuevo_estatus)
    if resultado:
        return jsonify({'success': True, 'message': 'Estado actualizado correctamente'}), 200
    return jsonify({'success': False, 'message': 'No se pudo actualizar el estado'}), 400

@home_bp.route('/api/solicitudes/eliminar/<int:id_solicitud>', methods=['DELETE'])
def api_eliminar_solicitud(id_solicitud):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401

    resultado = eliminar_solicitud(id_solicitud, session)
    if isinstance(resultado, dict):
        success = resultado.get('success')
    else:
        success = bool(resultado)

    if success:
        return jsonify({'status': 'success', 'message': resultado.get('message', 'Solicitud eliminada')}), 200
    return jsonify({'status': 'error', 'message': resultado.get('message', 'No se pudo eliminar la solicitud')}), 400



### Contratacion

@contrataciones_bp.route('/form-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template('contrataciones/form_contratacion.html')
    return redirect(url_for('login_bp.inicio'))

@contrataciones_bp.route('/contrataciones', methods=['GET'])
def gestionar_contrataciones():
    if 'conectado' in session:
        modelo = ContratacionModel()
        lista = modelo.obtener_todas_las_contrataciones()
        return render_template('contratacion/form_contratacion.html', contrataciones=lista)
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
        
        flash('Contratación no encontrada o ha sido eliminada.', 'error')
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
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
        exito, mensaje = modelo.registrar_contrataciones(request.form)
        
        if exito:
            return jsonify({'status': 'success', 'message': mensaje})
        return jsonify({'status': 'error', 'message': mensaje})
            
    return jsonify({'status': 'error', 'message': 'Sesión expirada.'}), 401


@contrataciones_bp.route('/procesar-actualizacion', methods=['POST'])
def procesar_actualizacion():
    if 'conectado' in session:
        modelo = ContratacionModel()
        
        exito, mensaje = modelo.actualizar_contratacion(request.form) 
        
        if exito:
            return jsonify({
                'status': 'success', 
                'message': mensaje,
                'redirect': url_for('contrataciones_bp.gestionar_contrataciones')
            })
        return jsonify({'status': 'error', 'message': mensaje})
            
    return jsonify({'status': 'error', 'message': 'Sesión expirada.'}), 401


@contrataciones_bp.route('/eliminar-contratacion/<int:id>', methods=['POST'])
def eliminar_contratacion(id):
    if 'conectado' in session:
        modelo = ContratacionModel()
        if modelo.eliminar_contratacion(id):
            return jsonify({'exito': True, 'mensaje': 'Contratación eliminada correctamente.'})
        return jsonify({'exito': False, 'mensaje': 'Error al intentar eliminar el registro.'})
            
    return jsonify({'exito': False, 'mensaje': 'Sesión expirada.'}), 401

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
        datos_formulario = session.pop('form_empresa', None)
        
        from models.model_empresas import EmpresaModel
        modelo = EmpresaModel()
        
        return render_template(f'{PATH_URLE}/form_empresa.html', datos_form=datos_formulario)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

@app.route('/form-registrar-empresas', methods=['POST'])
def procesar_registro():
    from controllers.controller_empresa import procesar_registro_empresa
    
    exito, mensaje, categoria = procesar_registro_empresa(request.form)
    
    if exito:
        return jsonify({
        'exito': exito,
        'mensaje': mensaje,
        'categoria': categoria
    })

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
        return jsonify({'exito': True, 'mensaje': 'Empresa actualizada correctamente.'})
    else:
        return jsonify({'exito': False, 'mensaje': 'Error al actualizar la empresa.', 'categoria': 'error'})

@app.route('/eliminar-empresa/<string:rif>', methods=['GET'])
def eliminar_empresa(rif):
    if 'conectado' in session:
        from controllers.controller_empresa import eliminar_empresa_por_rif
        
        if eliminar_empresa_por_rif(rif):
            return jsonify({'exito': True, 'mensaje': 'Empresa eliminada correctamente.'})
        else:
            return jsonify({'exito': False, 'mensaje': 'Error al intentar eliminar la empresa.', 'categoria': 'error'})
    else:
        return jsonify({'exito': False, 'mensaje': 'Debes iniciar sesión.', 'categoria': 'error'})


@home_bp.route('/bitacora', methods=['GET'])
@home_bp.route('/bitacora', methods=['GET'])
def viewBitacora():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesi n.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    # Obtener filtros actuales de la URL
    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_modulo = request.args.get('modulo', '').strip()
    filtro_accion = request.args.get('accion', '').strip()
    
    # 1. Obtener la página actual y la cantidad de registros por página
    page = request.args.get('page', 1, type=int) or 1
    per_page = request.args.get('per_page', 10, type=int) or 10
    allowed_per_page = {5, 10, 20, 50, 100}
    if per_page not in allowed_per_page:
        per_page = 10

    # Traer los registros paginados desde el modelo
    registros = filtrar_bitacora(
        usuario=filtro_usuario or None,
        modulo=filtro_modulo or None,
        accion=filtro_accion or None,
        page=page,
        per_page=per_page
    )

    total_registros = contar_bitacora_filtrada(
        usuario=filtro_usuario or None,
        modulo=filtro_modulo or None,
        accion=filtro_accion or None
    )
    total_pages = max(1, (total_registros + per_page - 1) // per_page)

    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages

    inicio = (page - 1) * per_page
    fin = inicio + per_page
    
    estadisticas = obtener_estadisticas_bitacora()
    
    return render_template(
        'bitacora/lista_bitacora.html',
        registros=registros,
        estadisticas=estadisticas,
        filtro_usuario=filtro_usuario,
        filtro_modulo=filtro_modulo,
        filtro_accion=filtro_accion,
        page=page,
        total_pages=total_pages,
        total_registros=total_registros,
        per_page=per_page,
        primera_fila=inicio + 1 if total_registros else 0,
        ultima_fila=min(fin, total_registros) if total_registros else 0
    )


@home_bp.route('/bitacora/ajax')
def bitacora_ajax():
    if 'conectado' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_modulo = request.args.get('modulo', '').strip()
    filtro_accion = request.args.get('accion', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    registros = filtrar_bitacora(
        usuario=filtro_usuario or None,
        modulo=filtro_modulo or None,
        accion=filtro_accion or None,
        page=page,
        per_page=per_page
    )

    total_registros = contar_bitacora_filtrada(
        usuario=filtro_usuario or None,
        modulo=filtro_modulo or None,
        accion=filtro_accion or None
    )

    html = render_template(
        'bitacora/_tabla_bitacora.html',
        registros=registros,
        estadisticas=obtener_estadisticas_bitacora(),
        filtro_usuario=filtro_usuario,
        filtro_modulo=filtro_modulo,
        filtro_accion=filtro_accion,
        page=page,
        per_page=per_page,
        total_registros=total_registros
    )

    return jsonify({'html': html})

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

    resultado = {'success': False}
    try:
        resultado = crear_solicitud(request.form, session) or {'success': False}
    except Exception as e:
        print(f"[Router] Error al crear solicitud: {e}")
        resultado = {'success': False}

    if resultado.get('success'):
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

    resultado = eliminar_solicitud(id_solicitud, session)
    if isinstance(resultado, dict):
        success = resultado.get('success')
    else:
        success = bool(resultado)

    if success:
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
    resultado = actualizar_solicitud(id_solicitud, request.form, session)
    if isinstance(resultado, dict):
        success = resultado.get('success')
    else:
        success = bool(resultado)

    if success:
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


@app.route('/api/dashboard/grafico-tipos', methods=['GET'])
def api_dashboard_grafico_tipos():
    if 'conectado' not in session:
        return Response('No autorizado', status=401)
    
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    
    try:
        datos = SolicitudModel.obtener_estadisticas_por_tipo()
    except Exception:
        datos = {}
    
    labels = list(datos.keys()) if datos else ['Sin datos']
    valores = [int(v) for v in datos.values()] if datos else [0]
    
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(6, 3))
    colores = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1', '#20c997']
    ax.bar(labels, valores, color=colores[:len(labels)])
    ax.set_title('Solicitudes por Tipo')
    ax.set_ylabel('Cantidad')
    ax.set_xlabel('Tipo')
    fig.tight_layout()
    fig.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    plt.close(fig)
    return Response(buffer.read(), mimetype='image/png')


@app.route('/api/dashboard/grafico-estatus', methods=['GET'])
def api_dashboard_grafico_estatus():
    if 'conectado' not in session:
        return Response('No autorizado', status=401)
    
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    
    try:
        datos = SolicitudModel.obtener_estadisticas()
    except Exception:
        datos = {}
    
    labels = list(datos.keys()) if datos else ['Sin datos']
    valores = [int(v) for v in datos.values()] if datos else [0]
    
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(5, 3))
    colores = ['#ffc107', '#0dcaf0', '#198754', '#6f42c1', '#dc3545']
    wedges, texts, autotexts = ax.pie(valores, labels=labels, autopct='%1.1f%%', colors=colores[:len(labels)], startangle=90)
    ax.set_title('Distribución por Estatus')
    fig.tight_layout()
    fig.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    plt.close(fig)
    return Response(buffer.read(), mimetype='image/png')


@app.route('/api/dashboard/grafico-parroquias', methods=['GET'])
def api_dashboard_grafico_parroquias():
    if 'conectado' not in session:
        return Response('No autorizado', status=401)
    
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    
    try:
        rows = SolicitudModel.obtener_estadisticas_por_parroquia()
    except Exception:
        rows = []
    
    if rows:
        labels = [r['parroquia'] for r in rows]
        valores = [int(r['total']) for r in rows]
    else:
        labels = ['Sin datos']
        valores = [0]
    
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(6, 3))
    colores = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1', '#20c997', '#fd7e14', '#20c997']
    ax.barh(labels, valores, color=colores[:len(labels)])
    ax.set_title('Solicitudes por Parroquia')
    ax.set_xlabel('Cantidad')
    fig.tight_layout()
    fig.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    plt.close(fig)
    return Response(buffer.read(), mimetype='image/png')


# Registrar el blueprint en la aplicación
app.register_blueprint(home_bp)
app.register_blueprint(contrataciones_bp)


# ============================================================
# MÓDULO: Manual del Sistema
# Abre el manual (PDF) en una ventana independiente, permitiendo
# consultarlo por completo sin salir del sistema.
# ============================================================
MANUAL_PDF = 'manuals/Manual_del_Sistema_INVILARA.pdf'

@app.route('/manual-sistema', methods=['GET'])
def manual_sistema():
    """Muestra el Manual del Sistema en un visor a pantalla completa."""
    pdf_url = url_for('static', filename=MANUAL_PDF)
    return render_template('manual/manual_sistema.html', pdf_url=pdf_url)

@app.route('/api/manual-sistema/pdf', methods=['GET'])
def manual_sistema_pdf():
    """Sirve el archivo PDF del manual directamente (descarga/visualización)."""
    import os
    from flask import send_from_directory
    directorio = os.path.join(app.root_path, 'static', 'manuals')
    return send_from_directory(directorio, 'Manual_del_Sistema_INVILARA.pdf',
                               mimetype='application/pdf')