from models.model_evidencia import EvidenciaModel


def test_validadores_de_archivo_y_url():
    evidencia = EvidenciaModel.__new__(EvidenciaModel)

    assert evidencia._validar_nombre_archivo('obra_01.jpg') is True
    assert evidencia._validar_url('uploads/obra_01.jpg') is True


def test_url_no_permite_traversal_de_directorios():
    evidencia = EvidenciaModel.__new__(EvidenciaModel)

    assert evidencia._validar_url('../secreto.jpg') is False
