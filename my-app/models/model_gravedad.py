import re

class GravedadObraModel:
    def __init__(self, nivel_gravedad, criticidad, estado=1, id_gravedad=None):
        # Atributos privados (Encapsulamiento)
        self.__id_gravedad = id_gravedad
        self.__nivel_gravedad = nivel_gravedad
        self.__criticidad = criticidad
        self.__estado = estado

    # Getters
    def get_nivel_gravedad(self):
        return self.__nivel_gravedad

    # Setters con validación Regex (Backend Robusto)
    def set_nivel_gravedad(self, valor):
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,20}$', valor):
            raise ValueError("Formato de gravedad inválido. Solo letras permitidas.")
        self.__nivel_gravedad = valor

    # MÉTODO PRIVADO de modificación a BD
    def __registrar(self, cursor):
        sql = """INSERT INTO gravedad_obra (nivel_gravedad, criticidad, estado) 
                 VALUES (%s, %s, %s)"""
        valores = (self.__nivel_gravedad, self.__criticidad, self.__estado)
        cursor.execute(sql, valores)
        return True

    # MÉTODO PÚBLICO que invoca al privado (Capa de seguridad)
    def registrar_gravedad(self, cursor):
        return self.__registrar(cursor)

    # MÉTODO PRIVADO para Borrado Lógico
    def __eliminar_logico(self, cursor):
        sql = "UPDATE gravedad_obra SET estado = 0 WHERE id_gravedad = %s"
        cursor.execute(sql, (self.__id_gravedad,))
        return True
        
    # MÉTODO PÚBLICO para Borrado Lógico
    def eliminar_gravedad(self, cursor):
        return self.__eliminar_logico(cursor)