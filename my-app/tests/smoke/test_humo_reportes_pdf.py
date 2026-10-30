from tests.smoke.smoke_routes import smoke_module


def test_humo_reportes_pdf(client):
    smoke_module(client, 'reportes_pdf')
