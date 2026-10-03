import unittest
from unittest.mock import MagicMock, patch

from models.model_informe_avance import InformeAvanceModel


class InformeValidacionTestCase(unittest.TestCase):
    def setUp(self):
        self.modelo = InformeAvanceModel.__new__(InformeAvanceModel)

    def test_rechaza_gerente_inactivo_antes_de_crear_avance(self):
        with patch.object(
            self.modelo,
            '_InformeAvanceModel__validar_gerente_activo_db',
            return_value=False,
        ), patch.object(self.modelo, '_InformeAvanceModel__crear_avance_db') as crear_avance:
            with self.assertRaisesRegex(ValueError, 'no existe, está inactivo'):
                self.modelo.registrar_informe({'gerente_responsable_id': '27'})

        crear_avance.assert_not_called()

    def test_consulta_solo_gerentes_o_inspectores_activos(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.return_value = (27,)

        with patch('conexion.base_conexion.BaseConexionBD.obtener_conexion', return_value=conexion):
            valido = self.modelo.validar_gerente_activo('27')

        self.assertTrue(valido)
        cursor.execute.assert_called_once_with(
            'SELECT id_empleados FROM empleados '
            'WHERE id_empleados = %s AND estado = 1 AND cargo IN (%s, %s)',
            (27, 'Gerente', 'Inspector'),
        )
        cursor.close.assert_called_once()
        conexion.close.assert_called_once()

    def test_rechaza_identificador_no_numerico_sin_consultar_bd(self):
        with patch('conexion.base_conexion.BaseConexionBD.obtener_conexion') as conectar:
            self.assertFalse(self.modelo.validar_gerente_activo('no-es-un-id'))

        conectar.assert_not_called()


if __name__ == '__main__':
    unittest.main()