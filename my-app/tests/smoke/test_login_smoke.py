from app import app


def test_pagina_de_acceso_responde_sin_error_de_servidor():
    response = app.test_client().get('/login')

    assert response.status_code == 200
    assert 'Primero debes iniciar sesión.' not in response.get_data(as_text=True)
