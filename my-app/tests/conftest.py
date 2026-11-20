import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import json

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app


UNIT_MODULES = {
    'test_administracion_respaldos.py': 'Administración de Respaldos',
    'test_bitacora.py': 'Bitácora',
    'test_contratacion.py': 'Contratación',
    'test_empleados.py': 'Empleados',
    'test_empresa.py': 'Empresa',
    'test_evidencias.py': 'Evidencias',
    'test_gravedad_obra.py': 'Gravedad de Obra',
    'test_informe_avance.py': 'Informe de Avance de Obra',
    'test_inspecciones.py': 'Inspecciones',
    'test_maquinaria.py': 'Maquinaria',
    'test_obras.py': 'Obras',
    'test_permisos_por_rol.py': 'Permisos por Rol',
    'test_prioridad.py': 'Prioridad',
    'test_proyectos.py': 'Proyectos',
    'test_publicaciones.py': 'Publicaciones',
    'test_reportes_estadisticos.py': 'Reportes Estadísticos',
    'test_reportes_excel.py': 'Reportes Excel',
    'test_reportes_pdf.py': 'Reportes PDF',
    'test_solicitudes.py': 'Solicitudes',
    'test_usuarios.py': 'Usuarios',
    'test_informe_validacion.py': 'Validación de Informes',
    'test_security_controls.py': 'Controles de Seguridad',
    'test_sql_filter_allowlists.py': 'Filtros SQL de Reportes',
}

INTEGRATION_MODULES = {
    'test_integracion_solicitudes.py': 'Solicitudes',
    'test_integracion_gravedad_obra.py': 'Gravedad de Obra',
    'test_integracion_prioridad.py': 'Prioridad',
    'test_integracion_proyectos.py': 'Proyectos',
    'test_integracion_maquinaria.py': 'Maquinaria',
    'test_integracion_contratacion.py': 'Contratación',
    'test_integracion_empresa.py': 'Empresa',
    'test_integracion_obras.py': 'Obras',
    'test_integracion_empleados.py': 'Empleados',
    'test_integracion_inspecciones.py': 'Inspecciones',
    'test_integracion_evidencias.py': 'Evidencias',
    'test_integracion_informe_avance.py': 'Informe de Avance de Obra',
    'test_integracion_publicaciones.py': 'Publicaciones',
    'test_integracion_reportes_pdf.py': 'Reportes PDF',
    'test_integracion_reportes_excel.py': 'Reportes Excel',
    'test_integracion_reportes_estadisticos.py': 'Reportes Estadísticos',
    'test_integracion_usuarios.py': 'Usuarios',
    'test_integracion_permisos_por_rol.py': 'Permisos por Rol',
    'test_integracion_administracion_respaldos.py': 'Administración de Respaldos',
    'test_integracion_bitacora.py': 'Bitácora',
}

SMOKE_MODULES = {
    'test_humo_solicitudes.py': 'Solicitudes',
    'test_humo_gravedad_obra.py': 'Gravedad de Obra',
    'test_humo_prioridad.py': 'Prioridad',
    'test_humo_proyectos.py': 'Proyectos',
    'test_humo_maquinaria.py': 'Maquinaria',
    'test_humo_contratacion.py': 'Contratación',
    'test_humo_empresa.py': 'Empresa',
    'test_humo_obras.py': 'Obras',
    'test_humo_empleados.py': 'Empleados',
    'test_humo_inspecciones.py': 'Inspecciones',
    'test_humo_evidencias.py': 'Evidencias',
    'test_humo_informe_avance.py': 'Informe de Avance de Obra',
    'test_humo_publicaciones.py': 'Publicaciones',
    'test_humo_reportes_pdf.py': 'Reportes PDF',
    'test_humo_reportes_excel.py': 'Reportes Excel',
    'test_humo_reportes_estadisticos.py': 'Reportes Estadísticos',
    'test_humo_usuarios.py': 'Usuarios',
    'test_humo_permisos_por_rol.py': 'Permisos por Rol',
    'test_humo_administracion_respaldos.py': 'Administración de Respaldos',
    'test_humo_bitacora.py': 'Bitácora',
    'test_login_smoke.py': 'Acceso de INVISAP',
}

