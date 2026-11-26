import os

from locust_common import ModuleLoadUser


class NotificacionesLoadUser(ModuleLoadUser):
    module_name = 'Notificaciones'
    endpoint = '/notificaciones/lista'
    request_description = 'consulta de lista de notificaciones'
"""