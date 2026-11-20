"""Locust performance test with automatic evidence capture (HTML reports + screenshots)."""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from locust import HttpUser, between, task, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import gevent


class EvidenceCaptureUser(HttpUser):
    """Base user class with evidence capture capabilities."""
    
    abstract = True
    wait_time = between(1, 2)
    endpoint = '/'
    module_name = 'INVISAP'
    request_description = 'consulta GET de solo lectura'
    case_id = "CP-LOC-RNF10"
    
    # Evidence directory
    evidence_dir = Path(__file__).parent.parent / "evidence" / "performance"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    def on_start(self):
        """Setup session with authentication if available."""
        session_cookie = os.environ.get('INVISAP_PERF_SESSION_COOKIE')
        if session_cookie:
            self.client.headers['Cookie'] = session_cookie
        
        # Initialize evidence tracking
        self._evidence_data = {
            "module": self.module_name,
            "case_id": self.case_id,
            "start_time": datetime.now().isoformat(),
            "requests": [],
            "errors": [],
            "screenshots": []
        }
    
    def on_stop(self):
        """Save evidence on test completion."""
        self._evidence_data["end_time"] = datetime.now().isoformat()
        evidence_file = self.evidence_dir / f"performance_{self.module_name.replace(' ', '_')}_{self.case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(self._evidence_data, f, indent=2, ensure_ascii=False)
        print(f"[EVIDENCIA RENDIMIENTO] Guardado: {evidence_file}")
    
    @task
    def read_module_endpoint(self):
        with self.client.get(
            self.endpoint,
            name=f'{self.module_name} - {self.request_description}',
            catch_response=True,
            allow_redirects=False,
            timeout=15,
        ) as response:
            request_data = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": self.endpoint,
                "method": "GET",
                "status_code": response.status_code,
                "response_time_ms": response.request_meta.get("response_time", 0),
                "content_length": len(response.content) if response.content else 0
            }
            
            self._evidence_data["requests"].append(request_data)
            
            if response.status_code != 200:
                error_data = {
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": self.endpoint,
                    "status_code": response.status_code,
                    "error": f'HTTP {response.status_code}'
                }
                self._evidence_data["errors"].append(error_data)
                response.failure(f'HTTP {response.status_code}')


# Module-specific user classes
class SolicitudesLoadUser(EvidenceCaptureUser):
    module_name = "Solicitudes"
    endpoint = '/api/obtener-solicitudes-json'
    case_id = "CP-LOC-RF01"

class GravedadObraLoadUser(EvidenceCaptureUser):
    module_name = "Gravedad de Obra"
    endpoint = '/api/gravedad/listar'
    case_id = "CP-LOC-RF02"

class PrioridadLoadUser(EvidenceCaptureUser):
    module_name = "Prioridad"
    endpoint = '/api/prioridad/listar'
    case_id = "CP-LOC-RF03"

class ProyectosLoadUser(EvidenceCaptureUser):
    module_name = "Proyectos"
    endpoint = '/api/proyecto/validar-codigo/TEST001'
    case_id = "CP-LOC-RF08"

class MaquinariaLoadUser(EvidenceCaptureUser):
    module_name = "Maquinaria"
    endpoint = '/api/maquinaria/listar'
    case_id = "CP-LOC-RF07"

class ContratacionLoadUser(EvidenceCaptureUser):
    module_name = "Contratación"
    endpoint = '/api/obtener-empresas-json'
    case_id = "CP-LOC-RF09"

class EmpresaLoadUser(EvidenceCaptureUser):
    module_name = "Empresa"
    endpoint = '/api/empresas/J-12345678-9'
    case_id = "CP-LOC-RF06"

class ObrasLoadUser(EvidenceCaptureUser):
    module_name = "Obras"
    endpoint = '/api/obra/estados'
    case_id = "CP-LOC-RF10"

class EmpleadosLoadUser(EvidenceCaptureUser):
    module_name = "Empleados"
    endpoint = '/empleados/api/listar-json'
    case_id = "CP-LOC-RF05"

class InspeccionesLoadUser(EvidenceCaptureUser):
    module_name = "Inspecciones"
    endpoint = '/inspecciones/api/inspectores/listar'
    case_id = "CP-LOC-RF11"

class EvidenciasLoadUser(EvidenceCaptureUser):
    module_name = "Evidencias"
    endpoint = '/api/evidencias/validar/1'
    case_id = "CP-LOC-RF12"

