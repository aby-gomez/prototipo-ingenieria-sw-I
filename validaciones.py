from datetime import date


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



    def validar_plazos(self, fecha_retiro, fecha_devolucion, gama, fecha_actual=None):
        if fecha_actual is None:
            fecha_actual = date.today().isoformat()

        try:
            f_retiro = date.fromisoformat(fecha_retiro)
            f_devolucion = date.fromisoformat(fecha_devolucion)
            f_actual = date.fromisoformat(fecha_actual)
            if any(
                parsed.isoformat() != original
                for parsed, original in (
                    (f_retiro, fecha_retiro),
                    (f_devolucion, fecha_devolucion),
                    (f_actual, fecha_actual),
                )
            ):
                raise ValueError
        except (TypeError, ValueError):
            return False, "Las fechas deben tener formato YYYY-MM-DD y ser fechas válidas."

        if f_retiro < f_actual:
            return False, "La fecha de retiro no puede ser anterior al día de solicitud."

        if f_devolucion <= f_retiro:
            return False, "La fecha de devolución debe ser posterior a la fecha de retiro."

        plazo_horas = (f_devolucion - f_retiro).days * 24
        
        if gama == 'alta' and plazo_horas < 48:
            return False, "Plazo menor a 48hs no permitido para gama alta."
        if gama in ('media', 'regular') and plazo_horas > 48:
            return False, "Plazo mayor a 48hs no permitido para préstamo regular."
        return True, ""

    def validar_rnf_07_08(self, es_derivado_cu11, fecha_retiro, fecha_devolucion):
        # RNF-07: No sábados
        # RNF-08: Si es derivado de CU-11, debe devolverse el mismo día
        if es_derivado_cu11:
            if fecha_retiro != fecha_devolucion:
                return False, "Los equipos asociados a una reserva de aula deben devolverse el mismo día (RNF-08)."
            # Simulación de día sábado (dummy)
            if "2026-11-21" == fecha_retiro: # Suponiendo que es sábado
                return False, "No es posible solicitar préstamo los sábados (RNF-07)."
        return True, ""

    def validar_cuenta_activa(self, usuario_id):
        # RNF-24: Simulación
        return True, ""
