from tests.smoke.smoke_routes import smoke_module


def test_humo_usuarios(client):
    # INICIO DE MOCK: Llamar smoke_module para prueba de humo de usuarios
    smoke_module(client, 'usuarios')
    # FIN DE MOCK: No hay aserciones explícitas, smoke_module las maneja internamente
