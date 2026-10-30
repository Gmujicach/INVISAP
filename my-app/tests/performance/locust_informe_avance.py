from locust_common import ModuleLoadUser


class InformeAvanceLoadUser(ModuleLoadUser):
    module_name = 'Informe de Avance de Obra'
    endpoint = '/api/informes/listar-json'
    request_description = 'listado JSON de informes de avance'
