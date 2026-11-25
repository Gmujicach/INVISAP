from tests.smoke.smoke_routes import smoke_module


def test_humo_solicitudes(client):
    # INICIO DE MOCK: Llamar smoke_module para prueba de humo de solicitudes
    smoke_module(client, 'solicitudes')
    # FIN DE MOCK: No hay aserciones explícitas, smoke_module las maneja internamente
