"""Verify that unit-test coverage entered each active model method."""
import ast
import os
from pathlib import Path

from coverage import Coverage, CoverageData


ROOT = Path(__file__).resolve().parents[2]
MODEL_FILES = (
    'base_model.py',
    'model_solicitudes.py',
    'model_gravedad.py',
    'model_prioridad.py',
    'model_proyecto.py',
    'model_maquinaria.py',
    'model_contratacion.py',
    'model_empresas.py',
    'model_obra.py',
    'model_empleados.py',
    'model_inspeccion.py',
    'model_evidencia.py',
    'model_informe_avance.py',
    'model_publicacion.py',
    'model_publicaciones.py',
    'model_ReporteEstadistico.py',
    'model_reportesExcel.py',
    'model_reportesPDF.py',
    'model_usuarios.py',
    'model_seguridad.py',
    'model_respaldo.py',
    'model_bitacora.py',
)


def _is_property_setter(method):
    for decorator in method.decorator_list:
        if (
            isinstance(decorator, ast.Attribute)
            and decorator.attr == 'setter'
            and isinstance(decorator.value, ast.Name)
            and decorator.value.id == method.name
        ):
            return True
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == 'setter'
            and isinstance(decorator.func.value, ast.Name)
            and decorator.func.value.id == method.name
        ):
            return True
    return False


def _is_property_getter(method):
    return any(
        isinstance(decorator, ast.Name) and decorator.id == 'property'
        for decorator in method.decorator_list
    )


def _active_methods(class_node):
    methods_by_name = {}
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods_by_name.setdefault(node.name, []).append(node)

    active = []
    for methods in methods_by_name.values():
        setters = [method for method in methods if _is_property_setter(method)]
        if setters:
            active.extend(
                method for method in methods
                if _is_property_getter(method) or _is_property_setter(method)
            )
        else:
            active.append(methods[-1])
    return active


def _first_executable_line(method):
    body = method.body
    first_value = body[0].value if body and isinstance(body[0], ast.Expr) else None
    docstring = (
        first_value is not None
        and isinstance(first_value, ast.Constant)
        and isinstance(getattr(first_value, 'value', None), str)
    )
    if (
        docstring
    ):
        body = body[1:]
    return body[0].lineno if body else method.lineno


def main():
    coverage_path = ROOT / '.coverage'
    if not coverage_path.exists():
        raise SystemExit(
            'No existe .coverage. Ejecuta primero '
            'python -m pytest tests\\unit --cov=models --cov-branch.'
        )

    data = CoverageData(basename=os.fspath(coverage_path))
    data.read()
    measured = {
        os.path.normcase(os.path.abspath(filename)): filename
        for filename in data.measured_files()
    }

    total = 0
    missing = []
    for filename in MODEL_FILES:
        source_path = ROOT / 'models' / filename
        tree = ast.parse(source_path.read_text(encoding='utf-8-sig'))
        coverage_filename = measured.get(
            os.path.normcase(os.path.abspath(source_path))
        )
        covered_lines = set(data.lines(coverage_filename) or ()) if coverage_filename else set()

        for node in (
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            total += 1
            line = _first_executable_line(node)
            if line not in covered_lines:
                missing.append(f'{filename}.{node.name}:{line}')

        for class_node in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for method in _active_methods(class_node):
                total += 1
                line = _first_executable_line(method)
                if line not in covered_lines:
                    missing.append(f'{filename}:{class_node.name}.{method.name}:{line}')

    covered = total - len(missing)
    print(f'Métodos/funciones activos ejecutados: {covered}/{total}')
    if missing:
        print('Métodos sin ejecutar:')
        print('\n'.join(missing))
        return 1

    coverage = Coverage(data_file=os.fspath(coverage_path), branch=True)
    coverage.load()
    coverage.report(
        include=[
            os.fspath(ROOT / 'models' / filename)
            for filename in MODEL_FILES
        ]
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
