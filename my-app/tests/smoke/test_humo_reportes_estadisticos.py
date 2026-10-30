from tests.smoke.smoke_routes import smoke_module


def test_humo_reportes_estadisticos(client):
    smoke_module(client, 'reportes_estadisticos')
