from locust_common import ModuleLoadUser


class EmpleadosLoadUser(ModuleLoadUser):
    module_name = 'Empleados'
    endpoint = '/empleados/api/listar-json?page=1&per_page=10'
    request_description = 'listado paginado de empleados'
