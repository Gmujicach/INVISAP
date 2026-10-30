from locust_common import ModuleLoadUser


class GravedadObraLoadUser(ModuleLoadUser):
    module_name = 'Gravedad de Obra'
    endpoint = '/api/gravedad/listar'
    request_description = 'listado JSON de gravedades'
