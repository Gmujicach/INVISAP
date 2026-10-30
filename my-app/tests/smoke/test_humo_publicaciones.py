from tests.smoke.smoke_routes import smoke_module


def test_humo_publicaciones(client):
    smoke_module(client, 'publicaciones')