API_MODULES = {
    'test_api_solicitudes.py': ('Solicitudes', 'JSON autenticado y control de sesión'),
    'test_api_gravedad_obra.py': ('Gravedad de Obra', 'JSON autenticado y listado'),
    'test_api_prioridad.py': ('Prioridad', 'paginación y propagación de filtros'),
    'test_api_proyectos.py': ('Proyectos', 'validación de código y parámetro consultado'),
    'test_api_maquinaria.py': ('Maquinaria', 'paginación y respuesta JSON'),
    'test_api_contratacion.py': ('Contratación', 'listado JSON de empresas y sesión'),
    'test_api_empresa.py': ('Empresa', 'consulta por RIF y respuestas 401/404/200'),
    'test_api_obras.py': ('Obras', 'listado JSON de estados y sesión'),
    'test_api_empleados.py': ('Empleados', 'paginación, conteo y respuesta JSON'),
    'test_api_inspecciones.py': ('Inspecciones', 'listado JSON de inspectores y sesión'),
    'test_api_evidencias.py': ('Evidencias', 'validación JSON de existencia por ID'),
    'test_api_informe_avance.py': ('Informe de Avance de Obra', 'listado JSON y control de sesión'),
    'test_api_publicaciones.py': ('Publicaciones', 'validación JSON del informe asociado'),
    'test_api_reportes_pdf.py': ('Reportes PDF', 'autenticación y módulo no válido'),
    'test_api_reportes_excel.py': ('Reportes Excel', 'autenticación y módulo no válido'),
    'test_api_reportes_estadisticos.py': ('Reportes Estadísticos', 'filtros y agrupación JSON'),
    'test_api_usuarios.py': ('Usuarios', 'autenticación, permiso y usuario inexistente'),
    'test_api_permisos_por_rol.py': ('Permisos por Rol', 'autenticación, autorización y consulta por rol'),
    'test_api_administracion_respaldos.py': ('Administración de Respaldos', 'autenticación y listado JSON'),
    'test_api_bitacora.py': ('Bitácora', 'autenticación, filtros y paginación JSON'),
    'test_parametrizacion_reportes.py': ('Reportes PDF y Excel', 'propagación de filtros de formularios'),
}

