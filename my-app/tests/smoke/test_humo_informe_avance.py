from tests.smoke.smoke_routes import smoke_module


def test_humo_informe_avance(client):
    smoke_module(client, 'informe_avance')