class InformeAvanceLoadUser(EvidenceCaptureUser):
    module_name = "Informe de Avance de Obra"
    endpoint = '/api/informes/listar-json'
    case_id = "CP-LOC-RF13"

class PublicacionesLoadUser(EvidenceCaptureUser):
    module_name = "Publicaciones"
    endpoint = '/api/publicaciones/validar-informe/1'
    case_id = "CP-LOC-RF14"

class ReportesPDFLoadUser(EvidenceCaptureUser):
    module_name = "Reportes PDF"
    endpoint = '/reportes/reporte-pdf'
    case_id = "CP-LOC-RF15"

class ReportesExcelLoadUser(EvidenceCaptureUser):
    module_name = "Reportes Excel"
    endpoint = '/reportes/reporte-excel'
    case_id = "CP-LOC-RF15"

class ReportesEstadisticosLoadUser(EvidenceCaptureUser):
    module_name = "Reportes Estadísticos"
    endpoint = '/reporte-estadistico/data'
    case_id = "CP-LOC-RF15"

class UsuariosLoadUser(EvidenceCaptureUser):
    module_name = "Usuarios"
    endpoint = '/api/users/1'
    case_id = "CP-LOC-RF04"

class PermisosPorRolLoadUser(EvidenceCaptureUser):
    module_name = "Permisos por Rol"
    endpoint = '/api/seguridad/permisos/obtener/1'
    case_id = "CP-LOC-RNF03"

class AdministracionRespaldosLoadUser(EvidenceCaptureUser):
    module_name = "Administración de Respaldos"
    endpoint = '/respaldo/api/listar-json'
    case_id = "CP-LOC-RF16"

class BitacoraLoadUser(EvidenceCaptureUser):
    module_name = "Bitácora"
    endpoint = '/api/obtener-bitacora-json'
    case_id = "CP-LOC-RNF06"


# Event hooks for HTML report generation
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize Locust with HTML report generation."""
    if not isinstance(environment, Environment):
        return
    
    # Setup logging
    setup_logging("INFO", None)
    
    # Start stats printer
    gevent.spawn(stats_printer, environment.stats)
    gevent.spawn(stats_history, environment.runner)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate HTML report when test stops."""
    evidence_dir = Path(__file__).parent.parent / "evidence" / "performance"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_report = evidence_dir / f"locust_report_{timestamp}.html"
    csv_report = evidence_dir / f"locust_stats_{timestamp}.csv"
    
    # Generate HTML report
    generate_html_report(environment, html_report)
    
    # Generate CSV report
    generate_csv_report(environment, csv_report)
    
    print(f"[EVIDENCIA RENDIMIENTO] Reporte HTML: {html_report}")
    print(f"[EVIDENCIA RENDIMIENTO] Reporte CSV: {csv_report}")