TEST_DESCRIPTIONS = {
    'test_limpia_nombre_de_archivo_de_respaldo': 'limpieza segura del nombre del archivo de respaldo',
    'test_formatea_tamano_de_respaldo': 'conversión del tamaño del respaldo a unidades legibles',
    'test_bitacora_acepta_texto_y_usuario_validos': 'aceptación de texto y usuario válidos en bitácora',
    'test_bitacora_rechaza_caracteres_no_permitidos': 'rechazo de caracteres no permitidos en bitácora',
    'test_registro_rechaza_datos_incompletos_sin_conectar_base_de_datos': 'rechazo de contratación incompleta sin conectar a la base de datos',
    'test_valida_datos_completos_de_contratacion': 'validación de campos, catálogos y fechas de contratación',
    'test_valida_y_limpia_nombre_y_cargo': 'validación y limpieza del nombre y cargo del empleado',
    'test_rechaza_datos_de_empleado_invalidos': 'rechazo de nombre, cargo y cédula inválidos',
    'test_empresa_existente_activa_no_se_registra_de_nuevo': 'prevención de duplicados para empresa activa',
    'test_empresa_nueva_usa_rif_parametrizado': 'registro de empresa con RIF enviado como parámetro SQL',
    'test_validadores_de_archivo_y_url': 'validación de nombre de archivo y URL de evidencia',
    'test_url_no_permite_traversal_de_directorios': 'rechazo de rutas que intentan salir del directorio de evidencias',
    'test_calcula_nivel_de_gravedad': 'clasificación del nivel según criticidad, incluidos los límites',
    'test_criticidad_rechaza_valores_fuera_de_rango': 'rechazo de criticidad fuera del rango de 0 a 100',
    'test_criticidad_acepta_y_normaliza_valor_numerico': 'normalización de criticidad numérica',
    'test_porcentaje_de_avance_se_limita_a_rango_valido': 'limitación del porcentaje de avance al rango de 0 a 100',
    'test_estado_de_informe_normaliza_opcion_valida': 'normalización del estado válido del informe',
    'test_rechaza_estado_de_informe_desconocido': 'rechazo de un estado de informe no catalogado',
    'test_consulta_solo_gerentes_o_inspectores_activos': 'consulta de responsables activos con cargos permitidos',
    'test_rechaza_identificador_no_numerico_sin_consultar_bd': 'rechazo de identificador inválido antes de consultar la base de datos',
    'test_validadores_de_inspeccion_aceptan_datos_correctos': 'aceptación de inspector, fecha y observaciones válidos',
    'test_validadores_de_inspeccion_rechazan_datos_invalidos': 'rechazo de inspector, fecha y observaciones inválidos',
    'test_tipo_de_inspeccion_rechaza_valores_no_catalogados': 'rechazo de tipo de inspección fuera del catálogo',
    'test_valida_nombre_y_tipo_de_maquinaria': 'validación de nombre y tipo de maquinaria',
    'test_rechaza_nombre_corto_y_tipo_ajeno_al_catalogo': 'rechazo de nombre corto y tipo de maquinaria no permitido',
    'test_valida_texto_y_numero_de_contrato': 'validación de texto de obra y número de contrato',
    'test_rechaza_texto_o_numero_de_contrato_con_caracteres_invalidos': 'rechazo de caracteres inválidos en obra y contrato',
    'test_fecha_fin_no_puede_ser_anterior_a_fecha_inicio': 'validación del orden cronológico de fechas de obra',
    'test_modulo_rechaza_url_que_no_empieza_con_barra': 'validación de URL de módulo con barra inicial',
    'test_rol_rechaza_nombre_con_caracteres_no_permitidos': 'rechazo de nombre de rol con caracteres no permitidos',
    'test_prioridad_redondea_rango_valido': 'redondeo del rango de prioridad válido',
    'test_prioridad_rechaza_rango_fuera_de_limites': 'rechazo de prioridad fuera del intervalo permitido',
    'test_prioridad_rechaza_origen_no_permitido': 'rechazo de origen de prioridad no permitido',
    'test_computos_metricos_se_serializan_y_se_recuperan': 'serialización y recuperación de cómputos métricos',
    'test_texto_legacy_de_computos_metricos_se_convierte': 'compatibilidad con cómputos métricos en formato anterior',
    'test_formatea_computos_metricos_para_mostrar': 'formateo legible de cómputos métricos',
    'test_obtener_publicacion_consulta_por_id_con_parametro': 'consulta de publicación por ID con parámetro SQL',
    'test_filtro_estadistico_acepta_columna_mapeada': 'aplicación de filtro estadístico a columna permitida',
    'test_filtro_excel_ignora_columna_no_mapeada': 'rechazo de columna no permitida en filtro Excel',
    'test_filtro_pdf_usa_parametro_y_no_interpola_valor': 'parametrización de valor en filtro PDF',
    'test_tipo_y_estado_de_solicitud_validos': 'validación de tipo y estado de solicitud',
    'test_rechaza_tipo_de_solicitud_desconocido': 'rechazo de tipo de solicitud no reconocido',
    'test_problematica_incluye_categoria_valida': 'asociación de categoría válida a la problemática',
    'test_listar_usuarios_asigna_avatar_por_defecto': 'asignación de avatar por defecto a usuarios sin avatar',
    'test_rechaza_gerente_inactivo_antes_de_crear_avance': 'rechazo de gerente inactivo antes de crear avance',
    'test_report_filters_ignore_unmapped_sql_identifiers': 'rechazo de identificadores SQL no mapeados',
    'test_report_filters_bind_values_for_mapped_columns': 'parametrización de valores en columnas permitidas',
    'test_query_builder_binds_values_and_rejects_untrusted_identifiers': 'construcción segura de consultas y rechazo de identificadores no confiables',
    'test_query_builder_rejects_unsupported_operator_and_invalid_between': 'rechazo de operadores no admitidos y rangos BETWEEN inválidos',
    'test_no_acepta_verificacion_si_no_hay_secreto_configurado': 'rechazo de verificación externa si no existe secreto configurado',
    'test_no_acepta_verificacion_si_google_no_responde': 'manejo del fallo de respuesta del servicio de verificación',
}


# ============================================================
# EVIDENCE / SCREENSHOT CONFIGURATION
# ============================================================
EVIDENCE_BASE_DIR = Path(__file__).parent / "evidence"
EVIDENCE_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Subdirectories per test type
EVIDENCE_DIRS = {
    "unit": EVIDENCE_BASE_DIR / "unit",
    "integration": EVIDENCE_BASE_DIR / "integration",
    "api": EVIDENCE_BASE_DIR / "api",
    "smoke": EVIDENCE_BASE_DIR / "smoke",
    "ui": EVIDENCE_BASE_DIR / "ui",
    "performance": EVIDENCE_BASE_DIR / "performance",
    "acceptance": EVIDENCE_BASE_DIR / "acceptance",
}

for d in EVIDENCE_DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

