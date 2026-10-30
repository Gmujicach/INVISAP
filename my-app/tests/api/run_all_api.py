"""Ejecuta los contratos HTTP de backend/API de los 20 módulos."""

import subprocess
import sys
from pathlib import Path


API_TEST_FILES = [
    'test_api_solicitudes.py',
    'test_api_gravedad_obra.py',
    'test_api_prioridad.py',
    'test_api_proyectos.py',
    'test_api_maquinaria.py',
    'test_api_contratacion.py',
    'test_api_empresa.py',
    'test_api_obras.py',
    'test_api_empleados.py',
    'test_api_inspecciones.py',
    'test_api_evidencias.py',
    'test_api_informe_avance.py',
    'test_api_publicaciones.py',
    'test_api_reportes_pdf.py',
    'test_api_reportes_excel.py',
    'test_api_reportes_estadisticos.py',
    'test_api_usuarios.py',
    'test_api_permisos_por_rol.py',
    'test_api_administracion_respaldos.py',
    'test_api_bitacora.py',
]


def main():
    tests_dir = Path(__file__).resolve().parent
    missing = [name for name in API_TEST_FILES if not (tests_dir / name).is_file()]
    if missing:
        print('Faltan archivos de pruebas backend/API:')
        for filename in missing:
            print(f'  - {filename}')
        return 2

    project_dir = tests_dir.parents[1]
    test_paths = [str(tests_dir / filename) for filename in API_TEST_FILES]
    test_paths.append(str(tests_dir / 'test_parametrizacion_reportes.py'))
    print('Ejecutando pruebas de backend/API para los 20 módulos de INVISAP...')
    return subprocess.run(
        [sys.executable, '-m', 'pytest', '-v', '-s', *test_paths],
        cwd=project_dir,
        check=False,
    ).returncode


if __name__ == '__main__':
    raise SystemExit(main())
