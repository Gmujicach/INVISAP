"""
Controller para Informe de Avance de Obra
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models.model_informe_avance import InformeAvanceModel
from models.model_empleados import EmpleadoModel
from services.bitacora_service import BitacoraService
from werkzeug.utils import secure_filename
import os

from conexion.conexionBD import connectionBD_invilara

# Crear Blueprint para el módulo
informe_avance_bp = Blueprint('informe_avance_bp', __name__)

# Agregar al final del archivo controller_informe_avance.py, antes de los reportes

# ==================== API PARA MODALES (EVIDENCIAS E INSPECTORES) ====================

@informe_avance_bp.route('/api/obtener-evidencias', methods=['GET'])
def api_obtener_evidencias():
    """
    API para obtener evidencias filtradas por etapa
    Usado por los modales de selección
    """
    if 'conectado' not in session:
        return jsonify([]), 401
    
    try:
        etapa = request.args.get('etapa', '').lower()
        
        if etapa not in ['antes', 'durante', 'despues']:
            return jsonify({
                'status': 'error',
                'message': 'Etapa inválida'
            }), 400
        
        conn = connectionBD_invilara()
        if not conn:
            return jsonify([]), 500
        
        cur = conn.cursor(dictionary=True)
        
        # Consulta parametrizada para obtener evidencias por etapa
        sql = """
            SELECT id_evidencia, fotos, url_archivos, fecha_registro, etapa
            FROM evidencia
            WHERE etapa = %s AND estado = 1
            ORDER BY fecha_registro DESC
        """
        
        cur.execute(sql, (etapa,))
        evidencias = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify(evidencias)
        
    except Exception as e:
        print(f"Error api_obtener_evidencias: {e}")
        return jsonify([]), 500


@informe_avance_bp.route('/api/obtener-inspectores', methods=['GET'])
def api_obtener_inspectores():
    """
    API para obtener solo empleados con cargo 'Inspector'
    Usado por el modal de selección de inspector
    """
    if 'conectado' not in session:
        return jsonify([]), 401
    
    try:
        conn = connectionBD_invilara()
        if not conn:
            return jsonify([]), 500
        
        cur = conn.cursor(dictionary=True)
        
        # Solo inspectores activos (Prof. Jhoanly)
        sql = """
            SELECT id_empleados, nombre_empleado, cargo, gerencia_asignada
            FROM empleados
            WHERE cargo = 'Inspector' AND estado = 1
            ORDER BY nombre_empleado ASC
        """
        
        cur.execute(sql)
        inspectores = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify(inspectores)
        
    except Exception as e:
        print(f"Error api_obtener_inspectores: {e}")
        return jsonify([]), 500

# Configuración de carga de archivos
UPLOAD_FOLDER = 'static/uploads/evidencias'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB por imagen

def allowed_file(filename):
    """Valida extensión de archivo permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== RUTAS PRINCIPALES ====================

@informe_avance_bp.route('/inf_avance_obra', methods=['GET'])
def listar_informes():
    """
    Lista todos los informes de avance de obra
    Muestra tabla con informes y formulario de registro
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        informes = modelo.obtener_todos_informes()
        gerentes = modelo.obtener_gerentes_activos()
        
        # Registrar en bitácora
        BitacoraService.registrar_accion(
            session, 'Informes de Avance', 'VER',
            f'Accedió al módulo de Informes de Avance'
        )
        
        return render_template(
            'inf_avance_obra/inf_avance_obra.html', 
            informes=informes, 
            gerentes=gerentes
        )
        
    except Exception as e:
        print(f"Error en listar_informes: {e}")
        flash('Error al cargar los informes.', 'error')
        return render_template('inf_avance_obra/inf_avance_obra.html', informes=[], gerentes=[])


@informe_avance_bp.route('/informe-detalle/<int:id_informe>', methods=['GET'])
def ver_detalle_informe(id_informe):
    """
    Muestra el detalle completo de un informe
    Incluye evidencias fotográficas (antes, durante, después)
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        informe = modelo.obtener_informe_por_id(id_informe)
        
        if not informe:
            flash('El informe no existe.', 'error')
            return redirect(url_for('informe_avance_bp.listar_informes'))
        
        # Registrar en bitácora
        BitacoraService.registrar_accion(
            session, 'Informes de Avance', 'VER',
            f'Visualizó detalles del Informe #{id_informe}'
        )
        
        return render_template(
            'inf_avance_obra/detalle_informe.html',
            informe=informe
        )
        
    except Exception as e:
        print(f"Error en ver_detalle_informe: {e}")
        flash('Error al cargar el detalle del informe.', 'error')
        return redirect(url_for('informe_avance_bp.listar_informes'))


