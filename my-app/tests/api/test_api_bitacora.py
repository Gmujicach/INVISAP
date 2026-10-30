from controllers import funciones_bitacora


def test_api_bitacora_aplica_filtros_y_paginacion_y_exige_sesion(
    client,
    api_client,
    monkeypatch,
):
    assert client.get('/api/obtener-bitacora-json').status_code == 401
    llamadas = []

    def filtrar_bitacora(**kwargs):
        llamadas.append(kwargs)
        return {'registros': [{'id': 1}], 'total': 1}

    monkeypatch.setattr(funciones_bitacora, 'filtrar_bitacora', filtrar_bitacora)
    respuesta = api_client.get(
        '/api/obtener-bitacora-json?usuario=ana&modulo=obras&accion=crear&page=2&per_page=5'
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {'registros': [{'id': 1}], 'total': 1}
    assert llamadas == [{
        'usuario': 'ana',
        'modulo': 'obras',
        'accion': 'crear',
        'page': 2,
        'per_page': 5,
    }]
