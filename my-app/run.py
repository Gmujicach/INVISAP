# Declarando nombre del sistema invilara e inicializando, crear la aplicación Flask
from app import app

# Ejecutando el objeto Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5600)
