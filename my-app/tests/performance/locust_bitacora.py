from locust_common import ModuleLoadUser


class BitacoraLoadUser(ModuleLoadUser):
    module_name = 'Bitácora'
    endpoint = '/api/obtener-bitacora-json?page=1&per_page=10'
    request_description = 'consulta paginada de bitácora'
