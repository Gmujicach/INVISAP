from routers import router_home


def test_api_maquinaria_propaga_paginacion_y_devuelve_json(client, api_client, monkeypatch):
    assert client.get('/api/maquinaria/listar').status_code == 401
    llamadas = []
    monkeypatch.setattr(
        router_home,
        'listar_maquinarias_controller',
        lambda page, per_page: llamadas.append((page, per_page)) or [{'id': 4}],
    )
    monkeypatch.setattr(router_home, 'contar_maquinarias_controller', lambda: 21)

    respuesta = api_client.get('/api/maquinaria/listar?page=2&per_page=10')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        'success': True,
        'data': [{'id': 4}],
        'total': 21,
        'page': 2,
        'total_pages': 3,
    }
    assert llamadas == [(2, 10)]
