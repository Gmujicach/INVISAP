from routers import router_home


def test_api_permisos_rol_verifica_sesion_permiso_y_consulta(
    client,
    api_client,
    monkeypatch,
):
    assert client.get('/api/seguridad/permisos/obtener/4').status_code == 401
    llamadas = []
    monkeypatch.setattr(router_home, 'verificar_permiso', lambda permiso: True)
    monkeypatch.setattr(
        router_home,
        'obtener_permisos_rol_controller',
        lambda rol_id: llamadas.append(rol_id) or [{'modulo': 'obras'}],
    )

    respuesta = api_client.get('/api/seguridad/permisos/obtener/4')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == [{'modulo': 'obras'}]
    assert llamadas == [4]
