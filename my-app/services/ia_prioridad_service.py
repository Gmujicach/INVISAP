import requests
import json

def calcular_prioridad_con_ia(descripcion, gravedad_nivel=None):
    prompt = f"""
    Eres un sistema de priorización de proyectos de infraestructura.
    Basándote en la siguiente descripción de una solicitud:
    "{descripcion}"
    {f"Además, la gravedad asignada es: {gravedad_nivel}" if gravedad_nivel else ""}
    Asigna una prioridad numérica del 1 (muy baja) al 5 (muy alta) y proporciona una breve justificación (máx. 100 caracteres).
    Responde únicamente en formato JSON: {{"prioridad": <número>, "justificacion": "<texto>"}}.
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
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        resultado = json.loads(data.get("response", "{}"))  # ← CLAVE CORRECTA
        return {
            "prioridad": float(resultado.get("prioridad", 3.0)),
            "justificacion": resultado.get("justificacion", "Sin justificación")
        }
    except Exception as e:
        return {"prioridad": 3.0, "justificacion": f"Error en IA: {str(e)}"}