"""
Tests unitarios para la parametrización de los reportes Excel y PDF.

Verifica que los filtros enviados en el formulario se propaguen correctamente
a las funciones de los modelos y que el filtrado por módulo funcione.
"""
import unittest
from unittest.mock import patch, MagicMock

from app import app


class ReportesParametrizacionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        with self.client.session_transaction() as sess:
            sess['conectado'] = True
            sess['name_surname'] = 'Test User'

    def _fake_data_modulo(self, modulo):
        if modulo == 'solicitudes':
            return [{
                'id_solicitudes': 1, 'fecha': '01/01/2024', 'tipo_solicitud': 'X',
                'estatus_solicitud': 'P', 'problematica': 'p', 'cedula': '12345',
                'prioridad': 'Alta'
            }]
        if modulo == 'obras':
            return [{
                'id_obra': 1, 'nombre_obra': 'Obra X', 'ubicacion_obra': 'Y',
                'porcentaje_avance_obra': 50, 'semaforo': 'Verde', 'color': 'green',
                'contratista': 'Z'
            }]
        return [{'nombre': 'A', 'apellido': 'B', 'cedula': '1'}]


class ReportesExcelTestCase(ReportesParametrizacionTestCase):
    def test_solicitudes_con_filtro_cedula(self):
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_solicitudes_reporte.return_value = self._fake_data_modulo('solicitudes')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={
                'modulo': 'solicitudes',
                'cedula': '12345',
            })
            self.assertEqual(resp.status_code, 200)
            mock_model.obtener_solicitudes_reporte.assert_called_once_with({'cedula': '12345'})

    def test_solicitudes_con_multiples_filtros(self):
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_solicitudes_reporte.return_value = self._fake_data_modulo('solicitudes')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={
                'modulo': 'solicitudes',
                'cedula': '12345',
                'tipo_solicitud': 'Comunidad',
                'estatus_solicitud': 'Pendiente',
                'fecha_desde': '2024-01-01',
                'fecha_hasta': '2024-12-31',
                'municipio': 'Iribarren',
                'sector': 'Centro',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_solicitudes_reporte.call_args[0][0]
            self.assertEqual(call_args.get('cedula'), '12345')
            self.assertEqual(call_args.get('tipo_solicitud'), 'Comunidad')
            self.assertEqual(call_args.get('estatus_solicitud'), 'Pendiente')
            self.assertEqual(call_args.get('fecha_desde'), '2024-01-01')
            self.assertEqual(call_args.get('fecha_hasta'), '2024-12-31')
            self.assertEqual(call_args.get('municipio'), 'Iribarren')
            self.assertEqual(call_args.get('sector'), 'Centro')

    def test_obras_con_filtro_titulo(self):
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_obras_reporte.return_value = self._fake_data_modulo('obras')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={
                'modulo': 'obras',
                'titulo_obra': 'Obra X',
                'semaforo_estado': 'Verde',
                'contratista': 'ACME',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_obras_reporte.call_args[0][0]
            self.assertEqual(call_args.get('titulo_obra'), 'Obra X')
            self.assertEqual(call_args.get('semaforo_estado'), 'Verde')
            self.assertEqual(call_args.get('contratista'), 'ACME')

    def test_obras_ignora_filtros_comunes_no_aplicables(self):
        """Filtros como cedula del bloque Comunes no deben aplicarse a obras."""
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_obras_reporte.return_value = self._fake_data_modulo('obras')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={
                'modulo': 'obras',
                'titulo_obra': 'Obra X',
                'cedula': '99999',
                'nombre_solicitante': 'Juan',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_obras_reporte.call_args[0][0]
            self.assertNotIn('cedula', call_args)
            self.assertNotIn('nombre_solicitante', call_args)
            self.assertEqual(call_args.get('titulo_obra'), 'Obra X')

    def test_empleados_con_filtro_cargo_y_fechas(self):
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_empleados_reporte.return_value = [{
                'nombre_empleado': 'A', 'profesion_empleado': 'B', 'gerencia_asignada': 'C',
                'fecha_ingreso': '01/01/2024', 'email_empleado': 'a@b.com',
                'telefono_empleado': '1234', 'estado_empleado': 'Activo'
            }]
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={
                'modulo': 'empleados',
                'cargo': 'Inspector',
                'fecha_ingreso_desde': '2024-01-01',
                'fecha_ingreso_hasta': '2024-12-31',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_empleados_reporte.call_args[0][0]
            self.assertEqual(call_args.get('cargo'), 'Inspector')
            self.assertEqual(call_args.get('fecha_ingreso_desde'), '2024-01-01')
            self.assertEqual(call_args.get('fecha_ingreso_hasta'), '2024-12-31')

    def test_contrataciones_con_filtros_multiples_fechas(self):
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_contrataciones_reporte.return_value = [{
                'nombre_empresa': 'ACME', 'rif_empresa': 'J-123', 'numero_contrato': 'C-1',
                'monto': 1000, 'descripcion': 'D', 'observacion': 'O', 'tipo_contrato': 'Obra',
                'modalidad': 'Abierto', 'objeto': 'Construccion',
                'fecha_registro': '01/01/2024', 'fecha_inicio': '02/01/2024', 'fecha_adjudicacion': '03/01/2024'
            }]
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={
                'modulo': 'contrataciones',
                'empresa_ganadora': 'ACME',
                'fecha_registro_desde': '2024-01-01',
                'fecha_registro_hasta': '2024-12-31',
                'fecha_adjudicacion_desde': '2024-06-01',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_contrataciones_reporte.call_args[0][0]
            self.assertEqual(call_args.get('empresa_ganadora'), 'ACME')
            self.assertEqual(call_args.get('fecha_registro_desde'), '2024-01-01')
            self.assertEqual(call_args.get('fecha_registro_hasta'), '2024-12-31')
            self.assertEqual(call_args.get('fecha_adjudicacion_desde'), '2024-06-01')

    def test_sin_filtros_genera_reporte_general(self):
        with patch('controllers.controller_reportesExcel.modelo_reporte') as mock_model:
            mock_model.obtener_solicitudes_reporte.return_value = self._fake_data_modulo('solicitudes')
            mock_model.obtener_empleados_reporte.return_value = [{'nombre_empleado': 'A'}]
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-excel', data={'modulo': 'general'})
            self.assertEqual(resp.status_code, 200)
            mock_model.obtener_solicitudes_reporte.assert_called_once_with(None)
            mock_model.obtener_empleados_reporte.assert_called_once_with(None)


class ReportesPDFTestCase(ReportesParametrizacionTestCase):
    def test_solicitudes_con_filtro_cedula(self):
        with patch('controllers.controller_reportesPDF.modelo_reporte') as mock_model:
            mock_model.obtener_solicitudes.return_value = self._fake_data_modulo('solicitudes')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-pdf', data={
                'modulo': 'solicitudes',
                'cedula': '12345',
            })
            self.assertEqual(resp.status_code, 200)
            mock_model.obtener_solicitudes.assert_called_once_with({'cedula': '12345'})

    def test_obras_con_filtro_titulo(self):
        with patch('controllers.controller_reportesPDF.modelo_reporte') as mock_model:
            mock_model.obtener_obras.return_value = self._fake_data_modulo('obras')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-pdf', data={
                'modulo': 'obras',
                'titulo_obra': 'Obra X',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_obras.call_args[0][0]
            self.assertEqual(call_args.get('titulo_obra'), 'Obra X')

    def test_obras_ignora_filtros_comunes_no_aplicables(self):
        with patch('controllers.controller_reportesPDF.modelo_reporte') as mock_model:
            mock_model.obtener_obras.return_value = self._fake_data_modulo('obras')
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-pdf', data={
                'modulo': 'obras',
                'titulo_obra': 'Obra X',
                'cedula': '99999',
                'nombre_solicitante': 'Juan',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_obras.call_args[0][0]
            self.assertNotIn('cedula', call_args)
            self.assertNotIn('nombre_solicitante', call_args)

    def test_empleados_con_filtro_cargo(self):
        with patch('controllers.controller_reportesPDF.modelo_reporte') as mock_model:
            mock_model.obtener_empleados.return_value = [{'nombre_empleado': 'A'}]
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-pdf', data={
                'modulo': 'empleados',
                'cargo': 'Inspector',
                'estado_empleado': '1',
            })
            self.assertEqual(resp.status_code, 200)
            call_args = mock_model.obtener_empleados.call_args[0][0]
            self.assertEqual(call_args.get('cargo'), 'Inspector')
            self.assertEqual(call_args.get('estado_empleado'), '1')

    def test_sin_filtros_genera_pdf_general(self):
        with patch('controllers.controller_reportesPDF.modelo_reporte') as mock_model:
            mock_model.obtener_solicitudes.return_value = self._fake_data_modulo('solicitudes')
            mock_model.obtener_empleados.return_value = [{'nombre_empleado': 'A'}]
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-pdf', data={'modulo': 'general'})
            self.assertEqual(resp.status_code, 200)
            mock_model.obtener_solicitudes.assert_called_once_with(None)
            mock_model.obtener_empleados.assert_called_once_with(None)

    def test_sin_datos_retorna_redirect(self):
        with patch('controllers.controller_reportesPDF.modelo_reporte') as mock_model:
            mock_model.obtener_solicitudes.return_value = []
            mock_model.obtener_publicaciones_reporte.return_value = []
            resp = self.client.post('/reporte-pdf', data={'modulo': 'solicitudes'})
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/reporte-pdf', resp.headers.get('Location', ''))


if __name__ == '__main__':
    unittest.main()
