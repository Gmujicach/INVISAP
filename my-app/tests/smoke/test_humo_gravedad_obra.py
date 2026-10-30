from tests.smoke.smoke_routes import smoke_module


def test_humo_gravedad_obra(client):
    smoke_module(client, 'gravedad_obra')
