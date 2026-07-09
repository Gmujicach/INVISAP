import requests
import json


def calcular_prioridad_con_ia(descripcion, gravedad_nivel=None, color_semaforo=None):
    """
    Clasifica una solicitud en un rango de prioridad de 0 (máxima prioridad)
    a 1 (mínima prioridad) usando el modelo local llama3.2:1b de Ollama.
    Funciona 100% en local (sin internet, sin CDN).
    """
    contexto = ""
    if gravedad_nivel:
        contexto += f"La gravedad asignada es: {gravedad_nivel}. "
    if color_semaforo:
        contexto += f"El semáforo de la obra asociada está en color: {color_semaforo}. "

    prompt = f"""
    Eres un sistema de priorización de solicitudes de infraestructura vial del INVILARA.
    Analiza la siguiente solicitud de un ciudadano:
    "{descripcion}"
    {contexto}
    Asigna una prioridad numérica del 0.0 (muy alta prioridad / crítica, atender ya)
    al 1.0 (muy baja prioridad) y proporciona una breve justificación (máx. 100 caracteres).
    Responde ÚNICAMENTE en formato JSON: {{"prioridad": <número>, "justificacion": "<texto>"}}.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        resultado = json.loads(data.get("response", "{}"))
        return {
            "prioridad": float(resultado.get("prioridad", 0.5)),
            "justificacion": resultado.get("justificacion", "Sin justificación")
        }
    except Exception as e:
        return {"prioridad": 0.5, "justificacion": f"Error en IA: {str(e)}"}
