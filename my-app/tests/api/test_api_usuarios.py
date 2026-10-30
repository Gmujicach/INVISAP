from controllers import UserController


def test_api_usuarios_controla_sesion_permiso_y_usuario_inexistente(
    client,
    api_client,
    monkeypatch,
):
    assert client.get('/api/users/9').status_code == 401
    monkeypatch.setattr(UserController.user_model, 'buscar_por_id', lambda user_id: None)

    respuesta = api_client.get('/api/users/9')

    assert respuesta.status_code == 404
    assert respuesta.get_json() == {
        'ok': False,
        'mensaje': 'El usuario no existe.',
    }
