from locust_common import ModuleLoadUser


class AdministracionRespaldosLoadUser(ModuleLoadUser):
    module_name = 'Administración de Respaldos'
    endpoint = '/respaldo/api/listar-json'
    request_description = 'listado JSON de respaldos existentes'
