import requests
import json

class IAPrioridadService:
    def __init__(self):
        # Puerto por defecto donde corre Ollama en tu PC
        self.api_url = "http://localhost:11434/api/generate"
        # Usaremos llama3 o mistral (asegúrate de tenerlo descargado en Ollama)
        self.modelo = "llama3" 

    def clasificar_prioridad(self, descripcion_solicitud, nivel_gravedad):
        prompt = (f"Eres un ingeniero civil evaluando obras públicas. "
                  f"Basado en esta descripción: '{descripcion_solicitud}' "
                  f"y un nivel de gravedad estructural catalogado como '{nivel_gravedad}', "
                  f"determina la prioridad de atención. "
                  f"Responde estrictamente con una sola palabra: ALTA, MEDIA o BAJA.")

        payload = {
            "model": self.modelo,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            respuesta_ia = data.get("response", "").strip().upper()
            
            # Limpiamos la respuesta por si la IA añade texto extra
            if "ALTA" in respuesta_ia: return "ALTA"
            if "MEDIA" in respuesta_ia: return "MEDIA"
            return "BAJA"
            
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con Ollama: {e}")
            return "PENDIENTE" # Estado de fallback si falla la IA