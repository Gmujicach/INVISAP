"""Run per-module Locust scenarios and update the Chapter IV test log."""

import argparse
import csv
import io
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


MODULES = {
    'solicitudes': ('Solicitudes', 'locust_solicitudes.py', '/api/obtener-solicitudes-json'),
    'gravedad_obra': ('Gravedad de Obra', 'locust_gravedad_obra.py', '/api/gravedad/listar'),
    'prioridad': ('Prioridad', 'locust_prioridad.py', '/api/prioridad/listar'),
    'proyectos': ('Proyectos', 'locust_proyectos.py', '/api/proyecto/validar-codigo/<código>'),
    'maquinaria': ('Maquinaria', 'locust_maquinaria.py', '/api/maquinaria/listar'),
    'contratacion': ('Contratación', 'locust_contratacion.py', '/api/obtener-empresas-json'),
    'empresa': ('Empresa', 'locust_empresa.py', '/api/empresas/<RIF>'),
    'obras': ('Obras', 'locust_obras.py', '/api/obra/estados'),
    'empleados': ('Empleados', 'locust_empleados.py', '/empleados/api/listar-json'),
    'inspecciones': ('Inspecciones', 'locust_inspecciones.py', '/inspecciones/api/inspectores/listar'),
    'evidencias': ('Evidencias', 'locust_evidencias.py', '/api/evidencias/validar/<id>'),
    'informe_avance': ('Informe de Avance de Obra', 'locust_informe_avance.py', '/api/informes/listar-json'),
    'publicaciones': ('Publicaciones', 'locust_publicaciones.py', '/api/publicaciones/validar-informe/<id>'),
    'reportes_pdf': ('Reportes PDF', 'locust_reportes_pdf.py', '/reportes/reporte-pdf'),
    'reportes_excel': ('Reportes Excel', 'locust_reportes_excel.py', '/reportes/reporte-excel'),
    'reportes_estadisticos': (
        'Reportes Estadísticos',
        'locust_reportes_estadisticos.py',
        '/reporte-estadistico/data',
    ),
    'usuarios': ('Usuarios', 'locust_usuarios.py', '/api/users/<id>'),
    'permisos_por_rol': ('Permisos por Rol', 'locust_permisos_por_rol.py', '/api/seguridad/permisos/obtener/<id_rol>'),
    'administracion_respaldos': (
        'Administración de Respaldos',
        'locust_administracion_respaldos.py',
        '/respaldo/api/listar-json',
    ),
    'bitacora': ('Bitácora', 'locust_bitacora.py', '/api/obtener-bitacora-json'),
}

PROFILES = {
    'quick': {'users': 1, 'spawn_rate': 1, 'run_time': '5s'},
    'baseline': {'users': 5, 'spawn_rate': 1, 'run_time': '30s'},
    'stress': {'users': 20, 'spawn_rate': 5, 'run_time': '60s'},
    'spike': {'users': 30, 'spawn_rate': 30, 'run_time': '30s'},
}

RESULT_FIELDS = [
    'timestamp',
    'module',
    'profile',
    'host',
    'users',
    'spawn_rate',
    'run_time',
    'request_name',
    'requests',
    'failures',
    'failure_percent',
    'requests_per_second',
    'average_ms',
    'median_ms',
    'p95_ms',
    'locust_exit_code',
]


