from locust_common import ModuleLoadUser


class ReportesPdfLoadUser(ModuleLoadUser):
    module_name = 'Reportes PDF'
    endpoint = '/reportes/reporte-pdf'
    request_description = 'carga del formulario de reportes PDF sin exportar'
