from models.model_respaldo import RespaldoModel


def test_limpia_nombre_de_archivo_de_respaldo():
    assert RespaldoModel._limpiar_nombre('copia de bd!.sql') == 'copia_de_bd__sql'


def test_formatea_tamano_de_respaldo():
    assert RespaldoModel._formatear_tamano(1024) == '1.0 KB'
    assert RespaldoModel._formatear_tamano(1048576) == '1.0 MB'