@informe_avance_bp.route('/editar-informe/<int:id_informe>', methods=['GET'])
def editar_informe(id_informe):
    """
    Muestra formulario de edición de informe
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        informe = modelo.obtener_informe_por_id(id_informe)
        gerentes = modelo.obtener_gerentes_activos()
        
        if not informe:
            flash('El informe no existe.', 'error')
            return redirect(url_for('informe_avance_bp.listar_informes'))
        
        # Registrar en bitácora
        BitacoraService.registrar_accion(
            session, 'Informes de Avance', 'VER',
            f'Accedió a editar Informe #{id_informe}'
        )
        
        return render_template(
            'inf_avance_obra/editar_informe.html',
            informe=informe,
            gerentes=gerentes
        )
        
    except Exception as e:
        print(f"Error en editar_informe: {e}")
        flash('Error al cargar el formulario de edición.', 'error')
        return redirect(url_for('informe_avance_bp.listar_informes'))


# ==================== API REST (FETCH/AJAX) ====================

@informe_avance_bp.route('/api/informes/crear', methods=['POST'])
def api_crear_informe():
    """
    API para crear informe con Fetch/Ajax (Prof. Escalona - OBLIGATORIO)
    Evita recargar la página completa
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401
    
    try:
        # Obtener datos del request (soporta JSON y FormData)
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        modelo = InformeAvanceModel()
        
        # Validación de existencia de gerente en tiempo real (Prof. Escalona)
        gerente_id = data.get('gerente_responsable_id')
        if gerente_id:
            modelo_empleado = EmpleadoModel()
            if not modelo_empleado.validar_empleado_activo(gerente_id):
                return jsonify({
                    'status': 'error', 
                    'message': 'El gerente/inspector seleccionado no existe o fue eliminado.'
                }), 400
        
        # Registrar informe usando el modelo
        nuevo_id = modelo.registrar_informe(data)
        
        if nuevo_id:
            # Registrar en bitácora
            BitacoraService.registrar_accion(
                session, 'Informes de Avance', 'CREAR',
                f'Informe #{nuevo_id} creado por {session.get("nombre", "")}'
            )
            
            return jsonify({
                'status': 'success', 
                'message': 'Informe registrado correctamente',
                'id': nuevo_id
            }), 201
        
        return jsonify({
            'status': 'error', 
            'message': 'No se pudo guardar el informe'
        }), 500
        
    except ValueError as ve:
        # Errores de validación (Regex, campos requeridos, etc.)
        return jsonify({
            'status': 'error', 
            'message': str(ve)
        }), 400
        
    except Exception as e:
        print(f"Error api_crear_informe: {e}")
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500


