from tests.smoke.smoke_routes import smoke_module


def test_humo_obras(client):
    smoke_module(client, 'obras')