# Traceability matrix mapping for screenshot naming
# Format: test_name -> (test_type, module, case_id)
TRACEABILITY_MAP = {
    # Unit tests
    "test_solicitudes": ("unit", "Solicitudes", "CP-UNI-RF01"),
    "test_gravedad_obra": ("unit", "Gravedad de Obra", "CP-UNI-RF02"),
    "test_prioridad": ("unit", "Prioridad", "CP-UNI-RF03"),
    "test_usuarios": ("unit", "Usuarios", "CP-UNI-RF04"),
    "test_empleados": ("unit", "Empleados", "CP-UNI-RF05"),
    "test_empresa": ("unit", "Empresa", "CP-UNI-RF06"),
    "test_maquinaria": ("unit", "Maquinaria", "CP-UNI-RF07"),
    "test_proyectos": ("unit", "Proyectos", "CP-UNI-RF08"),
    "test_contratacion": ("unit", "Contratación", "CP-UNI-RF09"),
    "test_obras": ("unit", "Obras", "CP-UNI-RF10"),
    "test_inspecciones": ("unit", "Inspecciones", "CP-UNI-RF11"),
    "test_evidencias": ("unit", "Evidencias", "CP-UNI-RF12"),
    "test_informe_avance": ("unit", "Informe de Avance de Obra", "CP-UNI-RF13"),
    "test_publicaciones": ("unit", "Publicaciones", "CP-UNI-RF14"),
    "test_reportes_pdf": ("unit", "Reportes PDF", "CP-UNI-RF15"),
    "test_reportes_excel": ("unit", "Reportes Excel", "CP-UNI-RF15"),
    "test_reportes_estadisticos": ("unit", "Reportes Estadísticos", "CP-UNI-RF15"),
    "test_administracion_respaldos": ("unit", "Administración de Respaldos", "CP-UNI-RF16"),
    "test_bitacora": ("unit", "Bitácora", "CP-UNI-RNF06"),
    "test_permisos_por_rol": ("unit", "Permisos por Rol", "CP-UNI-RNF03"),
    "test_security_controls": ("unit", "Seguridad", "CP-UNI-RNF01"),
    "test_sql_filter_allowlists": ("unit", "Validación Entradas", "CP-UNI-RNF05"),
    "test_informe_validacion": ("unit", "Validación Informes", "CP-UNI-RF13"),
    # Integration tests
    "test_integracion_solicitudes": ("integration", "Solicitudes", "CP-INT-RF01"),
    "test_integracion_gravedad_obra": ("integration", "Gravedad de Obra", "CP-INT-RF02"),
    "test_integracion_prioridad": ("integration", "Prioridad", "CP-INT-RF03"),
    "test_integracion_proyectos": ("integration", "Proyectos", "CP-INT-RF08"),
    "test_integracion_maquinaria": ("integration", "Maquinaria", "CP-INT-RF07"),
    "test_integracion_contratacion": ("integration", "Contratación", "CP-INT-RF09"),
    "test_integracion_empresa": ("integration", "Empresa", "CP-INT-RF06"),
    "test_integracion_obras": ("integration", "Obras", "CP-INT-RF10"),
    "test_integracion_empleados": ("integration", "Empleados", "CP-INT-RF05"),
    "test_integracion_inspecciones": ("integration", "Inspecciones", "CP-INT-RF11"),
    "test_integracion_evidencias": ("integration", "Evidencias", "CP-INT-RF12"),
    "test_integracion_informe_avance": ("integration", "Informe de Avance", "CP-INT-RF13"),
    "test_integracion_publicaciones": ("integration", "Publicaciones", "CP-INT-RF14"),
    "test_integracion_reportes_pdf": ("integration", "Reportes PDF", "CP-INT-RF15"),
    "test_integracion_reportes_excel": ("integration", "Reportes Excel", "CP-INT-RF15"),
    "test_integracion_reportes_estadisticos": ("integration", "Reportes Estadísticos", "CP-INT-RF15"),
    "test_integracion_usuarios": ("integration", "Usuarios", "CP-INT-RF04"),
    "test_integracion_permisos_por_rol": ("integration", "Permisos por Rol", "CP-INT-RNF03"),
    "test_integracion_administracion_respaldos": ("integration", "Respaldos", "CP-INT-RF16"),
    "test_integracion_bitacora": ("integration", "Bitácora", "CP-INT-RNF06"),
    "test_contrataciones_bitacora": ("integration", "Contratación-Bitácora", "CP-INT-RF09"),
    # API tests
    "test_api_solicitudes": ("api", "Solicitudes", "CP-API-RF01"),
    "test_api_gravedad_obra": ("api", "Gravedad de Obra", "CP-API-RF02"),
    "test_api_prioridad": ("api", "Prioridad", "CP-API-RF03"),
    "test_api_proyectos": ("api", "Proyectos", "CP-API-RF08"),
    "test_api_maquinaria": ("api", "Maquinaria", "CP-API-RF07"),
    "test_api_contratacion": ("api", "Contratación", "CP-API-RF09"),
    "test_api_empresa": ("api", "Empresa", "CP-API-RF06"),
    "test_api_obras": ("api", "Obras", "CP-API-RF10"),
    "test_api_empleados": ("api", "Empleados", "CP-API-RF05"),
    "test_api_inspecciones": ("api", "Inspecciones", "CP-API-RF11"),
    "test_api_evidencias": ("api", "Evidencias", "CP-API-RF12"),
    "test_api_informe_avance": ("api", "Informe de Avance", "CP-API-RF13"),
    "test_api_publicaciones": ("api", "Publicaciones", "CP-API-RF14"),
    "test_api_reportes_pdf": ("api", "Reportes PDF", "CP-API-RF15"),
    "test_api_reportes_excel": ("api", "Reportes Excel", "CP-API-RF15"),
    "test_api_reportes_estadisticos": ("api", "Reportes Estadísticos", "CP-API-RF15"),
    "test_api_usuarios": ("api", "Usuarios", "CP-API-RF04"),
    "test_api_permisos_por_rol": ("api", "Permisos por Rol", "CP-API-RNF03"),
    "test_api_administracion_respaldos": ("api", "Respaldos", "CP-API-RF16"),
    "test_api_bitacora": ("api", "Bitácora", "CP-API-RNF06"),
    "test_parametrizacion_reportes": ("api", "Reportes Parametrización", "CP-API-RF15"),
    # Smoke tests
    "test_humo_solicitudes": ("smoke", "Solicitudes", "CP-HUM-RF01"),
    "test_humo_gravedad_obra": ("smoke", "Gravedad de Obra", "CP-HUM-RF02"),
    "test_humo_prioridad": ("smoke", "Prioridad", "CP-HUM-RF03"),
    "test_humo_proyectos": ("smoke", "Proyectos", "CP-HUM-RF08"),
    "test_humo_maquinaria": ("smoke", "Maquinaria", "CP-HUM-RF07"),
    "test_humo_contratacion": ("smoke", "Contratación", "CP-HUM-RF09"),
    "test_humo_empresa": ("smoke", "Empresa", "CP-HUM-RF06"),
    "test_humo_obras": ("smoke", "Obras", "CP-HUM-RF10"),
    "test_humo_empleados": ("smoke", "Empleados", "CP-HUM-RF05"),
    "test_humo_inspecciones": ("smoke", "Inspecciones", "CP-HUM-RF11"),
    "test_humo_evidencias": ("smoke", "Evidencias", "CP-HUM-RF12"),
    "test_humo_informe_avance": ("smoke", "Informe de Avance", "CP-HUM-RF13"),
    "test_humo_publicaciones": ("smoke", "Publicaciones", "CP-HUM-RF14"),
    "test_humo_reportes_pdf": ("smoke", "Reportes PDF", "CP-HUM-RF15"),
    "test_humo_reportes_excel": ("smoke", "Reportes Excel", "CP-HUM-RF15"),
    "test_humo_reportes_estadisticos": ("smoke", "Reportes Estadísticos", "CP-HUM-RF15"),
    "test_humo_usuarios": ("smoke", "Usuarios", "CP-HUM-RF04"),
    "test_humo_permisos_por_rol": ("smoke", "Permisos por Rol", "CP-HUM-RNF03"),
    "test_humo_administracion_respaldos": ("smoke", "Respaldos", "CP-HUM-RF16"),
    "test_humo_bitacora": ("smoke", "Bitácora", "CP-HUM-RNF06"),
    "test_login_smoke": ("smoke", "Acceso INVISAP", "CP-HUM-RNF01"),
    # UI tests
    "test_formulario_de_acceso_se_muestra_en_el_navegador": ("ui", "Login", "CP-UI-RNF01"),
    "test_formulario_de_acceso_tiene_etiquetas_y_acciones_comprensibles": ("ui", "Login", "CP-UI-RNF08"),
    # Performance tests
    "locust_": ("performance", "", "CP-LOC-RNF10"),
}

