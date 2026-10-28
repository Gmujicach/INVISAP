import unittest
from unittest.mock import MagicMock, patch

import pytest

from app import app
from models.model_contratacion import ContratacionModel


@pytest.mark.usefixtures('authenticated_permissions')
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

    def test_registrar_contratacion_reintenta_si_hay_id_duplicado(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        select_calls = [
            (5,),
            (5,),
            (6,),
        ]

        def execute_side_effect(sql, params=None):
            if 'SELECT COALESCE(MAX(id_contratacion)' in sql:
                mock_cursor.fetchone.return_value = select_calls.pop(0)
                return None
            if 'INSERT INTO contratacion' in sql:
                if mock_cursor.execute.call_count == 2:
                    raise type('DuplicateError', (Exception,), {'errno': 1062})(
                        "Duplicate entry '5' for key 'PRIMARY'"
                    )
                return None
            return None

        mock_cursor.execute.side_effect = execute_side_effect
        mock_cursor.fetchone.side_effect = [
            (5,),
            (5,),
            (6,),
        ]

        with patch.object(ContratacionModel, 'obtener_conexion', return_value=mock_conn):
            ok, msg = ContratacionModel().registrar_contrataciones({
                'descripcion': 'Contrato de prueba',
                'empresa_ganadora': 'Empresa S.A.',
                'numero_contrato': 'CTR-002',
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

        self.assertTrue(ok)
        self.assertEqual(msg, 'Contratación registrada correctamente.')

if __name__ == '__main__':
    unittest.main()
