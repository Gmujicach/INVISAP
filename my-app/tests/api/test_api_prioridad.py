from routers import router_home


def test_api_prioridad_propaga_paginacion_y_filtros(client, api_client, monkeypatch):
    assert client.get('/api/prioridad/listar').status_code == 401

    llamadas = {}

    def listar_priorizadas(**kwargs):
        llamadas.update(kwargs)
        return [{'id': 3, 'rango': 1}], 1

    monkeypatch.setattr(
        router_home.PrioridadModel,
        'listar_priorizadas',
        listar_priorizadas,
    )
    respuesta = api_client.get(
        '/api/prioridad/listar?page=2&per_page=5&q=escuela&riesgo=alto&orden=rango_desc'
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        'data': [{'id': 3, 'rango': 1}],
        'total': 1,
        'page': 2,
        'per_page': 5,
    }
    assert llamadas == {
        'page': 2,
        'per_page': 5,
        'q': 'escuela',
        'riesgo': 'ALTO',
        'orden': 'rango_desc',
    }
