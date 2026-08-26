import json
import os
import re
import subprocess
import time
import urllib.request
import urllib.error

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
OLLAMA_BIN = os.environ.get("OLLAMA_BIN", r"C:\Users\Eliot\ollama_portable\ollama.exe")
_REQUEST_TIMEOUT = 120


def _generar_prompt(descripcion, gravedad_nivel, color_semaforo):
    contexto = ""
    if gravedad_nivel:
        contexto += f"La gravedad asignada es: {gravedad_nivel}. "
    if color_semaforo:
        contexto += f"El semáforo de la obra asociada está en color: {color_semaforo}. "

    return f"""
    Eres un sistema de priorización de solicitudes de infraestructura vial del INVILARA.
    Analiza la siguiente solicitud de un ciudadano:
    "{descripcion}"
    {contexto}
    Asigna una prioridad numérica del 0.0 (muy alta prioridad / crítica, atender ya)
    al 1.0 (muy baja prioridad) y proporciona una breve justificación (máx. 100 caracteres).
    Responde ÚNICAMENTE en formato JSON: {{"prioridad": <número>, "justificacion": "<texto>"}}.
    """


def _servidor_disponible():
    try:
        with urllib.request.urlopen(
            f"http://{OLLAMA_HOST}/api/tags", timeout=3
        ) as r:
            return r.status == 200
    except Exception:
        return False


def _arrancar_ollama():
    """Lanza el servidor de Ollama en segundo plano si no está corriendo."""
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
    """Extrae de forma defensiva el JSON de la respuesta del modelo."""
    raw = (data.get("response") or "{}").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}


def _prioridad_heuristica(gravedad_nivel, color_semaforo):
    """
    Calcula una prioridad determinista (0=máxima, 1=mínima) a partir de la
    gravedad y el color del semáforo, usada como respaldo cuando el modelo
    local no devuelve un JSON válido.
    """
    color = (color_semaforo or "").lower()
    gravedad = (gravedad_nivel or "").lower()

    base_por_color = {
        "rojo": 0.15,
        "roja": 0.15,
        "amarillo": 0.50,
        "amarilla": 0.50,
        "verde": 0.85,
    }
    p = base_por_color.get(color, 0.5)

    if gravedad in ("alta", "critica", "crítica"):
        p = min(p, 0.2)
    elif gravedad in ("baja", "minima", "mínima"):
        p = max(p, 0.75)

    p = round(min(max(p, 0.0), 1.0), 3)
    partes = []
    if color:
        partes.append(f"semáforo {color}")
    if gravedad:
        partes.append(f"gravedad {gravedad}")
    contexto = " y ".join(partes) if partes else "sin contexto de gravedad/semáforo"
    return {
        "prioridad": p,
        "justificacion": f"Prioridad estimada por reglas ({contexto}).",
    }


def _a_float(valor, defecto=0.5):
    try:
        return round(min(max(float(valor), 0.0), 1.0), 3)
    except (TypeError, ValueError):
        return defecto


def _clasificar(descripcion, gravedad_nivel, color_semaforo):
    prompt = _generar_prompt(descripcion, gravedad_nivel, color_semaforo)
    payload = json.dumps({
        "model": "llama3.2:1b",
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"num_predict": 220, "temperature": 0},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"http://{OLLAMA_HOST}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        # Cualquier fallo de red/respuesta: usar respaldo por reglas.
        return {"prioridad": 0.5, "justificacion": "Sin justificación"}
    resultado = _parsear_respuesta(data)
    return {
        "prioridad": _a_float(resultado.get("prioridad"), 0.5),
        "justificacion": str(resultado.get("justificacion", "Sin justificación"))[:100],
    }


def calcular_prioridad_con_ia(descripcion, gravedad_nivel=None, color_semaforo=None):
    """
    Clasifica una solicitud en un rango de prioridad de 0 (máxima prioridad)
    a 1 (mínima prioridad) usando el modelo local llama3.2:1b de Ollama.
    Si el servidor de Ollama no está activo, intenta arrancarlo automáticamente.
    Si el modelo no devuelve un JSON válido, usa una estimación por reglas.
    Funciona 100% en local (sin internet, sin CDN).
    """
    def _resultado_final():
        try:
            res = _clasificar(descripcion, gravedad_nivel, color_semaforo)
        except urllib.error.URLError:
            _arrancar_ollama()
            if _servidor_disponible():
                try:
                    res = _clasificar(descripcion, gravedad_nivel, color_semaforo)
                except Exception as e:
                    return {"prioridad": 0.5,
                            "justificacion": f"Error en IA: {str(e)}"}
            else:
                return {
                    "prioridad": 0.5,
                    "justificacion": (
                        "Ollama no está disponible. Verifica que el servidor "
                        f"esté activo en http://{OLLAMA_HOST} (ejecuta "
                        "'ollama serve')."
                    ),
                    "error_ia": "Ollama no accesible tras intentar arrancarlo",
                }
        # Si el modelo no dio una prioridad válida, usar respaldo por reglas.
        if res.get("prioridad") in (None, 0.5) and res.get("justificacion") in (
            None, "", "Sin justificación"
        ):
            return _prioridad_heuristica(gravedad_nivel, color_semaforo)
        return res

    try:
        return _resultado_final()
    except Exception as e:
        mensaje = str(e)
        if "this model does not support image input" in mensaje or "Cannot read" in mensaje:
            mensaje = "Error en IA: el modelo configurado no soporta imágenes. Usa un modelo de texto o envía solo texto."
        return {"prioridad": 0.5,
                "justificacion": mensaje}
