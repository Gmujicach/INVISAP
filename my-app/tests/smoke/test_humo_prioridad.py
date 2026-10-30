from tests.smoke.smoke_routes import smoke_module


def test_humo_prioridad(client):
    smoke_module(client, 'prioridad')
