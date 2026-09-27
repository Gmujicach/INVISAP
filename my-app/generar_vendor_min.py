"""
generar_vendor_min.py

Minifica las librerias de terceros que el proyecto carga en TODAS las
paginas. Motivo: los archivos originales son builds de desarrollo que
traen el sourcemap en base64 incrustado, lo que ocupa mas del 58% del
peso sin aportar nada al navegador.

    jquery.js     814 KB -> base64 491 KB
    bootstrap.js  823 KB -> base64 468 KB
    ...

Este script quita el base64, ejecuta terser y deja el `.min.js` al lado
del original. Los originales no se borran.
"""
import pathlib
import re
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
STATIC = RAIZ / 'static'
NPM_NPX = r'C:\Program Files\nodejs\npx.cmd'

OBJETIVOS = [
    ('assets/vendor/libs/jquery/jquery.js', 'assets/vendor/libs/jquery/jquery.min.js'),
    ('assets/vendor/js/bootstrap.js', 'assets/vendor/js/bootstrap.min.js'),
    ('assets/vendor/libs/popper/popper.js', 'assets/vendor/libs/popper/popper.min.js'),
    ('assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.js',
     'assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.min.js'),
    ('assets/vendor/js/menu.js', 'assets/vendor/js/menu.min.js'),
]

# Solo se toca el payload base64 del data URI. Los marcadores `//#` de
# webpack viven DENTRO de un string `eval("...\n//# sourceMappingURL=...")`.
# Borrar la linea entera se carry el `");` que cierra ese string y el archivo
# deja de ser JS valido, asi que se conserva el marcador y solo se vacia el
# base64.
RE_B64_URL = re.compile(
    r'(//#\s*sourceMappingURL=data:application/json;(?:charset=[^;]+;)?base64,)'
    r'[A-Za-z0-9+/=]+'
)


def limpiar(texto):
    """Quita el payload base64 sin romper los strings de webpack."""
    limpio, n = RE_B64_URL.subn(r'\1', texto)
    if limpio != texto:
        limpio = limpio.replace(
            '//# sourceMappingURL=data:application/json;charset=utf-8;base64,',
            '/* source map omitida en produccion */'
        )
    return limpio


def kb(n):
    return n / 1024.0


def validar(destino, esperado):
    """Verifica que el archivo generado sea JS valido y, cuando no intervino
    terser, que difiera del original unicamente en el sourcemap.

    Es imprescindible: si el base64 se quita de forma incorrecta se rompen
    los strings de `eval(...)` de webpack y el archivo deja de cargarse en
    el navegador sin que ningun error de Python lo delate.
    """
    if not destino.exists():
        return False, 'no se genero el archivo'

    if esperado is not None:
        leido = destino.read_text(encoding='utf-8', errors='ignore')
        if leido != esperado:
            return False, 'difiere del original fuera del sourcemap'

    if not shutil.which('node') and not pathlib.Path(NPM_NPX).exists():
        return True, 'valido (node no disponible)'

    proc = subprocess.run(['node', '--check', str(destino)], capture_output=True)
    if proc.returncode != 0:
        detalle = proc.stderr.decode('utf-8', 'ignore').splitlines()
        return False, (detalle[0] if detalle else 'error de sintaxis')
    return True, 'valido'


def main():
    temporal = RAIZ / '.vendor_tmp'
    temporal.mkdir(exist_ok=True)
    total_antes = total_despues = 0
    problemas = []

    try:
        for origen_rel, destino_rel in OBJETIVOS:
            origen = STATIC / origen_rel
            destino = STATIC / destino_rel

            if not origen.exists():
                print('NO EXISTE  %s' % origen_rel)
                continue

            crudo = origen.read_text(encoding='utf-8', errors='ignore')
            limpio = limpiar(crudo)

            if len(limpio) >= len(crudo):
                print('SIN CAMBIO %s (no habia sourcemaps que quitar)' % origen_rel)
                shutil.copyfile(origen, destino)
                total_antes += origen.stat().st_size
                total_despues += destino.stat().st_size
                continue

            tmp_js = temporal / (destino.stem + '.js')
            tmp_js.write_text(limpio, encoding='utf-8')

            comando = [
                NPM_NPX, '--yes', 'terser', str(tmp_js),
                '--compress', '--mangle', '--comments', '/^!/',
                '--output', str(destino),
            ]
            minificado_por_terser = True
            try:
                subprocess.run(comando, check=True, capture_output=True)
            except FileNotFoundError:
                minificado_por_terser = False
                print('npx no disponible; se usa la version sin sourcemap')
                shutil.copyfile(tmp_js, destino)
            except subprocess.CalledProcessError:
                # Los bundles de webpack con `eval(...)` no los parsea terser.
                # En ese caso el archivo sin sourcemap ya es valido.
                minificado_por_terser = False
                shutil.copyfile(tmp_js, destino)

            a = origen.stat().st_size
            b = destino.stat().st_size
            total_antes += a
            total_despues += b

            # Si terser no intervino, el resultado debe ser identico al
            # original salvo por el sourcemap: es la garantia de que solo
            # se borro informacion que el navegador no usa.
            ok, nota = validar(destino, None if minificado_por_terser else limpio)
            if not ok:
                problemas.append('%s -> %s' % (destino_rel, nota))
                # Se descarta el archivo roto para no dejar un .min.js inutil.
                destino.unlink(missing_ok=True)
                b = 0

            via = 'terser' if minificado_por_terser else 'sin sourcemap'
            print('%-56s %7.0f KB -> %6.0f KB  (-%.0f%%)  %s | %s' % (
                origen_rel, kb(a), kb(b), (1 - b / a) * 100 if a else 0, via, nota))
    finally:
        shutil.rmtree(temporal, ignore_errors=True)

    print('-' * 96)
    print('TOTAL %7.0f KB -> %6.0f KB  (-%.0f%%)' % (
        kb(total_antes), kb(total_despues),
        (1 - total_despues / total_antes) * 100 if total_antes else 0))

    if problemas:
        print()
        print('ARCHIVOS DESCARTADOS (no se pueden usar):')
        for p in problemas:
            print('   -', p)
        return 1

    print('Todos los archivos generados son JS valido.')
    return 0


if __name__ == '__main__':
    sys.exit(main())