@informe_avance_bp.route('/api/informes/actualizar', methods=['PUT', 'POST'])
def api_actualizar_informe():
    """
    API para actualizar informe con Fetch/Ajax
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión no válida'}), 401
    
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        id_informe = data.get('id_informe')
        if not id_informe:
            return jsonify({
                'status': 'error', 
                'message': 'ID de informe no proporcionado'
            }), 400
        
        modelo = InformeAvanceModel()
        
        # Validar que el informe existe
        if not modelo.validar_informe_activo(id_informe):
            return jsonify({
                'status': 'error', 
                'message': 'El informe no existe o fue eliminado'
            }), 404
        
        # Actualizar informe
        if modelo.actualizar_informe(data):
            # Registrar en bitácora
            BitacoraService.registrar_accion(
                session, 'Informes de Avance', 'EDITAR',
                f'Informe #{id_informe} actualizado'
            )
            
            return jsonify({
                'status': 'success', 
                'message': 'Informe actualizado correctamente'
            })
        
        return jsonify({
            'status': 'error', 
            'message': 'Error al actualizar el informe'
        }), 500
        
    except ValueError as ve:
        return jsonify({
            'status': 'error', 
            'message': f'Error de validación: {str(ve)}'
        }), 400
        
    except Exception as e:
        print(f"Error api_actualizar_informe: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Error interno del servidor'
        }), 500


@informe_avance_bp.route('/api/informes/eliminar/<int:id_informe>', methods=['DELETE'])
def api_eliminar_informe(id_informe):
    """
    API para borrado lógico de informe (Prof. Escalona - OBLIGATORIO)
    No elimina físicamente, marca como inactivo
    """
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    
    try:
        modelo = InformeAvanceModel()
        
        # Validar que el informe existe
        if not modelo.validar_informe_activo(id_informe):
            return jsonify({
                'status': 'error', 
                'message': 'El informe no existe o ya fue eliminado'
            }), 404
        
        # Borrado lógico
        if modelo.eliminar_informe_logico(id_informe):
            # Registrar en bitácora
            BitacoraService.registrar_accion(
                session, 'Informes de Avance', 'ELIMINAR',
                f'Informe #{id_informe} eliminado (borrado lógico)'
            )
            
            return jsonify({
                'status': 'success', 
                'message': 'Informe eliminado correctamente'
            })
        
        return jsonify({
            'status': 'error', 
            'message': 'No se pudo eliminar el informe'
        }), 500
        
    except Exception as e:
        print(f"Error api_eliminar_informe: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Error interno del servidor'
        }), 500


@informe_avance_bp.route('/api/informes/validar-gerente/<int:id_empleado>', methods=['GET'])
def validar_gerente(id_empleado):
    """
    Validación en tiempo real (Prof. Escalona - OBLIGATORIO)
    Verifica que el empleado exista, esté activo y sea Gerente/Inspector
    Usado por eventos 'change' en el frontend
    """
    try:
        modelo_empleado = EmpleadoModel()
        empleado = modelo_empleado.obtener_empleado_por_id(id_empleado)
        
        if empleado and empleado.get('estado') == 1:
            es_valido = empleado.get('cargo') in ['Gerente', 'Inspector']
            
            return jsonify({
                'existe': True,
                'activo': True,
                'es_gerente_o_inspector': es_valido,
                'nombre': empleado.get('nombre_empleado'),
                'cargo': empleado.get('cargo')
            })
        
        return jsonify({
            'existe': False, 
            'activo': False,
            'es_gerente_o_inspector': False
        })
        
    except Exception as e:
        print(f"Error validar_gerente: {e}")
        return jsonify({
            'existe': False, 
            'activo': False,
            'es_gerente_o_inspector': False
        })


@informe_avance_bp.route('/api/informes/validar/<int:id_informe>', methods=['GET'])
def validar_informe_existe(id_informe):
    """
    Validación de existencia de informe en tiempo real
    Usado por otros módulos (publicaciones, reportes, etc.)
    """
    try:
        modelo = InformeAvanceModel()
        existe = modelo.validar_informe_activo(id_informe)
        
        return jsonify({
            'existe': existe,
            'activo': existe
        })
        
    except Exception as e:
        print(f"Error validar_informe_existe: {e}")
        return jsonify({
            'existe': False,
            'activo': False
        })


@informe_avance_bp.route('/api/informes/listar-json', methods=['GET'])
def api_listar_informes_json():
    """
    API para obtener lista de informes en formato JSON
    Usado por otros módulos o para DataTables
    """
    if 'conectado' not in session:
        return jsonify([]), 401
    
    try:
        modelo = InformeAvanceModel()
        informes = modelo.obtener_todos_informes()
        
        return jsonify(informes)
        
    except Exception as e:
        print(f"Error api_listar_informes_json: {e}")
        return jsonify([]), 500


# ==================== FORMULARIOS TRADICIONALES (FALLBACK) ====================

@informe_avance_bp.route('/form-registrar-informe-avance-obra', methods=['POST'])
def form_registrar_informe():
    """
    Formulario tradicional (fallback si no usa Fetch)
    Mantiene compatibilidad con navegadores antiguos
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        data = request.form.to_dict()
        
        # Validación de gerente
        gerente_id = data.get('gerente_responsable_id')
        if gerente_id:
            modelo_empleado = EmpleadoModel()
            if not modelo_empleado.validar_empleado_activo(gerente_id):
                flash('El gerente/inspector seleccionado no existe o fue eliminado.', 'error')
                return redirect(url_for('informe_avance_bp.listar_informes'))
        
        # Registrar informe
        nuevo_id = modelo.registrar_informe(data)
        
        if nuevo_id:
            # Registrar en bitácora
            BitacoraService.registrar_accion(
                session, 'Informes de Avance', 'CREAR',
                f'Informe #{nuevo_id} creado'
            )
            
            flash('Informe registrado correctamente', 'success')
        else:
            flash('Error al guardar el informe', 'error')
            
    except ValueError as ve:
        flash(f'Error de validación: {str(ve)}', 'error')
        
    except Exception as e:
        print(f"Error form_registrar_informe: {e}")
        flash('Error interno del servidor', 'error')
    
    return redirect(url_for('informe_avance_bp.listar_informes'))