def parse_args():
    parser = argparse.ArgumentParser(
        description='Ejecuta escenarios Locust de INVISAP y actualiza la bitácora del Capítulo IV.'
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--module', choices=MODULES, help='Identificador del módulo.')
    selection.add_argument('--all', action='store_true', help='Ejecuta los 20 módulos.')
    parser.add_argument(
        '--profile',
        choices=PROFILES,
        default='baseline',
        help='Perfil: quick, baseline, stress o spike (por defecto: baseline).',
    )
    parser.add_argument(
        '--host',
        default=os.environ.get('INVISAP_TEST_URL', 'http://127.0.0.1:5600'),
        help='URL base de INVISAP; también puede definirse con INVISAP_TEST_URL.',
    )
    parser.add_argument('--users', type=int, help='Sobrescribe los usuarios del perfil.')
    parser.add_argument(
        '--spawn-rate',
        type=float,
        help='Sobrescribe los usuarios iniciados por segundo.',
    )
    parser.add_argument(
        '--run-time',
        help='Sobrescribe la duración de cada módulo, por ejemplo 45s o 2m.',
    )
    return parser.parse_args()


def read_locust_stats(stats_path):
    rows = []
    if not stats_path.is_file():
        return rows
    content = stats_path.read_bytes()
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = content.decode('cp1252')
    for row in csv.DictReader(io.StringIO(text, newline='')):
        if row.get('Name') and row.get('Name') != 'Aggregated':
            rows.append(row)
    return rows


def as_number(row, field):
    value = row.get(field, '')
    try:
        return float(value) if value else 0.0
    except ValueError:
        return 0.0


def format_number(value, decimals=2):
    return f'{value:.{decimals}f}'


def append_results(results_path, module, profile, host, users, spawn_rate, run_time, rows, exit_code, timestamp):
    results_path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not results_path.exists() or results_path.stat().st_size == 0
    with results_path.open('a', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=RESULT_FIELDS)
        if needs_header:
            writer.writeheader()
        for row in rows or [{}]:
            requests = int(as_number(row, 'Request Count'))
            failures = int(as_number(row, 'Failure Count'))
            writer.writerow({
                'timestamp': timestamp,
                'module': module,
                'profile': profile,
                'host': host,
                'users': users,
                'spawn_rate': spawn_rate,
                'run_time': run_time,
                'request_name': row.get('Name') or 'Sin solicitudes registradas',
                'requests': requests,
                'failures': failures,
                'failure_percent': format_number(
                    (failures * 100 / requests) if requests else 0
                ),
                'requests_per_second': row.get('Requests/s', '0'),
                'average_ms': row.get('Average Response Time', '0'),
                'median_ms': row.get('Median Response Time', '0'),
                'p95_ms': row.get('95%', '0'),
                'locust_exit_code': exit_code,
            })


def update_chapter_report(report_path, results_path):
    start_marker = '<!-- PERFORMANCE_RESULTS_START -->'
    end_marker = '<!-- PERFORMANCE_RESULTS_END -->'
    report = report_path.read_text(encoding='utf-8')
    if report.count(start_marker) != 1 or report.count(end_marker) != 1:
        raise RuntimeError(f'No se encontraron marcadores únicos de resultados en {report_path}.')

    table_rows = []
    if results_path.is_file():
        with results_path.open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                table_rows.append(row)

    lines = [
        '| Fecha y hora | Módulo | Perfil | Solicitudes | Fallos | Fallos % | Req/s | Promedio ms | Mediana ms | P95 ms |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for row in table_rows[-100:]:
        lines.append(
            '| {timestamp} | {module} | {profile} | {requests} | {failures} | '
            '{failure_percent}% | {requests_per_second} | {average_ms} | '
            '{median_ms} | {p95_ms} |'.format(**row)
        )
    if not table_rows:
        lines = [
            '_Sin ejecuciones registradas todavía. Inicie la aplicación de pruebas y ejecute '
            '`python tests\\performance\\run_performance.py --all --profile quick`._'
        ]

    replacement = f'{start_marker}\n' + '\n'.join(lines) + f'\n{end_marker}'
    report_path.write_text(
        report.replace(
            report[report.index(start_marker):report.index(end_marker) + len(end_marker)],
            replacement,
        ),
        encoding='utf-8',
    )


def run_module(project_dir, module_key, args, results_path, report_path):
    module_name, filename, endpoint = MODULES[module_key]
    profile = PROFILES[args.profile]
    users = args.users if args.users is not None else profile['users']
    spawn_rate = args.spawn_rate if args.spawn_rate is not None else profile['spawn_rate']
    run_time = args.run_time if args.run_time is not None else profile['run_time']
    locust_file = project_dir / 'tests' / 'performance' / filename
    if not locust_file.is_file():
        raise FileNotFoundError(f'No se encontró el escenario de {module_name}: {locust_file}')

    timestamp = datetime.now().astimezone().isoformat(timespec='seconds')
    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    results_path.parent.mkdir(parents=True, exist_ok=True)
    output_prefix = results_path.parent / f'{file_stamp}_{module_key}'
    command = [
        sys.executable,
        '-m',
        'locust',
        '-f',
        str(locust_file),
        '--headless',
        '--host',
        args.host.rstrip('/'),
        '--users',
        str(users),
        '--spawn-rate',
        str(spawn_rate),
        '--run-time',
        run_time,
        '--csv',
        str(output_prefix),
        '--loglevel',
        'WARNING',
    ]

    print(
        f'\n[PRUEBA DE RENDIMIENTO - LOCUST] {module_name}: '
        f'perfil {args.profile}, {users} usuarios, duración {run_time}; '
        f'GET {endpoint} ({locust_file.name}).',
        flush=True,
    )
    completed = subprocess.run(command, cwd=project_dir, check=False)
    rows = read_locust_stats(Path(f'{output_prefix}_stats.csv'))
    append_results(
        results_path,
        module_name,
        args.profile,
        args.host.rstrip('/'),
        users,
        spawn_rate,
        run_time,
        rows,
        completed.returncode,
        timestamp,
    )
    update_chapter_report(report_path, results_path)

    requests = sum(int(as_number(row, 'Request Count')) for row in rows)
    failures = sum(int(as_number(row, 'Failure Count')) for row in rows)
    outcome = (
        'APROBADA'
        if requests > 0 and completed.returncode == 0 and failures == 0
        else 'REVISAR'
    )
    print(
        f'Concluyó prueba de {module_name} — Tipo: Prueba de rendimiento '
        f'({args.profile}) — Resultado: {outcome}; '
        f'{requests} solicitudes, {failures} fallos HTTP. '
        f'Bitácora actualizada en {report_path}.',
        flush=True,
    )
    return completed.returncode == 0 and requests > 0 and failures == 0


def main():
    args = parse_args()
    if args.users is not None and args.users < 1:
        raise SystemExit('--users debe ser mayor que cero.')
    if args.spawn_rate is not None and args.spawn_rate <= 0:
        raise SystemExit('--spawn-rate debe ser mayor que cero.')
    if not args.host.startswith(('http://', 'https://')):
        raise SystemExit('--host debe comenzar con http:// o https://.')

    project_dir = Path(__file__).resolve().parents[2]
    performance_dir = project_dir / 'tests' / 'performance'
    results_dir = Path(os.environ.get(
        'INVISAP_PERF_RESULTS_DIR',
        str(performance_dir / 'results'),
    ))
    if not results_dir.is_absolute():
        results_dir = project_dir / results_dir
    results_path = results_dir / 'bitacora_rendimiento.csv'
    report_path = performance_dir / 'Capitulo_IV_Rendimiento.md'
    module_keys = list(MODULES) if args.all else [args.module]

    failures = []
    for module_key in module_keys:
        try:
            passed = run_module(
                project_dir,
                module_key,
                args,
                results_path,
                report_path,
            )
        except (OSError, RuntimeError) as error:
            print(f'Error ejecutando {module_key}: {error}', file=sys.stderr)
            failures.append(module_key)
            continue
        if not passed:
            failures.append(module_key)

    print(
        f'\nResumen de rendimiento: {len(module_keys) - len(failures)} '
        f'aprobados, {len(failures)} para revisar.'
    )
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
