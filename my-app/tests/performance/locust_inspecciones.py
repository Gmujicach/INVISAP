from locust_common import ModuleLoadUser


class InspeccionesLoadUser(ModuleLoadUser):
    module_name = 'Inspecciones'
    endpoint = '/inspecciones/api/inspectores/listar'
    request_description = 'consulta de inspectores disponibles'
