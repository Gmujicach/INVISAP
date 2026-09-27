"""Verificador de tours interactivos (Driver.js).

Recorre todos los archivos `static/js/tour/<modulo>/tour.js`, extrae los
selectores `element:` de cada paso y comprueba si existen realmente en las
plantillas HTML del módulo correspondiente.

Uso:  python verificar_tours.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VISTAS = RAIZ / "vista"
TOURS = RAIZ / "static" / "js" / "tour"

# Vistas candidatas por módulo (se busca el selector en la unión de todas).
# `base_cpanel.html` se incluye siempre porque aporta el menú lateral, la
# barra superior, el botón flotante del tour y los modales globales.
VISTAS_POR_MODULO = {
    "bitacora": ["bitacora/*.html", "base_cpanel.html"],
    "contratacion": ["contratacion/*.html", "base_cpanel.html"],
    "default": ["base_cpanel.html", "home/*.html"],
    "empleados": ["empleados/*.html", "base_cpanel.html"],
    "empresas": ["empresas/*.html", "base_cpanel.html"],
    "evidencia": ["evidencia/*.html", "base_cpanel.html"],
    "home": ["home/dashboard.html", "base_cpanel.html"],
    "ia": ["ia/*.html", "base_cpanel.html"],
    "inf_avance_obra": ["inf_avance_obra/*.html", "base_cpanel.html"],
    "inspeccion": ["inspeccion/*.html", "base_cpanel.html"],
    "login": ["login/*.html"],
    "manual": ["manual/*.html", "base_cpanel.html"],
    "obras": ["obras/*.html", "base_cpanel.html"],
    "perfil": ["perfil/*.html", "base_cpanel.html"],
    "proyectos": ["proyectos/*.html", "home/dashboard.html", "base_cpanel.html"],
    "publicaciones": ["publicaciones/*.html", "base_cpanel.html"],
    "reportes": ["reportes/*.html", "base_cpanel.html"],
    "respaldo": ["respaldo/*.html", "base_cpanel.html"],
    "seguridad": ["seguridad/*.html", "base_cpanel.html"],
    "solicitudes": ["solicitudes/*.html", "base_cpanel.html"],
    "usuarios": ["usuarios/*.html", "base_cpanel.html"],
}

# Elementos que se crean por JavaScript en tiempo de ejecución
DINAMICOS = {
    "tbody", "tr", "first-child", "nth-child",
}

RE_ELEMENTO = re.compile(r"element:\s*'([^']+)'")
RE_ID = re.compile(r"#([A-Za-z_][\w-]*)")
RE_CLASE = re.compile(r"\.([A-Za-z_][\w-]*)")
RE_ATRIBUTO = re.compile(r"\[([A-Za-z_:][\w:.-]*)(?:([~^$*|]?=)\"?'?([^\]\"']*))?\]")
RE_TAG = re.compile(r"(?:^|[\s,>])([a-z][a-z0-9]*)(?=[.\s\[,>:#]|$)")


def texto_de_vistas(patrones):
    partes = []
    for patron in patrones:
        for archivo in VISTAS.glob(patron):
            partes.append(archivo.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(partes)


def comprobar_selector(selector, html):
    """Devuelve (ok, razon). Un selector es válido si al menos uno de sus
    identificadores, clases, atributos o etiquetas simples aparece en el
    HTML del módulo."""
    if not selector.strip():
        return False, "selector vacío"

    ids = RE_ID.findall(selector)
    clases = RE_CLASE.findall(selector)

    for identificador in ids:
        if re.search(r'id="%s"' % re.escape(identificador), html):
            return True, "#%s" % identificador
    for clase in clases:
        if re.search(r'class="[^"]*\b%s\b' % re.escape(clase), html):
            return True, ".%s" % clase

    for atributo, operador, valor in RE_ATRIBUTO.findall(selector):
        if operador in ("", "~"):
            if re.search(r'\b%s\s*=' % re.escape(atributo), html):
                return True, "[%s]" % atributo
        elif operador == "=":
            if re.search(r'\b%s\s*=\s*"%s"' % (re.escape(atributo), re.escape(valor)), html):
                return True, '[%s="%s"]' % (atributo, valor)
        elif operador == "*=":
            if valor and valor.lower() in html.lower():
                return True, '[%s*="%s"]' % (atributo, valor)

    if ids or clases:
        return False, "no se encontró %s" % ", ".join(
            (["#" + i for i in ids] + ["." + c for c in clases])[:4]
        )

    tags = [t for t in RE_TAG.findall(selector) if t not in ("html", "body")]
    if not tags:
        return False, "selector sin referencia verificable"
    return True, "tag <%s>" % tags[0]


def main():
    problemas = 0
    total_pasos = 0
    for tour in sorted(TOURS.glob("*/tour.js")):
        modulo = tour.parent.name
        if modulo not in VISTAS_POR_MODULO:
            continue
        html = texto_de_vistas(VISTAS_POR_MODULO[modulo])
        if not html:
            print("[AVISO] %-16s sin vista de referencia" % modulo)
            continue
        fuente = tour.read_text(encoding="utf-8", errors="ignore")
        selectores = RE_ELEMENTO.findall(fuente)
        total_pasos += len(selectores)
        fallidos = []
        for selector in selectores:
            candidatos = [s.strip() for s in selector.split(",") if s.strip()]
            if any(comprobar_selector(s, html)[0] for s in candidatos):
                continue
            fallidos.append(selector)
        if fallidos:
            problemas += len(fallidos)
            print("[FALLA] %s" % modulo)
            for selector in fallidos:
                print("         %s" % selector)
        else:
            print("[OK]    %-16s %2d pasos verificados" % (modulo, len(selectores)))

    print("\n%d pasos analizados · %d selectores sin resolver" % (total_pasos, problemas))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
