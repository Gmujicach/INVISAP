"""Postman/Newman integration with automated evidence capture for INVISAP."""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PostmanEvidenceCapture:
    """Capture and organize Postman test evidence with traceability matrix naming."""
    
    def __init__(self, collection_path: str, environment_path: str = None):
        self.collection_path = Path(collection_path)
        self.environment_path = Path(environment_path) if environment_path else None
        self.evidence_dir = Path(__file__).parent.parent / "evidence" / "api"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Traceability mapping for Postman collections
        self.traceability_map = {
            "solicitudes": ("api", "Solicitudes", "CP-POST-RF01"),
            "gravedad_obra": ("api", "Gravedad de Obra", "CP-POST-RF02"),
            "prioridad": ("api", "Prioridad", "CP-POST-RF03"),
            "proyectos": ("api", "Proyectos", "CP-POST-RF08"),
            "maquinaria": ("api", "Maquinaria", "CP-POST-RF07"),
            "contratacion": ("api", "Contratación", "CP-POST-RF09"),
            "empresa": ("api", "Empresa", "CP-POST-RF06"),
            "obras": ("api", "Obras", "CP-POST-RF10"),
            "empleados": ("api", "Empleados", "CP-POST-RF05"),
            "inspecciones": ("api", "Inspecciones", "CP-POST-RF11"),
            "evidencias": ("api", "Evidencias", "CP-POST-RF12"),
            "informe_avance": ("api", "Informe de Avance", "CP-POST-RF13"),
            "publicaciones": ("api", "Publicaciones", "CP-POST-RF14"),
            "reportes_pdf": ("api", "Reportes PDF", "CP-POST-RF15"),
            "reportes_excel": ("api", "Reportes Excel", "CP-POST-RF15"),
            "reportes_estadisticos": ("api", "Reportes Estadísticos", "CP-POST-RF15"),
            "usuarios": ("api", "Usuarios", "CP-POST-RF04"),
            "permisos_por_rol": ("api", "Permisos por Rol", "CP-POST-RNF03"),
            "administracion_respaldos": ("api", "Respaldos", "CP-POST-RF16"),
            "bitacora": ("api", "Bitácora", "CP-POST-RNF06"),
            "login": ("api", "Autenticación", "CP-POST-RNF01"),
            "negative_no_session": ("api", "Acceso Sin Sesión", "CP-POST-NEG-01"),
        }
    
    def run_collection(self, 
                       iteration_count: int = 1,
                       delay_request: int = 100,
                       globals_file: str = None,
                       extra_args: List[str] = None) -> Dict:
        """Run Postman collection with Newman and capture evidence."""
        
        # Prepare output files
        output_dir = self.evidence_dir / f"postman_run_{self.timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cli_report = output_dir / "cli_report.txt"
        json_report = output_dir / "newman_report.json"
        htmlextra_report_dir = output_dir / "htmlextra"
        
        # Build Newman command
        cmd = [
            "newman", "run", str(self.collection_path),
            "--reporters", "cli,json,htmlextra",
            "--reporter-cli-no-failures", "false",
            "--reporter-cli-no-assertions", "false",
            "--reporter-json-export", str(json_report),
            "--reporter-htmlextra-export", str(htmlextra_report_dir),
            "--reporter-htmlextra-title", f"INVISAP Postman Evidence - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "--reporter-htmlextra-logs", "true",
            "--reporter-htmlextra-test-paging", "true",
            "--iteration-count", str(iteration_count),
            "--delay-request", str(delay_request),
            "--bail", "false",
            "--suppress-exit-code",
        ]
        
        if self.environment_path and self.environment_path.exists():
            cmd.extend(["--environment", str(self.environment_path)])
        
        if globals_file and Path(globals_file).exists():
            cmd.extend(["--globals", globals_file])
        
        if extra_args:
            cmd.extend(extra_args)
        
        print(f"[POSTMAN] Ejecutando colección: {self.collection_path}")
        print(f"[POSTMAN] Directorio de evidencia: {output_dir}")
        
        # Run Newman
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=output_dir.parent
            )
            
            # Save CLI output
            with open(cli_report, 'w', encoding='utf-8') as f:
                f.write(f"Comando: {' '.join(cmd)}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Exit Code: {result.returncode}\n\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\n\nSTDERR:\n")
                f.write(result.stderr)
            
            # Parse JSON report for evidence
            evidence = self._parse_newman_report(json_report, output_dir)
            
            # Generate structured evidence summary
            self._generate_evidence_summary(evidence, output_dir)
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "output_dir": str(output_dir),
                "cli_report": str(cli_report),
                "json_report": str(json_report),
                "htmlextra_report": str(htmlextra_report_dir / "index.html"),
                "evidence_summary": evidence
            }
            
        except subprocess.TimeoutExpired:
            error_msg = "Timeout ejecutando colección Postman (5 min)"
            print(f"[POSTMAN ERROR] {error_msg}")
            return {"success": False, "error": error_msg}
        except FileNotFoundError:
            error_msg = "Newman no encontrado. Instale con: npm install -g newman newman-reporter-htmlextra"
            print(f"[POSTMAN ERROR] {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error ejecutando Postman: {str(e)}"
            print(f"[POSTMAN ERROR] {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _parse_newman_report(self, json_report_path: Path, output_dir: Path) -> Dict:
        """Parse Newman JSON report and extract evidence per traceability ID."""
        if not json_report_path.exists():
            return {"error": "JSON report not found"}
        
        with open(json_report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        evidence = {
            "timestamp": datetime.now().isoformat(),
            "collection": report.get("collection", {}).get("name", "Unknown"),
            "total_requests": len(report.get("run", {}).get("executions", [])),
            "failed_requests": 0,
            "passed_requests": 0,
            "by_case_id": {},
            "executions": []
        }
        
        for execution in report.get("run", {}).get("executions", []):
            request = execution.get("request", {})
            response = execution.get("response", {})
            assertions = execution.get("assertions", [])
            
            # Determine test case ID from request name/url
            request_name = request.get("name", "").lower()
            case_id = self._map_request_to_case_id(request_name)
            
            exec_data = {
                "request_name": request.get("name"),
                "request_method": request.get("method"),
                "request_url": request.get("url", {}).get("raw", "") if isinstance(request.get("url"), dict) else str(request.get("url", "")),
                "response_code": response.get("code"),
                "response_status": response.get("status"),
                "response_time_ms": response.get("responseTime"),
                "assertions": [
                    {
                        "assertion": a.get("assertion"),
                        "passed": a.get("passed"),
                        "error": a.get("error", {}).get("message") if a.get("error") else None
                    }
                    for a in assertions
                ],
                "case_id": case_id,
                "passed": all(a.get("passed", False) for a in assertions) if assertions else response.get("code") == 200
            }
            
            evidence["executions"].append(exec_data)
            
            if exec_data["passed"]:
                evidence["passed_requests"] += 1
            else:
                evidence["failed_requests"] += 1
            
            # Group by case ID
            if case_id not in evidence["by_case_id"]:
                test_type, module, trace_id = self.traceability_map.get(
                    case_id.replace("CP-POST-", "").lower(), 
                    ("api", case_id, case_id)
                )
                evidence["by_case_id"][case_id] = {
                    "case_id": case_id,
                    "traceability_id": trace_id,
                    "module": module,
                    "test_type": test_type,
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "requests": []
                }
            
            evidence["by_case_id"][case_id]["total"] += 1
            evidence["by_case_id"][case_id]["requests"].append(exec_data)
            if exec_data["passed"]:
                evidence["by_case_id"][case_id]["passed"] += 1
            else:
                evidence["by_case_id"][case_id]["failed"] += 1
        
        return evidence
    
    def _map_request_to_case_id(self, request_name: str) -> str:
        """Map Postman request name to traceability case ID."""
        request_lower = request_name.lower().replace(" ", "_")
        
        for key, (_, _, case_id) in self.traceability_map.items():
            if key in request_lower or request_lower in key:
                return case_id
        
        # Fallback: generate from request name
        return f"CP-POST-{request_lower.upper()[:20]}"
    
    def _generate_evidence_summary(self, evidence: Dict, output_dir: Path):
        """Generate structured evidence summary with traceability matrix naming."""
        summary = {
            "metadata": {
                "project": "INVISAP",
                "system": "Sistema de Gestión e Información para el Seguimiento y Control de Solicitudes",
                "evidence_type": "Postman API Contract Testing",
                "timestamp": evidence["timestamp"],
                "collection": evidence["collection"],
                "traceability_matrix": "Matriz_Trazabilidad_Pruebas_INVISAP.docx"
            },
            "summary": {
                "total_requests": evidence["total_requests"],
                "passed": evidence["passed_requests"],
                "failed": evidence["failed_requests"],
                "success_rate": f"{(evidence['passed_requests'] / evidence['total_requests'] * 100) if evidence['total_requests'] > 0 else 0:.2f}%"
            },
            "by_traceability_id": {}
        }
        
        for case_id, data in evidence.get("by_case_id", {}).items():
            trace_id = data.get("traceability_id", case_id)
            module = data.get("module", "Unknown")
            test_type = data.get("test_type", "api")
            
            # Generate filename following convention: tipoPrueba_modulo_IDcaso
            clean_module = module.replace(" ", "_").replace("ó", "o").replace("á", "a")
            evidence_filename = f"{test_type}_{clean_module}_{trace_id}_postman_{self.timestamp}.json"
            evidence_filepath = output_dir / evidence_filename
            
            # Save individual evidence file
            case_evidence = {
                "traceability_id": trace_id,
                "module": module,
                "test_type": test_type,
                "case_id": case_id,
                "total_requests": data["total"],
                "passed": data["passed"],
                "failed": data["failed"],
                "success_rate": f"{(data['passed'] / data['total'] * 100) if data['total'] > 0 else 0:.2f}%",
                "requests": data["requests"]
            }
            
            with open(evidence_filepath, 'w', encoding='utf-8') as f:
                json.dump(case_evidence, f, indent=2, ensure_ascii=False)
            
            summary["by_traceability_id"][trace_id] = {
                "case_id": case_id,
                "module": module,
                "test_type": test_type,
                "evidence_file": evidence_filename,
                "total": data["total"],
                "passed": data["passed"],
                "failed": data["failed"],
                "status": "APROBADO" if data["failed"] == 0 else "REVISAR"
            }
        
        # Save master summary
        summary_path = output_dir / f"postman_evidence_summary_{self.timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"[POSTMAN EVIDENCE] Resumen guardado: {summary_path}")
        for trace_id, data in summary["by_traceability_id"].items():
            print(f"  {trace_id} ({data['module']}): {data['passed']}/{data['total']} - {data['status']}")


def run_postman_evidence_capture(
    collection_path: str = None,
    environment_path: str = None,
    base_url: str = "http://127.0.0.1:5600"
) -> Dict:
    """Convenience function to run Postman evidence capture."""
    
    # Default collection path
    if collection_path is None:
        collection_path = str(Path(__file__).parent.parent.parent / "postman" / "collections" / "INVISAP - Pruebas de Contrato HTTP.postman_collection.json")
    
    # Default environment path
    if environment_path is None:
        environment_path = str(Path(__file__).parent.parent.parent / "postman" / "environments" / "INVISAP - Local.postman_environment.json")
    
    # Update environment with current base_url if it exists
    if Path(environment_path).exists():
        with open(environment_path, 'r', encoding='utf-8') as f:
            env_data = json.load(f)
        
        # Update baseUrl in environment
        for value in env_data.get("values", []):
            if value.get("key") == "baseUrl":
                value["value"] = base_url
                break
        
        # Save updated environment
        updated_env_path = Path(environment_path).parent / f"INVISAP - Local - Updated {datetime.now().strftime('%Y%m%d_%H%M%S')}.postman_environment.json"
        with open(updated_env_path, 'w', encoding='utf-8') as f:
            json.dump(env_data, f, indent=2)
        
        environment_path = str(updated_env_path)
    
    # Run capture
    capture = PostmanEvidenceCapture(collection_path, environment_path)
    return capture.run_collection()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Postman collection with evidence capture")
    parser.add_argument("--collection", help="Path to Postman collection JSON")
    parser.add_argument("--environment", help="Path to Postman environment JSON")
    parser.add_argument("--base-url", default="http://127.0.0.1:5600", help="Base URL for API")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations")
    
    args = parser.parse_args()
    
    result = run_postman_evidence_capture(
        collection_path=args.collection,
        environment_path=args.environment,
        base_url=args.base_url
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))