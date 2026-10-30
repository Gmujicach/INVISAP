SMOKE_ROUTES = {
    'solicitudes': {
        'name': 'Solicitudes',
        'path': '/lista-de-solicitudes',
        'description': 'respuesta HTTP del listado de solicitudes',
    },
    'gravedad_obra': {
        'name': 'Gravedad de Obra',
        'path': '/gestionar-gravedad',
        'description': 'respuesta HTTP de la pantalla de gravedad de obra',
    },
    'prioridad': {
        'name': 'Prioridad',
        'path': '/gestionar-prioridad',
        'description': 'respuesta HTTP de la pantalla de prioridad',
    },
    'proyectos': {
        'name': 'Proyectos',
        'path': '/gestionar-proyectos',
        'description': 'respuesta HTTP de la pantalla de proyectos',
    },
    'maquinaria': {
        'name': 'Maquinaria',
        'path': '/maquinaria',
        'description': 'respuesta HTTP de la pantalla de maquinaria',
    },
    'contratacion': {
        'name': 'Contratación',
        'path': '/contrataciones',
        'description': 'respuesta HTTP del listado de contrataciones',
    },
    'empresa': {
        'name': 'Empresa',
        'path': '/lista-empresas',
        'description': 'respuesta HTTP del listado de empresas',
    },
    'obras': {
        'name': 'Obras',
        'path': '/gestionar-obras',
        'description': 'respuesta HTTP de la pantalla de obras',
    },
    'empleados': {
        'name': 'Empleados',
        'path': '/empleados/',
        'description': 'respuesta HTTP del listado de empleados',
    },
    'inspecciones': {
        'name': 'Inspecciones',
        'path': '/inspecciones/',
        'description': 'respuesta HTTP del listado de inspecciones',
    },
    'evidencias': {
        'name': 'Evidencias',
        'path': '/evidencias/listar',
        'description': 'respuesta HTTP del listado de evidencias',
    },
    'informe_avance': {
        'name': 'Informe de Avance de Obra',
        'path': '/inf_avance_obra',
        'description': 'respuesta HTTP del listado de informes de avance',
    },
    'publicaciones': {
        'name': 'Publicaciones',
        'path': '/lista-publicaciones',
        'description': 'respuesta HTTP del listado de publicaciones',
    },
    'reportes_pdf': {
        'name': 'Reportes PDF',
        'path': '/reportes/reporte-pdf',
        'description': 'respuesta HTTP de la pantalla de reportes PDF',
    },
    'reportes_excel': {
        'name': 'Reportes Excel',
        'path': '/reportes/reporte-excel',
        'description': 'respuesta HTTP de la pantalla de reportes Excel',
    },
    'reportes_estadisticos': {
        'name': 'Reportes Estadísticos',
        'path': '/reportes/reporte-estadistico',
        'description': 'respuesta HTTP de la pantalla de reportes estadísticos',
    },
    'usuarios': {
        'name': 'Usuarios',
        'path': '/users',
        'description': 'respuesta HTTP del listado de usuarios',
    },
    'permisos_por_rol': {
        'name': 'Permisos por Rol',
        'path': '/gestionar-permisos',
        'description': 'respuesta HTTP de la pantalla de permisos por rol',
    },
    'administracion_respaldos': {
        'name': 'Administración de Respaldos',
        'path': '/respaldo/',
        'description': 'respuesta HTTP del listado de respaldos',
    },
    'bitacora': {
        'name': 'Bitácora',
        'path': '/bitacora',
        'description': 'respuesta HTTP de la pantalla de bitácora',
    },
}


def smoke_module(client, module_key):
    case = SMOKE_ROUTES[module_key]
    response = client.get(case['path'], follow_redirects=False)
    content_type = response.headers.get('Content-Type', 'no especificado')

    print(
        f"Solicitud GET {case['path']} -> HTTP {response.status_code}; "
        f"Content-Type: {content_type}.",
        flush=True,
    )
    assert response.status_code not in (404, 500), (
        f"{case['name']}: GET {case['path']} devolvió HTTP "
        f"{response.status_code}; se esperaba una ruta existente sin error interno."
    )
    return response
