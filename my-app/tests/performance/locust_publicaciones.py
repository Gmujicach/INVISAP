import os

from locust_common import ModuleLoadUser


class PublicacionesLoadUser(ModuleLoadUser):
    module_name = 'Publicaciones'
    endpoint = (
        '/api/publicaciones/validar-informe/'
        + os.environ.get('INVISAP_PERF_ID_INFORME', '1')
    )
    request_description = 'validación de informe para publicación'
