from tests.smoke.smoke_routes import smoke_module


def test_humo_empresa(client):
    smoke_module(client, 'empresa')
