from controllers import controller_informe_avance


def test_api_informes_lista_json_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/api/informes/listar-json').status_code == 401
    informes = [{'id_informe': 6, 'porcentaje_avance': 45}]

    class FakeInformeAvanceModel:
        def obtener_todos_informes(self):
            return informes

    monkeypatch.setattr(
        controller_informe_avance,
        'InformeAvanceModel',
        FakeInformeAvanceModel,
    )
    respuesta = api_client.get('/api/informes/listar-json')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == informes
