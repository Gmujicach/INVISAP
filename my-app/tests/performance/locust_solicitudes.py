from locust_common import ModuleLoadUser


class SolicitudesLoadUser(ModuleLoadUser):
    module_name = 'Solicitudes'
    endpoint = '/api/obtener-solicitudes-json'
    request_description = 'listado JSON de solicitudes'
