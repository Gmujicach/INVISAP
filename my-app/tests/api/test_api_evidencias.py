from controllers import controller_evidencia


def test_api_evidencias_valida_existencia_por_identificador(monkeypatch, client):
    ids_consultados = []

    class FakeEvidenciaModel:
        def validar_evidencia_activa(self, evidencia_id):
            ids_consultados.append(evidencia_id)
            return evidencia_id == 12

    monkeypatch.setattr(controller_evidencia, 'EvidenciaModel', FakeEvidenciaModel)
    respuesta = client.get('/api/evidencias/validar/12')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {'existe': True, 'id': 12}
    assert ids_consultados == [12]
