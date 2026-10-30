from controllers import controller_reportesEstadistico


def test_api_reportes_estadisticos_aplica_filtros_y_agrupacion(
    client,
    api_client,
    monkeypatch,
):
    assert client.get('/reporte-estadistico/data').status_code == 401
    llamadas = []

    def obtener_stats(tipo_reporte, filtros, agrupacion):
        llamadas.append((tipo_reporte, filtros, agrupacion))
        return {'solicitudes': [{'label': 'Abiertas', 'valor': 2}]}

    monkeypatch.setattr(
        controller_reportesEstadistico,
        '_obtener_stats_por_tipo',
        obtener_stats,
    )
    respuesta = api_client.get(
        '/reporte-estadistico/data?tipo_reporte=solicitudes&agrupacion=mes&cedula=12345'
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        'solicitudes': [{'label': 'Abiertas', 'valor': 2}],
    }
    assert llamadas == [('solicitudes', {'cedula': '12345'}, 'mes')]
