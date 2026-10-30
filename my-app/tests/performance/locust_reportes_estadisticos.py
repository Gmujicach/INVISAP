from locust_common import ModuleLoadUser


class ReportesEstadisticosLoadUser(ModuleLoadUser):
    module_name = 'Reportes Estadísticos'
    endpoint = '/reporte-estadistico/data?tipo_reporte=solicitudes&agrupacion=dia'
    request_description = 'consulta estadística agrupada por día'
