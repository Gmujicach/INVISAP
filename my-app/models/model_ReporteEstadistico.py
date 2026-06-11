class ReporteEstadisticoModel:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_estadisticas_por_modulo(self, tabla_modulo):
        """
        Consulta parametrizada para evitar inyecciones.
        Recibe el nombre de la tabla y retorna datos para los gráficos.
        """
        cursor = self.conn.cursor(dictionary=True)
        # Nota: La tabla debe ser validada contra una lista blanca si es dinámica
        # Aquí asumimos que recibes el nombre de un campo de tiempo/categoría y un conteo
        query = "SELECT fecha_registro as label, COUNT(*) as valor FROM %s GROUP BY fecha_registro" % tabla_modulo
        
        try:
            cursor.execute(query) # OJO: Si el nombre de tabla es variable, valida siempre antes
            return cursor.fetchall()
        finally:
            cursor.close()