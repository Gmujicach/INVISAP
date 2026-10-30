import os

from locust_common import ModuleLoadUser


class EvidenciasLoadUser(ModuleLoadUser):
    module_name = 'Evidencias'
    endpoint = '/api/evidencias/validar/' + os.environ.get('INVISAP_PERF_ID_EVIDENCIA', '1')
    request_description = 'validación de existencia de evidencia'
