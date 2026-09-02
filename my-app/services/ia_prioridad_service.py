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
Eres un sistema experto en priorización de solicitudes de infraestructura vial del INVILARA (Instituto Vial del Estado Lara, Venezuela).

Analiza la siguiente solicitud ciudadana y determina su clasificación técnica:

SOLICITUD: "{descripcion}"
{contexto}

INSTRUCCIONES:
1. Determina si la magnitud del problema corresponde a una "Obra Mayor" (reconstrucción, asfalto extenso, puentes, drenajes principales) o "Obra Menor" (bacheo, reparaciones menores, mantenimiento puntual).
2. Determina la gravedad sugerida: "Alta" si representa riesgo inminente a personas o infraestructura crítica, "Baja" si es una mejora o mantenimiento no urgente.
3. Proporciona una justificación técnica breve (máx. 100 caracteres).

Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin markdown:
{{"tipo_obra": "Obra Mayor" o "Obra Menor", "gravedad_sugerida": "Alta" o "Baja", "justificacion": "<texto breve>"}}
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

    palabras_mayor = [
        "reconstrucción", "reconstruir", "asfalto", "asfaltar", "pavimentar",
        "puente", "drenaje", "alcantarilla", "colector", "vía principal",
        "carretera", "avenida", "colapso", "obstrucción", "sedimentos",
        "bacheo profundo", "reparación mayor", "infraestructura", "vialidad",
        "vía", "calzada", "obra", "construcción", "remoción", "maquinaria"
    ]
    palabras_alta_gravedad = [
        "riesgo", "peligro", "emergencia", "crítico", "crítica", "urgente",
        "colapso", "inundación", "deslave", "accidente", "heridos", "muerte",
        "obstrucción total", "paralizada", "rojo", "infraestructura crítica"
    ]

    if any(p in desc for p in palabras_mayor):
        tipo_obra = "Obra Mayor"
    if color in ("rojo", "roja") or gravedad in ("alta", "critica", "crítica"):
        gravedad_sugerida = "Alta"
    if any(p in desc for p in palabras_alta_gravedad):
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
        "justificacion": f"Heurística: {tipo_obra} con gravedad {gravedad_sugerida} ({contexto}).",
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
    Clasifica una solicitud usando el modelo local llama3.2:1b de Ollama.
    Retorna: {"tipo_obra": str, "gravedad_sugerida": str, "justificacion": str, "origen": str}
    Si Ollama no está disponible, intenta arrancarlo automáticamente.
    Si el modelo no devuelve un JSON válido, usa una estimación por reglas.
    """
    def _resultado_final():
        res = _clasificar(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante)
        if res is not None:
            return res

        try:
            import urllib.request
            urllib.request.urlopen(f"http://{OLLAMA_HOST}/api/tags", timeout=2)
        except Exception:
            _arrancar_ollama()
            if _servidor_disponible():
                res = _clasificar(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante)
                if res is not None:
                    return res

        return _clasificacion_heuristica(gravedad_nivel, color_semaforo, tipo_solicitante, descripcion)

    try:
        return _resultado_final()
    except Exception as e:
        return {
            "tipo_obra": "Obra Menor",
            "gravedad_sugerida": "Baja",
            "justificacion": f"Error en IA: {str(e)[:80]}",
            "origen": "error"
        }


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
