import os

from locust_common import ModuleLoadUser


class ProyectosLoadUser(ModuleLoadUser):
    module_name = 'Proyectos'
    endpoint = (
        '/api/proyecto/validar-codigo/'
        + os.environ.get('INVISAP_PERF_CODIGO_PROYECTO', 'PERF-TEST')
    )
    request_description = 'validación de código de proyecto'