def _get_traceability_info(item):
    """Extract traceability info from test item for screenshot naming."""
    nodeid = item.nodeid.replace('\\', '/')
    
    # Get test file name without extension
    test_file = nodeid.split('/')[-1].split('::')[0].replace('.py', '')
    
    # Get test function name
    test_function = item.originalname or item.name.split('[', 1)[0]
    
    # Try exact match first
    for key, (test_type, module, case_id) in TRACEABILITY_MAP.items():
        if key in test_file or key in test_function:
            return test_type, module, case_id, test_function
    
    # Fallback: infer from path
    if 'tests/unit/' in nodeid:
        module = UNIT_MODULES.get(test_file + '.py', test_file.replace('test_', '').replace('_', ' ').title())
        return "unit", module, f"CP-UNI-{test_file.upper()}", test_function
    elif 'tests/integration/' in nodeid:
        module = INTEGRATION_MODULES.get(test_file + '.py', test_file.replace('test_integracion_', '').replace('_', ' ').title())
        return "integration", module, f"CP-INT-{test_file.replace('test_integracion_', '').upper()}", test_function
    elif 'tests/api/' in nodeid:
        api_case = API_MODULES.get(test_file + '.py')
        module = api_case[0] if api_case else test_file.replace('test_api_', '').replace('_', ' ').title()
        return "api", module, f"CP-API-{test_file.replace('test_api_', '').upper()}", test_function
    elif 'tests/smoke/' in nodeid:
        module = SMOKE_MODULES.get(test_file + '.py', test_file.replace('test_humo_', '').replace('test_login_', '').replace('_', ' ').title())
        return "smoke", module, f"CP-HUM-{test_file.replace('test_humo_', '').replace('test_login_', '').upper()}", test_function
    elif 'tests/ui/' in nodeid:
        return "ui", "Login", f"CP-UI-{test_function.upper()}", test_function
    elif 'tests/performance/' in nodeid:
        module = test_file.replace('locust_', '').replace('_', ' ').title()
        return "performance", module, f"CP-LOC-RNF10-{test_file.replace('locust_', '').upper()}", test_function
    
    return "unknown", "Unknown", "CP-UNKNOWN", test_function


