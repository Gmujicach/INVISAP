MODULE_ROUTES = {
    'solicitudes': {
        'name': 'Solicitudes',
        'rule': '/lista-de-solicitudes',
        'endpoint': 'lista_solicitudes',
        'method': 'GET',
        'values': {},
        'description': 'registro de la ruta de listado de solicitudes',
    },
    'gravedad_obra': {
        'name': 'Gravedad de Obra',
        'rule': '/api/gravedad/listar',
        'endpoint': 'home_bp.api_listar_gravedades',
        'method': 'GET',
        'values': {},
        'description': 'conexión de la API de gravedad con su endpoint Flask',
    },
    'prioridad': {
        'name': 'Prioridad',
        'rule': '/api/prioridad/listar',
        'endpoint': 'home_bp.api_listar_prioridad',
        'method': 'GET',
        'values': {},
        'description': 'conexión de la API de prioridad con su endpoint Flask',
    },
    'proyectos': {
        'name': 'Proyectos',
        'rule': '/gestionar-proyectos',
        'endpoint': 'home_bp.viewFormProyectos',
        'method': 'GET',
        'values': {},
        'description': 'registro de la vista de gestión de proyectos',
    },
    'maquinaria': {
        'name': 'Maquinaria',
        'rule': '/maquinaria',
        'endpoint': 'home_bp.viewFormMaquinaria',
        'method': 'GET',
        'values': {},
        'description': 'registro de la vista de gestión de maquinaria',
    },
    'contratacion': {
        'name': 'Contratación',
        'rule': '/contrataciones',
        'endpoint': 'contrataciones_bp.gestionar_contrataciones',
        'method': 'GET',
        'values': {},
        'description': 'registro de la vista de gestión de contrataciones',
    },
    'empresa': {
        'name': 'Empresa',
        'rule': '/lista-empresas',
        'endpoint': 'lista_empresas',
        'method': 'GET',
        'values': {},
        'description': 'registro de la ruta de listado de empresas',
    },
    'obras': {
        'name': 'Obras',
        'rule': '/gestionar-obras',
        'endpoint': 'obra_bp.vista_gestionar_obras',
        'method': 'GET',
        'values': {},
        'description': 'registro de la vista de gestión de obras',
    },
    'empleados': {
        'name': 'Empleados',
        'rule': '/empleados/',
        'endpoint': 'empleado_bp.list_empleados',
        'method': 'GET',
        'values': {},
        'description': 'registro del listado de empleados',
    },
    'inspecciones': {
        'name': 'Inspecciones',
        'rule': '/inspecciones/',
        'endpoint': 'inspeccion_bp.list_inspecciones',
        'method': 'GET',
        'values': {},
        'description': 'registro del listado de inspecciones',
    },
    'evidencias': {
        'name': 'Evidencias',
        'rule': '/evidencias/listar',
        'endpoint': 'evidencia_bp.show_listar_evidencias',
        'method': 'GET',
        'values': {},
        'description': 'registro del listado de evidencias',
    },
    'informe_avance': {
        'name': 'Informe de Avance de Obra',
        'rule': '/inf_avance_obra',
        'endpoint': 'informe_avance_bp.listar_informes',
        'method': 'GET',
        'values': {},
        'description': 'registro del listado de informes de avance',
    },
    'publicaciones': {
        'name': 'Publicaciones',
        'rule': '/lista-publicaciones',
        'endpoint': 'home_bp.lista_publicaciones',
        'method': 'GET',
        'values': {},
        'description': 'registro del listado de publicaciones',
    },
    'reportes_pdf': {
        'name': 'Reportes PDF',
        'rule': '/reporte-pdf',
        'endpoint': 'reporte_pdf_bp.generarReportePDF',
        'method': 'GET',
        'values': {},
        'description': 'registro del endpoint de reportes PDF',
    },
    'reportes_excel': {
        'name': 'Reportes Excel',
        'rule': '/reporte-excel',
        'endpoint': 'reporte_excel_bp.generarReporteExcel',
        'method': 'GET',
        'values': {},
        'description': 'registro del endpoint de reportes Excel',
    },
    'reportes_estadisticos': {
        'name': 'Reportes Estadísticos',
        'rule': '/reporte-estadistico',
        'endpoint': 'reporte_estadistico_bp.generarReporteEstadistico',
        'method': 'GET',
        'values': {},
        'description': 'registro del endpoint de reportes estadísticos',
    },
    'usuarios': {
        'name': 'Usuarios',
        'rule': '/api/users/<int:user_id>',
        'endpoint': 'user_bp.api_detalle_usuario',
        'method': 'GET',
        'values': {'user_id': 1},
        'description': 'generación de la ruta de consulta de usuario por ID',
    },
    'permisos_por_rol': {
        'name': 'Permisos por Rol',
        'rule': '/gestionar-permisos',
        'endpoint': 'home_bp.viewFormPermisos',
        'method': 'GET',
        'values': {},
        'description': 'registro de la vista de gestión de permisos',
    },
    'administracion_respaldos': {
        'name': 'Administración de Respaldos',
        'rule': '/respaldo/',
        'endpoint': 'respaldo_bp.listar_respaldos_view',
        'method': 'GET',
        'values': {},
        'description': 'registro de la vista de administración de respaldos',
    },
    'bitacora': {
        'name': 'Bitácora',
        'rule': '/api/obtener-bitacora-json',
        'endpoint': 'home_bp.api_obtener_bitacora_json',
        'method': 'GET',
        'values': {},
        'description': 'conexión de la API de bitácora con su endpoint Flask',
    },
}


def verify_module_route(app, module_key):
    case = MODULE_ROUTES[module_key]
    matches = [
        rule for rule in app.url_map.iter_rules()
        if rule.rule == case['rule'] and rule.endpoint == case['endpoint']
    ]

    assert matches, (
        f"{case['name']}: no se encontró {case['rule']} "
        f"con endpoint {case['endpoint']}."
    )
    assert case['method'] in matches[0].methods, (
        f"{case['name']}: {case['rule']} no acepta {case['method']}."
    )
    assert callable(app.view_functions.get(case['endpoint'])), (
        f"{case['name']}: el endpoint {case['endpoint']} no tiene una vista callable."
    )

    adapter = app.url_map.bind('localhost')
    generated_path = adapter.build(
        case['endpoint'],
        case['values'],
        method=case['method'],
    )
    assert generated_path == case['rule'].replace('<int:user_id>', '1'), (
        f"{case['name']}: url_for generó {generated_path}, "
        f"se esperaba {case['rule']}."
    )

    return case
