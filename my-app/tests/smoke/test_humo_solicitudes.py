from tests.smoke.smoke_routes import smoke_module


def test_humo_solicitudes(client):
    smoke_module(client, 'solicitudes')
