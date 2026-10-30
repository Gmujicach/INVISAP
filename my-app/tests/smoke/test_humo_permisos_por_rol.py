from tests.smoke.smoke_routes import smoke_module


def test_humo_permisos_por_rol(client):
    smoke_module(client, 'permisos_por_rol')
