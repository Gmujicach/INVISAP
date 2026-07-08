import unittest
from unittest.mock import patch

from app import app


class ContratacionesBitacoraTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_registrar_contratacion_audita_la_accion(self):
        with patch('routers.router_home.ContratacionModel') as mock_model_cls, \
             patch('routers.router_home.BitacoraService.registrar_accion') as mock_registrar:
            mock_model = mock_model_cls.return_value
            mock_model.registrar_contrataciones.return_value = (True, 'ok')

            with self.client.session_transaction() as sess:
                sess['conectado'] = True
                sess['name_surname'] = 'Ana Test'

            response = self.client.post('/registrar-contratacion', data={
                'descripcion': 'Contrato de prueba',
                'empresa_ganadora': 'Empresa S.A.',
                'numero_contrato': 'CTR-001',
                'monto': '1000',
                'fecha_inicio_procedimiento': '2024-01-01',
                'fecha_adjudicacion': '2024-01-02',
                'tipo_contrato': 'Contrato de Obra',
                'modalidad': 'Concurso Abierto',
                'objeto': 'Ejecución de Obras',
                'observacion': 'Prueba',
                'fecha_registro': '2024-01-03',
                'empresa_rif': 'J-12345678-9'
            })

            self.assertEqual(response.status_code, 200)
            mock_registrar.assert_called_once()
            args = mock_registrar.call_args[0]
            self.assertEqual(args[1], 'Contrataciones')
            self.assertEqual(args[2], 'CREAR')


if __name__ == '__main__':
    unittest.main()
