import os

from locust_common import ModuleLoadUser


class EmpresaLoadUser(ModuleLoadUser):
    module_name = 'Empresa'
    endpoint = '/api/empresas/' + os.environ.get('INVISAP_PERF_EMPRESA_RIF', 'J-00000000-0')
    request_description = 'consulta de empresa por RIF'
