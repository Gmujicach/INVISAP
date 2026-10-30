from tests.smoke.smoke_routes import smoke_module


def test_humo_proyectos(client):
    smoke_module(client, 'proyectos')
