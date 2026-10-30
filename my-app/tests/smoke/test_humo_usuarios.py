from tests.smoke.smoke_routes import smoke_module


def test_humo_usuarios(client):
    smoke_module(client, 'usuarios')
