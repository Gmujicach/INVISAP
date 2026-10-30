from locust_common import ModuleLoadUser


class PrioridadLoadUser(ModuleLoadUser):
    module_name = 'Prioridad'
    endpoint = '/api/prioridad/listar?page=1&per_page=10&riesgo=ALL&orden=rango_asc'
    request_description = 'consulta paginada y ordenada de prioridades'
