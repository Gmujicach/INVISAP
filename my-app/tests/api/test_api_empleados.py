from controllers import controller_empleado


def test_api_empleados_lista_paginada_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/empleados/api/listar-json').status_code == 401

    class FakeEmpleadoModel:
        def obtener_empleados_paginados(self, page, per_page):
            assert (page, per_page) == (3, 5)
            return [{'id_empleado': 8, 'nombre': 'Ana'}]

        def contar_empleados(self):
            return 11

    monkeypatch.setattr(controller_empleado, 'EmpleadoModel', FakeEmpleadoModel)
    respuesta = api_client.get('/empleados/api/listar-json?page=3&per_page=5')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        'status': 'success',
        'empleados': [{'id_empleado': 8, 'nombre': 'Ana'}],
        'page': 3,
        'per_page': 5,
        'total_empleados': 11,
        'total_pages': 3,
    }
