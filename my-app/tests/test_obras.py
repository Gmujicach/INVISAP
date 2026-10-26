from models.model_obra import ObraModel


def test_valida_texto_y_numero_de_contrato():
    assert ObraModel._es_texto_valido('Reparación de vía') is True
    assert ObraModel._es_numero_contrato_valido('CTR-001/2025') is True


def test_rechaza_texto_o_numero_de_contrato_con_caracteres_invalidos():
    assert ObraModel._es_texto_valido('<script>') is False
    assert ObraModel._es_numero_contrato_valido('CTR;DROP') is False


def test_fecha_fin_no_puede_ser_anterior_a_fecha_inicio():
    assert ObraModel._validar_fechas('2025-02-01', '2025-01-31') is False
    assert ObraModel._validar_fechas('2025-01-01', '2025-02-01') is True
