from tests.smoke.smoke_routes import smoke_module


def test_humo_bitacora(client):
    smoke_module(client, 'bitacora')
