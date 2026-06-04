# Declarando nombre de la aplicación e inicializando, crear la aplicación Flask
from app import app

# Ejecutando el objeto Flask
if __name__ == '__main__':
    app.run(debug=True, port=5600)
