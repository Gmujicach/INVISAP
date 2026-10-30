from locust_common import ModuleLoadUser


class ObrasLoadUser(ModuleLoadUser):
    module_name = 'Obras'
    endpoint = '/api/obra/estados'
    request_description = 'consulta JSON de estados de obra'
