"""Evidence organizer utility for INVISAP - Organizes screenshots and evidence files 
based on traceability matrix IDs (Matriz_Trazabilidad_Pruebas_INVISAP)."""

import os
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TraceabilityEntry:
    """Entry from the traceability matrix."""
    requirement_id: str
    requirement: str
    case_ids: str
    test_type: str
    procedure: str
    expected_result: str
    case_id_list: List[str]


class TraceabilityMatrixParser:
    """Parse the traceability matrix DOCX to extract case ID mappings."""
    
    def __init__(self, matrix_path: str):
        self.matrix_path = Path(matrix_path)
        self.entries: List[TraceabilityEntry] = []
        self.case_id_to_info: Dict[str, Dict] = {}
    
    def parse(self) -> List[TraceabilityEntry]:
        """Parse the traceability matrix from DOCX."""
        try:
            from docx import Document
        except ImportError:
            print("[ERROR] python-docx no instalado. Ejecute: pip install python-docx")
            return self._load_fallback_mapping()
        
        if not self.matrix_path.exists():
            print(f"[WARNING] Matriz no encontrada: {self.matrix_path}")
            return self._load_fallback_mapping()
        
        doc = Document(str(self.matrix_path))
        
        for table in doc.tables:
            for row_idx, row in enumerate(table.rows):
                if row_idx == 0:  # Skip header
                    continue
                
                cells = [cell.text.strip() for cell in row.cells]
                if len(cells) >= 6:
                    req_id = cells[0]
                    req_desc = cells[1]
                    case_ids_text = cells[2]
                    test_type = cells[3]
                    procedure = cells[4]
                    expected = cells[5]
                    
                    # Parse case IDs (they can be ranges like CP-UNI-RF01-01..43)
                    case_ids = self._parse_case_ids(case_ids_text)
                    
                    entry = TraceabilityEntry(
                        requirement_id=req_id,
                        requirement=req_desc,
                        case_ids=case_ids_text,
                        test_type=test_type,
                        procedure=procedure,
                        expected_result=expected,
                        case_id_list=case_ids
                    )
                    self.entries.append(entry)
                    
                    # Build reverse mapping
                    for case_id in case_ids:
                        self.case_id_to_info[case_id] = {
                            "requirement_id": req_id,
                            "requirement": req_desc,
                            "test_type": test_type,
                            "module": self._extract_module_from_req(req_id, req_desc)
                        }
        
        return self.entries
    
    def _parse_case_ids(self, case_ids_text: str) -> List[str]:
        """Parse case IDs text into list, handling ranges."""
        case_ids = []
        
        # Split by newlines and commas
        parts = re.split(r'[\n,;]+', case_ids_text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Handle ranges like CP-UNI-RF01-01..43
            range_match = re.match(r'(.+)-(\d+)\.\.(\d+)', part)
            if range_match:
                prefix = range_match.group(1)
                start = int(range_match.group(2))
                end = int(range_match.group(3))
                for i in range(start, end + 1):
                    case_ids.append(f"{prefix}-{i:02d}")
            else:
                case_ids.append(part)
        
        return case_ids
    
    def _extract_module_from_req(self, req_id: str, req_desc: str) -> str:
        """Extract module name from requirement."""
        # Module mapping based on requirement IDs
        module_map = {
            "RF-01": "Solicitudes",
            "RF-02": "Gravedad de Obra",
            "RF-03": "Prioridad",
            "RF-04": "Usuarios",
            "RF-05": "Empleados",
            "RF-06": "Empresa",
            "RF-07": "Maquinaria",
            "RF-08": "Proyectos",
            "RF-09": "Contratación",
            "RF-10": "Obras",
            "RF-11": "Inspecciones",
            "RF-12": "Evidencias",
            "RF-13": "Informe de Avance de Obra",
            "RF-14": "Publicaciones",
            "RF-15": "Reportes",
            "RF-16": "Administración de Respaldos",
            "RF-17": "Notificaciones",
            "RF-18": "Panel Principal",
            "RF-19": "Perfil de Usuario",
            "RF-20": "Manual de Usuario",
            "RNF-01": "Autenticación",
            "RNF-02": "Ciclo de Cuentas",
            "RNF-03": "Autorización",
            "RNF-04": "Protección de Claves",
            "RNF-05": "Validación Entradas",
            "RNF-06": "Bitácora",
            "RNF-07": "Navegabilidad",
            "RNF-08": "Usabilidad",
            "RNF-09": "Adaptabilidad",
            "RNF-10": "Rendimiento",
            "RNF-11": "Escalabilidad",
            "RNF-12": "Fiabilidad",
            "RNF-13": "Disponibilidad",
            "RNF-14": "Mantenibilidad",
            "RNF-15": "Integridad Respaldos",
            "RNF-16": "Aislamiento Módulos",
            "RNF-17": "Respuestas Error",
            "RNF-18": "Portabilidad",
        }
        
        for key, module in module_map.items():
            if key in req_id:
                return module
        
        return "General"
    
    def _load_fallback_mapping(self) -> List[TraceabilityEntry]:
        """Load fallback mapping from generate_traceability_matrix.py."""
        # This is the mapping from the generator script
        fallback_entries = [
            ("RF-01", "Solicitudes", "CP-UNI-RF01-01..43\nCP-INT-RF01-01\nCP-API-RF01-01\nCP-POST-RF01-01\nCP-HUM-RF01-01"),
            ("RF-02", "Gravedad de Obra", "CP-UNI-RF02-01..11\nCP-INT-RF02-01\nCP-API-RF02-01\nCP-POST-RF02-01\nCP-HUM-RF02-01"),
            ("RF-03", "Prioridad", "CP-UNI-RF03-01..31\nCP-INT-RF03-01\nCP-API-RF03-01\nCP-POST-RF03-01\nCP-HUM-RF03-01"),
            ("RF-04", "Usuarios", "CP-UNI-RF04-01..19\nCP-INT-RF04-01\nCP-API-RF04-01\nCP-POST-RF04-01\nCP-HUM-RF04-01"),
            ("RF-05", "Empleados", "CP-UNI-RF05-01..14\nCP-INT-RF05-01\nCP-API-RF05-01\nCP-POST-RF05-01\nCP-HUM-RF05-01"),
            ("RF-06", "Empresa", "CP-UNI-RF06-01..09\nCP-INT-RF06-01\nCP-API-RF06-01\nCP-POST-RF06-01\nCP-HUM-RF06-01"),
            ("RF-07", "Maquinaria", "CP-UNI-RF07-01..20\nCP-INT-RF07-01\nCP-API-RF07-01\nCP-POST-RF07-01\nCP-HUM-RF07-01"),
            ("RF-08", "Proyectos", "CP-UNI-RF08-01..22\nCP-INT-RF08-01\nCP-API-RF08-01\nCP-POST-RF08-01\nCP-HUM-RF08-01"),
            ("RF-09", "Contratación", "CP-UNI-RF09-01..20\nCP-INT-RF09-01..03\nCP-API-RF09-01\nCP-POST-RF09-01\nCP-HUM-RF09-01"),
            ("RF-10", "Obras", "CP-UNI-RF10-01..14\nCP-INT-RF10-01\nCP-API-RF10-01\nCP-POST-RF10-01\nCP-HUM-RF10-01"),
            ("RF-11", "Inspecciones", "CP-UNI-RF11-01..18\nCP-INT-RF11-01\nCP-API-RF11-01\nCP-POST-RF11-01\nCP-HUM-RF11-01"),
            ("RF-12", "Evidencias", "CP-UNI-RF12-01..13\nCP-INT-RF12-01\nCP-API-RF12-01\nCP-POST-RF12-01\nCP-HUM-RF12-01"),
            ("RF-13", "Informe de Avance", "CP-UNI-RF13-01..21\nCP-INT-RF13-01\nCP-API-RF13-01\nCP-POST-RF13-01\nCP-HUM-RF13-01"),
            ("RF-14", "Publicaciones", "CP-UNI-RF14-01..14\nCP-INT-RF14-01\nCP-API-RF14-01\nCP-POST-RF14-01\nCP-HUM-RF14-01"),
            ("RF-15", "Reportes", "CP-UNI-RF15-01..46\nCP-INT-RF15-01..03\nCP-API-RF15-01..16\nCP-POST-RF15-01..03\nCP-HUM-RF15-01..03"),
            ("RF-16", "Respaldos", "CP-UNI-RF16-01..26\nCP-INT-RF16-01\nCP-API-RF16-01\nCP-POST-RF16-01\nCP-HUM-RF16-01"),
            ("RNF-01", "Autenticación", "CP-UNI-RNF01-01..02\nCP-HUM-RNF01-01\nCP-UI-RNF01-01"),
            ("RNF-03", "Autorización", "CP-UNI-RNF03-01..02\nCP-INT-RNF03-01\nCP-API-RNF03-01\nCP-HUM-RNF03-01"),
            ("RNF-05", "Validación Entradas", "CP-UNI-RNF05-01..39"),
            ("RNF-06", "Bitácora", "CP-UNI-RNF06-01..02\nCP-INT-RNF06-01..02\nCP-API-RNF06-01\nCP-HUM-RNF06-01"),
            ("RNF-10", "Rendimiento", "CP-LOC-RNF10-01"),
        ]
        
        for req_id, req_desc, case_ids_text in fallback_entries:
            case_ids = self._parse_case_ids(case_ids_text)
            entry = TraceabilityEntry(
                requirement_id=req_id,
                requirement=req_desc,
                case_ids=case_ids_text,
                test_type="Múltiple",
                procedure="",
                expected_result="",
                case_id_list=case_ids
            )
            self.entries.append(entry)
            
            for case_id in case_ids:
                self.case_id_to_info[case_id] = {
                    "requirement_id": req_id,
                    "requirement": req_desc,
                    "test_type": self._infer_test_type(case_id),
                    "module": req_desc
                }
        
        return self.entries
    
    def _infer_test_type(self, case_id: str) -> str:
        """Infer test type from case ID prefix."""
        if case_id.startswith("CP-UNI-"):
            return "unit"
        elif case_id.startswith("CP-INT-"):
            return "integration"
        elif case_id.startswith("CP-API-"):
            return "api"
        elif case_id.startswith("CP-POST-"):
            return "postman"
        elif case_id.startswith("CP-HUM-"):
            return "smoke"
        elif case_id.startswith("CP-UI-"):
            return "ui"
        elif case_id.startswith("CP-LOC-"):
            return "performance"
        elif case_id.startswith("CP-PEND-"):
            return "pending"
        return "unknown"


class EvidenceOrganizer:
    """Organize evidence files based on traceability matrix."""
    
    def __init__(self, evidence_base_dir: str, matrix_path: str = None):
        self.evidence_base_dir = Path(evidence_base_dir)
        self.matrix_parser = TraceabilityMatrixParser(matrix_path) if matrix_path else None
        self.organized_dir = self.evidence_base_dir / "organized"
        self.organized_dir.mkdir(parents=True, exist_ok=True)
        
        if self.matrix_parser:
            self.matrix_parser.parse()
    
    def organize_all(self, dry_run: bool = False) -> Dict:
        """Organize all evidence files into traceability-based structure."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "organized": {},
            "unmatched": [],
            "errors": []
        }
        
        # Scan all evidence directories
        for test_type_dir in self.evidence_base_dir.iterdir():
            if not test_type_dir.is_dir() or test_type_dir.name == "organized":
                continue
            
            test_type = test_type_dir.name
            results["organized"][test_type] = {}
            
            for evidence_file in test_type_dir.rglob("*.png"):
                try:
                    organized = self._organize_file(evidence_file, test_type, dry_run)
                    if organized:
                        key = f"{organized['traceability_id']}_{organized['module']}"
                        if key not in results["organized"][test_type]:
                            results["organized"][test_type][key] = []
                        results["organized"][test_type][key].append(organized)
                    else:
                        results["unmatched"].append(str(evidence_file))
                except Exception as e:
                    results["errors"].append({
                        "file": str(evidence_file),
                        "error": str(e)
                    })
            
            # Also check for JSON evidence files
            for evidence_file in test_type_dir.rglob("*.json"):
                if evidence_file.name.startswith("evidence_") or evidence_file.name == "evidence_summary.json":
                    continue
                try:
                    organized = self._organize_file(evidence_file, test_type, dry_run)
                    if organized:
                        key = f"{organized['traceability_id']}_{organized['module']}"
                        if key not in results["organized"][test_type]:
                            results["organized"][test_type][key] = []
                        results["organized"][test_type][key].append(organized)
                    else:
                        results["unmatched"].append(str(evidence_file))
                except Exception as e:
                    results["errors"].append({
                        "file": str(evidence_file),
                        "error": str(e)
                    })
        
        # Save organization report
        report_path = self.organized_dir / f"organization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"[EVIDENCIA] Reporte de organización: {report_path}")
        print(f"  Archivos organizados: {sum(len(v) for t in results['organized'].values() for v in t.values())}")
        print(f"  Archivos sin coincidencia: {len(results['unmatched'])}")
        print(f"  Errores: {len(results['errors'])}")
        
        return results
    
    def _organize_file(self, file_path: Path, test_type: str, dry_run: bool) -> Optional[Dict]:
        """Organize a single evidence file based on traceability."""
        filename = file_path.name
        
        # Try to extract case ID from filename
        case_id = self._extract_case_id_from_filename(filename)
        
        if not case_id and self.matrix_parser:
            # Try to infer from directory structure
            case_id = self._infer_case_id_from_path(file_path, test_type)
        
        if case_id and case_id in self.matrix_parser.case_id_to_info:
            info = self.matrix_parser.case_id_to_info[case_id]
            traceability_id = case_id
            module = info.get("module", "Unknown")
            requirement_id = info.get("requirement_id", "")
        else:
            # Generate from filename pattern
            traceability_id, module = self._generate_ids_from_filename(filename, test_type)
            requirement_id = ""
        
        # Clean module name for directory
        clean_module = re.sub(r'[^\w\s-]', '', module).strip().replace(' ', '_')
        clean_trace = traceability_id.replace('/', '-').replace('..', '_')
        
        # Target directory: organized/test_type/module/
        target_dir = self.organized_dir / test_type / clean_module
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Target filename: traceability_id_originalname
        target_name = f"{clean_trace}_{filename}"
        target_path = target_dir / target_name
        
        if not dry_run:
            # Copy file to organized location
            shutil.copy2(file_path, target_path)
        
        return {
            "source": str(file_path),
            "target": str(target_path),
            "traceability_id": traceability_id,
            "module": module,
            "requirement_id": requirement_id,
            "test_type": test_type,
            "original_name": filename,
            "organized_name": target_name
        }
    
    def _extract_case_id_from_filename(self, filename: str) -> Optional[str]:
        """Extract case ID from filename pattern."""
        # Pattern: tipoPrueba_modulo_IDcaso_...
        patterns = [
            r'(CP-[A-Z]+-[A-Z]+?\d+[\-_]?\d*)',  # CP-UNI-RF01-01
            r'(CP-PEND-[A-Z]+?\d+[\-_]?\d*)',
            r'(CP-LOC-[A-Z]+?\d+[\-_]?\d*)',
            r'(CP-UI-[A-Z]+?\d+[\-_]?\d*)',
            r'(CP-POST-[A-Z]+?\d+[\-_]?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return None
    
    def _infer_case_id_from_path(self, file_path: Path, test_type: str) -> Optional[str]:
        """Infer case ID from directory path."""
        path_str = str(file_path).lower()
        
        # Map directory names to requirement IDs
        dir_to_req = {
            "solicitudes": "RF-01",
            "gravedad": "RF-02",
            "prioridad": "RF-03",
            "usuarios": "RF-04",
            "empleados": "RF-05",
            "empresa": "RF-06",
            "maquinaria": "RF-07",
            "proyectos": "RF-08",
            "contratacion": "RF-09",
            "obras": "RF-10",
            "inspecciones": "RF-11",
            "evidencias": "RF-12",
            "informe_avance": "RF-13",
            "publicaciones": "RF-14",
            "reportes_pdf": "RF-15",
            "reportes_excel": "RF-15",
            "reportes_estadisticos": "RF-15",
            "respaldos": "RF-16",
            "bitacora": "RNF-06",
            "permisos": "RNF-03",
            "seguridad": "RNF-01",
            "login": "RNF-01",
        }
        
        type_prefix_map = {
            "unit": "CP-UNI",
            "integration": "CP-INT",
            "api": "CP-API",
            "smoke": "CP-HUM",
            "ui": "CP-UI",
            "performance": "CP-LOC",
            "postman": "CP-POST",
        }
        
        prefix = type_prefix_map.get(test_type, "CP-UNK")
        
        for dir_key, req_id in dir_to_req.items():
            if dir_key in path_str:
                # Find matching case IDs in matrix
                for case_id in self.matrix_parser.case_id_to_info:
                    if case_id.startswith(f"{prefix}-{req_id}"):
                        return case_id
                
                # Generate generic
                return f"{prefix}-{req_id}-01"
        
        return None
    
    def _generate_ids_from_filename(self, filename: str, test_type: str) -> Tuple[str, str]:
        """Generate traceability ID and module from filename."""
        # Remove extension
        name = filename.replace('.png', '').replace('.json', '')
        
        # Split by underscores
        parts = name.split('_')
        
        if len(parts) >= 3:
            # Format: testtype_module_caseid_...
            test_type_part = parts[0]
            module_part = parts[1]
            case_part = parts[2]
            
            # Try to reconstruct case ID
            if case_part.startswith("CP-"):
                traceability_id = case_part
            else:
                type_prefix = {
                    "unit": "CP-UNI",
                    "integration": "CP-INT",
                    "api": "CP-API",
                    "smoke": "CP-HUM",
                    "ui": "CP-UI",
                    "performance": "CP-LOC",
                }.get(test_type, "CP-UNK")
                traceability_id = f"{type_prefix}-{case_part}"
            
            module = module_part.replace('_', ' ').title()
            return traceability_id, module
        
        # Fallback
        return f"CP-UNK-{name[:20]}", "Unknown"
    
    def generate_traceability_report(self) -> Dict:
        """Generate a report mapping evidence to traceability matrix."""
        if not self.matrix_parser:
            self.matrix_parser = TraceabilityMatrixParser("")
            self.matrix_parser.parse()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "traceability_matrix": "Matriz_Trazabilidad_Pruebas_INVISAP.docx",
            "evidence_base_dir": str(self.evidence_base_dir),
            "coverage": {}
        }
        
        # Check each case ID in matrix for evidence
        for case_id, info in self.matrix_parser.case_id_to_info.items():
            req_id = info.get("requirement_id", "")
            module = info.get("module", "")
            test_type = info.get("test_type", "")
            
            key = f"{req_id}_{case_id}"
            
            # Look for evidence files
            evidence_files = []
            if test_type:
                type_dir = self.evidence_base_dir / test_type
                if type_dir.exists():
                    for ext in ['*.png', '*.json', '*.html']:
                        evidence_files.extend(list(type_dir.rglob(ext)))
            
            # Filter files related to this case_id
            case_evidence = [f for f in evidence_files if case_id in f.name]
            
            report["coverage"][key] = {
                "requirement_id": req_id,
                "case_id": case_id,
                "module": module,
                "test_type": test_type,
                "evidence_count": len(case_evidence),
                "evidence_files": [str(f.relative_to(self.evidence_base_dir)) for f in case_evidence],
                "has_evidence": len(case_evidence) > 0
            }
        
        # Save report
        report_path = self.organized_dir / f"traceability_coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[EVIDENCIA] Reporte de cobertura de trazabilidad: {report_path}")
        
        # Summary
        total = len(report["coverage"])
        with_evidence = sum(1 for v in report["coverage"].values() if v["has_evidence"])
        print(f"  Total casos en matriz: {total}")
        print(f"  Con evidencia: {with_evidence} ({with_evidence/total*100:.1f}%)")
        print(f"  Sin evidencia: {total - with_evidence}")
        
        return report


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize INVISAP test evidence by traceability matrix")
    parser.add_argument("--evidence-dir", default="tests/evidence", help="Base evidence directory")
    parser.add_argument("--matrix", help="Path to traceability matrix DOCX")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without copying files")
    parser.add_argument("--report-only", action="store_true", help="Only generate coverage report")
    
    args = parser.parse_args()
    
    organizer = EvidenceOrganizer(args.evidence_dir, args.matrix)
    
    if args.report_only:
        organizer.generate_traceability_report()
    else:
        organizer.organize_all(dry_run=args.dry_run)
        organizer.generate_traceability_report()


if __name__ == "__main__":
    main()