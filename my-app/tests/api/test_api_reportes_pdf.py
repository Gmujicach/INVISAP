from controllers import controller_reportesPDF


def test_api_reportes_pdf_requiere_sesion_y_rechaza_modulo_desconocido(
    client,
    api_client,
    monkeypatch,
):
    sin_sesion = client.post('/reporte-pdf', data={'modulo': 'no-existe'})
    assert sin_sesion.status_code == 302

    monkeypatch.setattr(controller_reportesPDF, 'construir_modulos_config', lambda: [])
    respuesta = api_client.post('/reporte-pdf', data={'modulo': 'no-existe'})

    assert respuesta.status_code == 302
    assert respuesta.headers['Location'].endswith('/reporte-pdf')
