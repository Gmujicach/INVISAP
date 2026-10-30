from tests.smoke.smoke_routes import smoke_module


def test_humo_contratacion(client):
    smoke_module(client, 'contratacion')