def _generate_screenshot_name(test_type, module, case_id, test_function, outcome="passed"):
    """Generate structured screenshot filename: tipoPrueba_modulo_IDcaso_resultado_timestamp.png"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean module name for filename
    clean_module = re.sub(r'[^\w\s-]', '', module).strip().replace(' ', '_')
    clean_case_id = case_id.replace('/', '-').replace('..', '_')
    clean_function = re.sub(r'[^\w]', '_', test_function)
    filename = f"{test_type}_{clean_module}_{clean_case_id}_{clean_function}_{outcome}_{timestamp}.png"
    return filename


def _unit_module(item):
    if 'tests/unit/' not in item.nodeid.replace('\\', '/'):
        return None
    filename = item.nodeid.replace('\\', '/').split('/')[-1].split('::')[0]
    return UNIT_MODULES.get(filename)


def _describe_test(item):
    function_name = item.originalname or item.name.split('[', 1)[0]
    description = TEST_DESCRIPTIONS.get(function_name)
    if description:
        return description
    readable = re.sub(r'[_\[\]-]+', ' ', item.name.removeprefix('test_')).strip()
    return readable


_unit_results = defaultdict(list)
_integration_results = defaultdict(list)
_smoke_results = defaultdict(list)
_api_results = defaultdict(list)


def _integration_module(item):
    normalized_nodeid = item.nodeid.replace('\\', '/')
    if 'tests/integration/' not in normalized_nodeid:
        return None
    filename = normalized_nodeid.split('/')[-1].split('::')[0]
    return INTEGRATION_MODULES.get(filename)


def _smoke_module(item):
    normalized_nodeid = item.nodeid.replace('\\', '/')
    if 'tests/smoke/' not in normalized_nodeid:
        return None
    filename = normalized_nodeid.split('/')[-1].split('::')[0]
    return SMOKE_MODULES.get(filename)


def _api_module(item):
    normalized_nodeid = item.nodeid.replace('\\', '/')
    if 'tests/api/' not in normalized_nodeid:
        return None
    filename = normalized_nodeid.split('/')[-1].split('::')[0]
    return API_MODULES.get(filename)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    module = _unit_module(item)
    if module:
        print(
            f'\n[PRUEBA UNITARIA] {module}: '
            f'{_describe_test(item)}.'
        )
        return

    module = _integration_module(item)
    if module:
        print(
            f'\n[PRUEBA DE INTEGRACIÓN] {module}: '
            'comprobando la ruta Flask, el endpoint, el método HTTP '
            'y la generación de URL.'
        )
        return

    module = _smoke_module(item)
    if module:
        filename = item.nodeid.replace('\\', '/').split('/')[-1].split('::')[0]
        if filename == 'test_login_smoke.py':
            print(
                f'\n[PRUEBA DE HUMO] {module}: '
                'solicitando GET /login y comprobando HTTP 200 '
                'y ausencia de aviso de sesión incorrecto.'
            )
        else:
            from tests.smoke.smoke_routes import SMOKE_ROUTES

            case = next(
                (
                    route for route in SMOKE_ROUTES.values()
                    if route['name'] == module
                ),
                None,
            )
            if case:
                print(
                    f"\n[PRUEBA DE HUMO] {module}: "
                    f"solicitando GET {case['path']} y comprobando "
                    'que no responda HTTP 404 ni 500.'
                )
        return

    api_case = _api_module(item)
    if api_case:
        module, description = api_case
        print(
            f'\n[PRUEBA DE BACKEND/API] {module}: '
            f'comprobando {description}.'
        )


def pytest_runtest_logreport(report):
    nodeid = report.nodeid.replace('\\', '/')
    if report.when == 'call' or (
        report.when == 'setup' and (report.failed or report.skipped)
    ):
        outcome = {
            'passed': 'APROBADA',
            'failed': 'FALLIDA',
            'skipped': 'OMITIDA',
        }.get(report.outcome, report.outcome.upper())
        if 'tests/unit/' in nodeid:
            filename = nodeid.split('/')[-1].split('::')[0]
            module = UNIT_MODULES.get(filename)
            if module:
                _unit_results[module].append(report.outcome)
                print(
                    f'\nConcluyó prueba de {module} — '
                    f'Tipo: Prueba unitaria — Resultado: {outcome}.'
                )
        elif 'tests/integration/' in nodeid:
            filename = nodeid.split('/')[-1].split('::')[0]
            module = INTEGRATION_MODULES.get(filename)
            if module:
                _integration_results[module].append(report.outcome)
                print(
                    f'\nConcluyó prueba de {module} — '
                    f'Tipo: Prueba de integración — Resultado: {outcome}.'
                )
        elif 'tests/smoke/' in nodeid:
            filename = nodeid.split('/')[-1].split('::')[0]
            module = SMOKE_MODULES.get(filename)
            if module:
                _smoke_results[module].append(report.outcome)
                print(
                    f'\nConcluyó prueba de {module} — '
                    f'Tipo: Prueba de humo (smoke) — Resultado: {outcome}.'
                )
        elif 'tests/api/' in nodeid:
            filename = nodeid.split('/')[-1].split('::')[0]
            api_case = API_MODULES.get(filename)
            if api_case:
                module, _ = api_case
                _api_results[module].append(report.outcome)
                print(
                    f'\nConcluyó prueba de {module} — '
                    f'Tipo: Prueba de backend (API) — Resultado: {outcome}.'
                )


# ============================================================
# SCREENSHOT CAPTURE HOOKS
# ============================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture screenshots on test failure for UI tests."""
    outcome = yield
    rep = outcome.get_result()
    
    # Only capture screenshots for UI tests (Playwright/Selenium)
    if rep.when == "call" and "tests/ui/" in item.nodeid.replace('\\', '/'):
        test_type, module, case_id, test_function = _get_traceability_info(item)
        
        # Capture on failure
        if rep.failed:
            page = item.funcargs.get("page")
            driver = item.funcargs.get("driver")
            
            screenshot_name = _generate_screenshot_name(test_type, module, case_id, test_function, "FAILED")
            screenshot_path = EVIDENCE_DIRS["ui"] / screenshot_name
            
            if page:  # Playwright
                try:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"\n[EVIDENCIA UI] Captura de fallo guardada: {screenshot_path}")
                except Exception as e:
                    print(f"\n[EVIDENCIA UI] Error capturando screenshot Playwright: {e}")
            elif driver:  # Selenium
                try:
                    driver.save_screenshot(str(screenshot_path))
                    print(f"\n[EVIDENCIA UI] Captura de fallo guardada: {screenshot_path}")
                except Exception as e:
                    print(f"\n[EVIDENCIA UI] Error capturando screenshot Selenium: {e}")
        
        # Also capture on pass for evidence
        elif rep.passed:
            page = item.funcargs.get("page")
            driver = item.funcargs.get("driver")
            
            screenshot_name = _generate_screenshot_name(test_type, module, case_id, test_function, "PASSED")
            screenshot_path = EVIDENCE_DIRS["ui"] / screenshot_name
            
            if page:  # Playwright
                try:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"\n[EVIDENCIA UI] Captura de éxito guardada: {screenshot_path}")
                except Exception as e:
                    print(f"\n[EVIDENCIA UI] Error capturando screenshot Playwright: {e}")
            elif driver:  # Selenium
                try:
                    driver.save_screenshot(str(screenshot_path))
                    print(f"\n[EVIDENCIA UI] Captura de éxito guardada: {screenshot_path}")
                except Exception as e:
                    print(f"\n[EVIDENCIA UI] Error capturando screenshot Selenium: {e}")


