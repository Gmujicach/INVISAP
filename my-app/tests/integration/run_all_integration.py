from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTEGRATION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.integration.route_contracts import MODULE_ROUTES

def main():
    test_files = [
        INTEGRATION_DIR / f"test_integracion_{module_key}.py"
        for module_key in MODULE_ROUTES
    ]
    missing_files = [path for path in test_files if not path.is_file()]
    if missing_files:
        for path in missing_files:
            print(f"Falta el archivo de integración: {path}")
        return 2

    print(
        f"Escaneando {len(test_files)} módulos — "
        "Tipo: Pruebas de integración Flask (rutas y endpoints).",
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
