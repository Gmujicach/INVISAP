from locust_common import ModuleLoadUser


class MaquinariaLoadUser(ModuleLoadUser):
    module_name = 'Maquinaria'
    endpoint = '/api/maquinaria/listar?page=1&per_page=10'
    request_description = 'listado paginado de maquinaria'