@informe_avance_bp.route('/form-actualizar-informe', methods=['POST'])
def form_actualizar_informe():
    """
    Formulario tradicional para actualizar informe
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        data = request.form.to_dict()
        
        id_informe = data.get('id_informe')
        
        if modelo.actualizar_informe(data):
            # Registrar en bitácora
            BitacoraService.registrar_accion(
                session, 'Informes de Avance', 'EDITAR',
                f'Informe #{id_informe} actualizado'
            )
            
            flash('Informe actualizado correctamente', 'success')
        else:
            flash('Error al actualizar el informe', 'error')
            
    except ValueError as ve:
        flash(f'Error de validación: {str(ve)}', 'error')
        
    except Exception as e:
        print(f"Error form_actualizar_informe: {e}")
        flash('Error interno del servidor', 'error')
    
    return redirect(url_for('informe_avance_bp.listar_informes'))


@informe_avance_bp.route('/eliminar-informe/<int:id_informe>', methods=['GET'])
def eliminar_informe_get(id_informe):
    """
    Eliminación desde enlace GET (fallback)
    Realiza borrado lógico
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        
        if modelo.eliminar_informe_logico(id_informe):
            # Registrar en bitácora
            BitacoraService.registrar_accion(
                session, 'Informes de Avance', 'ELIMINAR',
                f'Informe #{id_informe} eliminado'
            )
            
            flash('Informe eliminado correctamente.', 'success')
        else:
            flash('No se pudo eliminar el informe.', 'error')
            
    except ValueError as ve:
        flash(f'Error: {str(ve)}', 'error')
        
    except Exception as e:
        print(f"Error eliminar_informe_get: {e}")
        flash('Error al eliminar el informe.', 'error')
    
    return redirect(url_for('informe_avance_bp.listar_informes'))


# ==================== REPORTES Y EXPORTACIÓN ====================

@informe_avance_bp.route('/generar-sabana/<int:id_informe>', methods=['GET'])
def generar_sabana(id_informe):
    """
    Genera la "Sábana" (reporte técnico de ~3 hojas)
    Toma datos organizados de todo el sistema
    Prof. Cadenas: Debe ser profesional y completo
    """
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    try:
        modelo = InformeAvanceModel()
        informe = modelo.obtener_informe_por_id(id_informe)
        
        if not informe:
            flash('El informe no existe.', 'error')
            return redirect(url_for('informe_avance_bp.listar_informes'))
        
        # Registrar en bitácora
        BitacoraService.registrar_accion(
            session, 'Informes de Avance', 'GENERAR_REPORTE',
            f'Generó sábana del Informe #{id_informe}'
        )
        
        # TODO: Implementar generación de PDF con ReportLab o WeasyPrint
        return render_template(
            'inf_avance_obra/sabana_informe.html',
            informe=informe
        )
        
    except Exception as e:
        print(f"Error generar_sabana: {e}")
        flash('Error al generar la sábana.', 'error')
        return redirect(url_for('informe_avance_bp.listar_informes'))