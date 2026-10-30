from tests.smoke.smoke_routes import smoke_module


def test_humo_administracion_respaldos(client):
    smoke_module(client, 'administracion_respaldos')
