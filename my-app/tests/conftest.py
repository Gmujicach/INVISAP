import os
import re
import sys
from collections import defaultdict

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
