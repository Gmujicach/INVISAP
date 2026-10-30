from controllers import controller_inspeccion


def test_api_inspecciones_lista_inspectores_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/inspecciones/api/inspectores/listar').status_code == 401
    inspectores = [{'id_empleado': 4, 'nombre': 'Luis'}]

    class FakeInspeccionModel:
        def obtener_inspectores(self):
            return inspectores

    monkeypatch.setattr(controller_inspeccion, 'InspeccionModel', FakeInspeccionModel)
    respuesta = api_client.get('/inspecciones/api/inspectores/listar')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == inspectores
