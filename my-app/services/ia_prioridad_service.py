import json
import os
import re
import subprocess
import time

import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
OLLAMA_BIN = os.environ.get("OLLAMA_BIN", r"C:\Users\Eliot\ollama_portable\ollama.exe")
_REQUEST_TIMEOUT = 120

TIPOS_OBRA_VALIDOS = {"Obra Mayor", "Obra Menor"}
GRAVEDADAS_VALIDAS = {"Alta", "Baja"}


def _generar_prompt(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante):
    contexto = ""
    if gravedad_nivel:
        contexto += f"La gravedad registrada es: {gravedad_nivel}. "
    if color_semaforo:
        contexto += f"El semáforo de la obra asociada está en color: {color_semaforo}. "
    if tipo_solicitante:
        contexto += f"El tipo de solicitante es: {tipo_solicitante}. "

    return f"""
Eres un ingeniero civil experto del INVILARA (Instituto Vial del Estado Lara, Venezuela). Tu trabajo es clasificar solicitudes de infraestructura vial.

Analiza la siguiente solicitud:

SOLICITUD: "{descripcion}"
{contexto}

DEFINICIONES TÉCNICAS:
- "Obra Mayor": Proyectos complejos que requieren maquinaria pesada, permisos extensos, y tardan MESES en completarse. Ejemplos: reconstrucción de carreteras, asfaltado de avenidas principales, reparación de puentes, drenajes profundos, colapsos estructurales.
- "Obra Menor": Reparaciones simples y rápidas que se completan en DÍAS. Ejemplos: bacheo menor, reparación de fugas simples, luminarias, señalización, jornadas de vacunación, cortes de agua/luz/gas.

RIESGO (Gravedad):
- "Alta": Riesgo inminente a personas, infraestructura crítica, o paralización total del servicio.
- "Baaja": Situación controlada, mejora gradual, sin peligro inmediato.

Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin markdown:
{{"tipo_obra": "Obra Mayor" o "Obra Menor", "gravedad_sugerida": "Alta" o "Baja", "justificacion": "<texto breve en español>"}}
"""


