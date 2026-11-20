class ValidadorSolicitud:
    def __init__(self, db_path='prestamos.db'):
        self.db_path = db_path

    def validar_gama(self, equipos):
        # Exclusividad de gama: No se puede mezclar
        gamas = set([e['gama'] for e in equipos])
        if len(gamas) > 1:
            return False, "No es posible mezclar gamas en una misma solicitud."
        return True, ""

    def validar_restriccion_alta(self, usuario_año, equipos):
        # Alumno 1er/2do año no puede gama alta
        for e in equipos:
            if e['gama'] == 'alta' and usuario_año < 3:
                return False, "Equipo reservado para alumnos de 3er año o superior y docentes."
        return True, ""

    def validar_plazos(self, fecha_retiro, fecha_devolucion, gama):
        # Simulación de cálculo de horas (dummy)
        # En una implementación real, calcularía diferencia entre fechas
        plazo_horas = 24 # Dummy
        
        if gama == 'alta' and plazo_horas < 48:
            return False, "Plazo menor a 48hs no permitido para gama alta."
        if gama == 'regular' and plazo_horas > 48:
            return False, "Plazo mayor a 48hs no permitido para préstamo regular."
        return True, ""
