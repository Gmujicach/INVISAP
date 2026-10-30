from routers import router_home


def test_api_publicaciones_valida_informe_y_retorna_json(monkeypatch, client):
    informes_consultados = []

    class FakePublicacionModel:
        def validar_informe_activo(self, informe_id):
            informes_consultados.append(informe_id)
            return True

    monkeypatch.setattr(router_home, 'PublicacionModel', FakePublicacionModel)
    respuesta = client.get('/api/publicaciones/validar-informe/17')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {'existe': True}
    assert informes_consultados == [17]