def _servidor_disponible():
    try:
        r = requests.get(f"http://{OLLAMA_HOST}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _arrancar_ollama():
    if _servidor_disponible() or not os.path.exists(OLLAMA_BIN):
        return
    try:
        subprocess.Popen(
            [OLLAMA_BIN, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            | getattr(subprocess, "DETACHED_PROCESS", 0),
        )
    except Exception:
        return
    for _ in range(20):
        time.sleep(1)
        if _servidor_disponible():
            return


def _parsear_respuesta(data):
    raw = (data.get("response") or "{}").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}


def _clasificacion_heuristica(gravedad_nivel, color_semaforo, tipo_solicitante, descripcion=""):
    color = (color_semaforo or "").lower()
    gravedad = (gravedad_nivel or "").lower()
    desc = (descripcion or "").lower()

    tipo_obra = "Obra Menor"
    gravedad_sugerida = "Baja"

    obra_mayor_keywords = [
        "reconstrucción", "reconstruir", "asfaltado extenso", "asfaltar avenida",
        "puente", "viaducto", "drenaje profundo", "colector pluvial",
        "carretera nacional", "carretera regional", "colapso de vía",
        "colapso estructural", "sedimentos masivos", "remoción de escombros",
        "maquinaria pesada", "excavadora", "retroexcavadora",
        "acondicionamiento vial", "vialidad", "bacheo profundo",
        "reparación mayor", "obra civil mayor", "infraestructura vial"
    ]
    obra_menor_keywords = [
        "no hay agua", "no hay luz", "no hay gas", "fuga de agua",
        "fuga de gas", "bache simple", "bacheo menor", "reparación menor",
        "luminaria", "señalización", "jornada de vacunación", "vacunación",
        "limpieza", "pintura", "barrido", "desmalezamiento", "hueco simple",
        "servicios básicos"
    ]
    alta_gravedad_keywords = [
        "riesgo inminente", "peligro", "emergencia", "crítico", "crítica",
        "colapso", "inundación", "deslave", "accidente", "heridos",
        "paralizada", "obstrucción total", "infraestructura crítica",
        "aguas negras", "contaminación"
    ]

    es_mayor = any(p in desc for p in obra_mayor_keywords)
    es_menor = any(p in desc for p in obra_menor_keywords)

    if es_mayor and not es_menor:
        tipo_obra = "Obra Mayor"
    elif es_menor and not es_mayor:
        tipo_obra = "Obra Menor"
    elif es_mayor and es_menor:
        tipo_obra = "Obra Mayor"

    if color in ("rojo", "roja") or gravedad in ("alta", "critica", "crítica"):
        gravedad_sugerida = "Alta"
    if any(p in desc for p in alta_gravedad_keywords):
        gravedad_sugerida = "Alta"

    if tipo_solicitante and tipo_solicitante.lower() in ("comunidad", "institucion", "institución"):
        if tipo_obra == "Obra Menor" and gravedad_sugerida == "Alta":
            tipo_obra = "Obra Mayor"

    partes = []
    if color:
        partes.append(f"semáforo {color}")
    if gravedad:
        partes.append(f"gravedad {gravedad}")
    contexto = " y ".join(partes) if partes else "análisis de descripción"

    return {
        "tipo_obra": tipo_obra,
        "gravedad_sugerida": gravedad_sugerida,
        "justificacion": f"Clasificación: {tipo_obra} con riesgo {gravedad_sugerida} ({contexto}).",
        "origen": "heuristica"
    }


def _validar_resultado(resultado):
    tipo_obra = resultado.get("tipo_obra")
    gravedad = resultado.get("gravedad_sugerida")
    justificacion = resultado.get("justificacion", "")

    if tipo_obra not in TIPOS_OBRA_VALIDOS:
        return None
    if gravedad not in GRAVEDADAS_VALIDAS:
        return None

    return {
        "tipo_obra": tipo_obra,
        "gravedad_sugerida": gravedad,
        "justificacion": str(justificacion)[:100],
        "origen": "ia"
    }


def _clasificar(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante):
    prompt = _generar_prompt(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante)
    payload = {
        "model": "llama3.2:1b",
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"num_predict": 220, "temperature": 0},
    }
    try:
        response = requests.post(
            f"http://{OLLAMA_HOST}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    resultado = _parsear_respuesta(data)
    if not resultado:
        return None

    return _validar_resultado(resultado)


def clasificar_solicitud_ia(descripcion, gravedad_nivel=None, color_semaforo=None, tipo_solicitante=None):
    """
    Clasifica una solicitud. Usa heurística como método principal (más confiable)
    y solo intenta con IA si la heurística no encuentra coincidencias claras.
    """
    resultado = _clasificacion_heuristica(gravedad_nivel, color_semaforo, tipo_solicitante, descripcion)

    if resultado.get("origen") != "heuristica":
        return resultado

    try:
        res_ia = _clasificar(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante)
        if res_ia is not None:
            tipo_ia = res_ia.get("tipo_obra")
            heuristica_tipo = resultado.get("tipo_obra")
            if tipo_ia == heuristica_tipo:
                return {
                    "tipo_obra": res_ia["tipo_obra"],
                    "gravedad_sugerida": res_ia["gravedad_sugerida"],
                    "justificacion": res_ia["justificacion"],
                    "origen": "ia_validada"
                }
    except Exception:
        pass

    return resultado


def calcular_prioridad_con_ia(descripcion, gravedad_nivel=None, color_semaforo=None, tipo_solicitante=None):
    """
    Wrapper de compatibilidad con la interfaz anterior.
    Retorna: {"prioridad": float, "justificacion": str, "tipo_obra": str, "gravedad_sugerida": str}
    """
    resultado = clasificar_solicitud_ia(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante)

    pesos = {
        ("Obra Mayor", "Alta"): 0.10,
        ("Obra Mayor", "Baja"): 0.35,
        ("Obra Menor", "Alta"): 0.55,
        ("Obra Menor", "Baja"): 0.85,
    }

    prioridad = pesos.get(
        (resultado["tipo_obra"], resultado["gravedad_sugerida"]),
        0.50
    )

    return {
        "prioridad": prioridad,
        "justificacion": resultado["justificacion"],
        "tipo_obra": resultado["tipo_obra"],
        "gravedad_sugerida": resultado["gravedad_sugerida"],
        "origen": resultado.get("origen", "desconocido"),
    }
