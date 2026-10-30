from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SMOKE_DIR = Path(__file__).resolve().parent

MODULE_TESTS = [
    'test_humo_solicitudes.py',
    'test_humo_gravedad_obra.py',
    'test_humo_prioridad.py',
    'test_humo_proyectos.py',
    'test_humo_maquinaria.py',
    'test_humo_contratacion.py',
    'test_humo_empresa.py',
    'test_humo_obras.py',
    'test_humo_empleados.py',
    'test_humo_inspecciones.py',
    'test_humo_evidencias.py',
    'test_humo_informe_avance.py',
    'test_humo_publicaciones.py',
    'test_humo_reportes_pdf.py',
    'test_humo_reportes_excel.py',
    'test_humo_reportes_estadisticos.py',
    'test_humo_usuarios.py',
    'test_humo_permisos_por_rol.py',
    'test_humo_administracion_respaldos.py',
    'test_humo_bitacora.py',
]


def main():
    test_files = [SMOKE_DIR / name for name in MODULE_TESTS]
    missing_files = [path for path in test_files if not path.is_file()]
    if missing_files:
        for path in missing_files:
            print(f"Falta el archivo de prueba de humo: {path}")
        return 2

    print(
        f"Escaneando {len(test_files)} módulos — "
        "Tipo: Pruebas de humo HTTP con Flask.",
        flush=True,
    )
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', *(str(path) for path in test_files)],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
