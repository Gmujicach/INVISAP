from tests.smoke.smoke_routes import smoke_module


def test_humo_empleados(client):
    smoke_module(client, 'empleados')
