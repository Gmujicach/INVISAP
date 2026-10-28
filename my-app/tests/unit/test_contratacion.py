from unittest.mock import patch

from models.model_contratacion import ContratacionModel


def test_registro_rechaza_datos_incompletos_sin_conectar_base_de_datos():
    modelo = ContratacionModel()

    with patch.object(modelo, 'obtener_conexion') as obtener_conexion:
        registrado, mensaje = modelo.registrar_contrataciones({})

    assert registrado is False
    assert 'obligatorio' in mensaje
    obtener_conexion.assert_not_called()


def test_valida_datos_completos_de_contratacion():
    modelo = ContratacionModel()
    datos = {
        'empresa_ganadora': 'Empresa S.A.',
        'empresa_rif': 'J-12345678-9',
        'descripcion': 'Mantenimiento vial',
        'numero_contrato': 'CTR-001',
        'monto': '1000',
        'tipo_contrato': 'Contrato de Obra',
        'modalidad': 'Concurso Abierto',
        'objeto': 'Ejecución de Obras',
        'fecha_inicio_procedimiento': '2024-01-01',
        'fecha_adjudicacion': '2024-01-02',
        'fecha_registro': '2024-01-03',
    }

    assert modelo._ContratacionModel__validar_datos(datos) == (True, 'Validación exitosa')
