import os

from locust_common import ModuleLoadUser


class UsuariosLoadUser(ModuleLoadUser):
    module_name = 'Usuarios'
    endpoint = '/api/users/' + os.environ.get('INVISAP_PERF_ID_USUARIO', '1')
    request_description = 'consulta de detalle de usuario'
