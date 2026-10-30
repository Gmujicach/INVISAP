from locust_common import ModuleLoadUser


class ContratacionLoadUser(ModuleLoadUser):
    module_name = 'Contratación'
    endpoint = '/api/obtener-empresas-json'
    request_description = 'consulta JSON de empresas para contrataciones'
