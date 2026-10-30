from controllers import controller_reportesExcel


def test_api_reportes_excel_requiere_sesion_y_rechaza_modulo_desconocido(
    client,
    api_client,
    monkeypatch,
):
    sin_sesion = client.post('/reporte-excel', data={'modulo': 'no-existe'})
    assert sin_sesion.status_code == 302

    monkeypatch.setattr(controller_reportesExcel, 'construir_modulos_config_excel', lambda: [])
    respuesta = api_client.post('/reporte-excel', data={'modulo': 'no-existe'})

    assert respuesta.status_code == 302
    assert respuesta.headers['Location'].endswith('/reporte-excel')
