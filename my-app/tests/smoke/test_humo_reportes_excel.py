from tests.smoke.smoke_routes import smoke_module


def test_humo_reportes_excel(client):
    smoke_module(client, 'reportes_excel')