def pytest_sessionfinish(session, exitstatus):
    """Generate evidence summary report at end of test session."""
    evidence_summary = {
        "timestamp": datetime.now().isoformat(),
        "exit_status": exitstatus,
        "evidence_dirs": {k: str(v) for k, v in EVIDENCE_DIRS.items()},
        "screenshots_captured": {}
    }
    
    for test_type, dir_path in EVIDENCE_DIRS.items():
        screenshots = list(dir_path.glob("*.png"))
        evidence_summary["screenshots_captured"][test_type] = len(screenshots)
        if screenshots:
            evidence_summary["screenshots_captured"][f"{test_type}_files"] = [s.name for s in screenshots]
    
    summary_path = EVIDENCE_BASE_DIR / "evidence_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(evidence_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n[EVIDENCIA] Resumen de capturas guardado en: {summary_path}")
    for test_type, count in evidence_summary["screenshots_captured"].items():
        if isinstance(count, int):
            print(f"  {test_type}: {count} capturas")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    for results, title, test_type in (
        (_unit_results, 'RESUMEN DE PRUEBAS UNITARIAS POR MÓDULO', 'Prueba unitaria'),
        (
            _integration_results,
            'RESUMEN DE PRUEBAS DE INTEGRACIÓN POR MÓDULO',
            'Prueba de integración',
        ),
        (
            _smoke_results,
            'RESUMEN DE PRUEBAS DE HUMO POR MÓDULO',
            'Prueba de humo (smoke)',
        ),
        (
            _api_results,
            'RESUMEN DE PRUEBAS DE BACKEND/API POR MÓDULO',
            'Prueba de backend (API)',
        ),
    ):
        if not results:
            continue
        terminalreporter.write_sep('=', title)
        for module, outcomes in results.items():
            failed = outcomes.count('failed')
            skipped = outcomes.count('skipped')
            passed = outcomes.count('passed')
            result = 'APROBADA' if not failed and not skipped else 'REVISAR'
            terminalreporter.write_line(
                f'Concluyó prueba de {module} — Tipo: {test_type} — '
                f'{result}: {passed} aprobadas, {failed} fallidas, {skipped} omitidas.'
            )


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def api_client(app, authenticated_permissions):
    test_client = app.test_client()
    with test_client.session_transaction() as session:
        session['conectado'] = True
        session['name_surname'] = 'Usuario de pruebas API'
    return test_client


