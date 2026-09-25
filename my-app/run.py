# Declarando nombre del sistema invilara e inicializando, crear la aplicación Flask
import os

from app import app
from services.ia_prioridad_service import iniciar_scheduler

# Ejecutando el objeto Flask
if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        try:
            iniciar_scheduler()
        except Exception as e:
            print(f"[run] No se pudo iniciar el scheduler de prioridad: {e}")
    app.run(host='0.0.0.0', debug=True, port=5600)
