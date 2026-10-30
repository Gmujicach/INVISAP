import os

from locust_common import ModuleLoadUser


class PermisosPorRolLoadUser(ModuleLoadUser):
    module_name = 'Permisos por Rol'
    endpoint = (
        '/api/seguridad/permisos/obtener/'
        + os.environ.get('INVISAP_PERF_ID_ROL', '1')
    )
    request_description = 'consulta JSON de permisos asignados a un rol'
