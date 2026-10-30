from tests.smoke.smoke_routes import smoke_module


def test_humo_maquinaria(client):
    smoke_module(client, 'maquinaria')