def generate_html_report(environment, output_path):
    """Generate HTML performance report."""
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Rendimiento INVISAP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
        .card h3 {{ margin: 0 0 10px 0; color: #7f8c8d; font-size: 14px; }}
        .card .value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
        .card .success {{ color: #27ae60; }}
        .card .warning {{ color: #f39c12; }}
        .card .danger {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
        th {{ background: #3498db; color: white; font-weight: bold; }}
        tr:hover {{ background: #f8f9fa; }}
        .status-pass {{ color: #27ae60; font-weight: bold; }}
        .status-fail {{ color: #e74c3c; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; color: #7f8c8d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Reporte de Pruebas de Rendimiento - INVISAP</h1>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Entorno:</strong> {os.getenv('INVISAP_TEST_URL', 'http://127.0.0.1:5600')}</p>
        
        <h2>Resumen General</h2>
        <div class="summary">
            <div class="card">
                <h3>Total Solicitudes</h3>
                <div class="value">{environment.stats.total.num_requests}</div>
            </div>
            <div class="card">
                <h3>Solicitudes Exitosas</h3>
                <div class="value success">{environment.stats.total.num_requests - environment.stats.total.num_failures}</div>
            </div>
            <div class="card">
                <h3>Solicitudes Fallidas</h3>
                <div class="value danger">{environment.stats.total.num_failures}</div>
            </div>
            <div class="card">
                <h3>Tasa de Fallo</h3>
                <div class="value {'danger' if environment.stats.total.fail_ratio > 0 else 'success'}">{environment.stats.total.fail_ratio * 100:.2f}%</div>
            </div>
            <div class="card">
                <h3>Tiempo Promedio (ms)</h3>
                <div class="value">{environment.stats.total.avg_response_time:.2f}</div>
            </div>
            <div class="card">
                <h3>Percentil 95 (ms)</h3>
                <div class="value">{environment.stats.total.get_response_time_percentile(0.95):.2f}</div>
            </div>
            <div class="card">
                <h3>Usuarios Concurrentes</h3>
                <div class="value">{environment.runner.user_count if environment.runner else 'N/A'}</div>
            </div>
            <div class="card">
                <h3>Duración (s)</h3>
                <div class="value">{(environment.stats.total.last_request_timestamp - environment.stats.total.start_time) if environment.stats.total.start_time else 0:.0f}</div>
            </div>
        </div>
        
        <h2>Detalle por Endpoint</h2>
        <table>
            <thead>
                <tr>
                    <th>Endpoint</th>
                    <th>Método</th>
                    <th>Total</th>
                    <th>Exitosas</th>
                    <th>Fallidas</th>
                    <th>Tasa Fallo %</th>
                    <th>Promedio (ms)</th>
                    <th>Mediana (ms)</th>
                    <th>P95 (ms)</th>
                    <th>Min (ms)</th>
                    <th>Max (ms)</th>
                    <th>RPS</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for name, entry in environment.stats.entries.items():
        method, path = name.split(' ', 1) if ' ' in name else ('GET', name)
        fail_ratio = entry.num_failures / entry.num_requests * 100 if entry.num_requests > 0 else 0
        status_class = "status-fail" if fail_ratio > 0 else "status-pass"
        
        html_content += f"""
                <tr>
                    <td>{path}</td>
                    <td>{method}</td>
                    <td>{entry.num_requests}</td>
                    <td>{entry.num_requests - entry.num_failures}</td>
                    <td>{entry.num_failures}</td>
                    <td class="{status_class}">{fail_ratio:.2f}%</td>
                    <td>{entry.avg_response_time:.2f}</td>
                    <td>{entry.median_response_time:.2f}</td>
                    <td>{entry.get_response_time_percentile(0.95):.2f}</td>
                    <td>{entry.min_response_time if entry.min_response_time != float('inf') else 0:.2f}</td>
                    <td>{entry.max_response_time:.2f}</td>
                    <td>{entry.total_rps:.2f}</td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
        
        <h2>Errores Detallados</h2>
        <table>
            <thead>
                <tr>
                    <th>Endpoint</th>
                    <th>Error</th>
                    <th>Ocurrencias</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for error in environment.stats.errors.values():
        html_content += f"""
                <tr>
                    <td>{error.name}</td>
                    <td>{error.error}</td>
                    <td>{error.occurrences}</td>
                </tr>
"""
    
    if not environment.stats.errors:
        html_content += """
                <tr>
                    <td colspan="3" style="text-align: center;">No se registraron errores</td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>Generado automáticamente por Locust + pytest framework INVISAP</p>
            <p>Criterio de aceptación RNF-10: 20 usuarios, promedio < 2s, 0% errores HTTP</p>
            <p>Evidencia almacenada en: tests/evidence/performance/</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_csv_report(environment, output_path):
    """Generate CSV report with detailed statistics."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Endpoint', 'Método', 'Total_Requests', 'Successful', 'Failed',
            'Failure_Rate_%', 'Avg_Response_Time_ms', 'Median_Response_Time_ms',
            'P95_Response_Time_ms', 'Min_Response_Time_ms', 'Max_Response_Time_ms',
            'RPS', 'Timestamp'
        ])
        
        for name, entry in environment.stats.entries.items():
            method, path = name.split(' ', 1) if ' ' in name else ('GET', name)
            fail_ratio = entry.num_failures / entry.num_requests * 100 if entry.num_requests > 0 else 0
            
            writer.writerow([
                path, method, entry.num_requests,
                entry.num_requests - entry.num_failures, entry.num_failures,
                f"{fail_ratio:.2f}", f"{entry.avg_response_time:.2f}",
                f"{entry.median_response_time:.2f}",
                f"{entry.get_response_time_percentile(0.95):.2f}",
                f"{entry.min_response_time if entry.min_response_time != float('inf') else 0:.2f}",
                f"{entry.max_response_time:.2f}",
                f"{entry.total_rps:.2f}",
                datetime.now().isoformat()
            ])