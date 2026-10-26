from models.model_bitacora import BitacoraModel


def test_bitacora_acepta_texto_y_usuario_validos():
    assert BitacoraModel._es_texto_valido('Solicitud registrada') is True
    assert BitacoraModel._es_usuario_valido('Ana Pérez') is True


def test_bitacora_rechaza_caracteres_no_permitidos():
    assert BitacoraModel._es_texto_valido('<script>') is False
    assert BitacoraModel._es_usuario_valido('usuario@ejemplo.com') is False