@pytest.fixture
def authenticated_permissions(monkeypatch):
    from controllers import UserController
    from models.model_seguridad import ModuloModel

    monkeypatch.setattr(ModuloModel, 'consultar_activos', lambda self: [])
    monkeypatch.setattr(UserController, 'verificar_permiso', lambda *args, **kwargs: True)
    monkeypatch.setattr(
        UserController,
        'verificar_permiso_accion',
        lambda *args, **kwargs: True
    )


# ============================================================
# PLAYWRIGHT FIXTURES
# ============================================================
@pytest.fixture(scope="session")
def playwright_browser():
    """Session-scoped Playwright browser fixture."""
    playwright = pytest.importorskip(
        "playwright.sync_api",
        reason="Instala Playwright: pip install playwright && playwright install chromium"
    )
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(playwright_browser, request):
    """Page fixture with automatic screenshot capture on failure."""
    base_url = os.getenv("INVISAP_TEST_URL", "http://127.0.0.1:5600")
    page = playwright_browser.new_page()
    page.set_default_timeout(30000)
    
    # Store test info for screenshot naming
    page._test_info = {
        "base_url": base_url,
        "test_name": request.node.name,
    }
    
    yield page
    
    # Cleanup
    page.close()


# ============================================================
# SELENIUM FIXTURES
# ============================================================
@pytest.fixture(scope="session")
def selenium_driver():
    """Session-scoped Selenium WebDriver fixture."""
    selenium = pytest.importorskip(
        "selenium.webdriver",
        reason="Instala Selenium: pip install selenium"
    )
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = selenium.webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture
def driver(selenium_driver, request):
    """Driver fixture with test info for screenshot naming."""
    selenium_driver._test_info = {
        "test_name": request.node.name,
    }
    yield selenium_driver
