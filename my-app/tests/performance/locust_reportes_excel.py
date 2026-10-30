from locust_common import ModuleLoadUser


class ReportesExcelLoadUser(ModuleLoadUser):
    module_name = 'Reportes Excel'
    endpoint = '/reportes/reporte-excel'
    request_description = 'carga del formulario de reportes Excel sin exportar'
