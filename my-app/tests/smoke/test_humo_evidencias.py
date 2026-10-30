from tests.smoke.smoke_routes import smoke_module


def test_humo_evidencias(client):
    smoke_module(client, 'evidencias')
