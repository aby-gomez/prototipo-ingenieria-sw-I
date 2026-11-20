import unittest

from validaciones import ValidadorSolicitud


class ValidacionesFechasCU07Test(unittest.TestCase):
    def setUp(self):
        self.validador = ValidadorSolicitud()
        self.hoy = "2026-11-20"

    def validar(self, retiro, devolucion, gama):
        return self.validador.validar_plazos(
            retiro, devolucion, gama, fecha_actual=self.hoy
        )

    def test_TC05_fecha_invalida_o_inexistente(self):
        casos = [
            ("bad", "2026-11-21", "media"),
            ("2026-02-30", "2026-11-21", "media"),
            ("", "2026-11-21", "media"),
            ("2026-11-20", "", "media"),
        ]
        for retiro, devolucion, gama in casos:
            with self.subTest(retiro=retiro, devolucion=devolucion):
                ok, _ = self.validar(retiro, devolucion, gama)
                self.assertFalse(ok)

    def test_TC06_retiro_anterior_al_dia_actual(self):
        ok, mensaje = self.validar("2026-11-19", "2026-11-21", "media")
        self.assertFalse(ok)
        self.assertIn("anterior al día de solicitud", mensaje)

    def test_TC06_devolucion_anterior_o_no_posterior(self):
        ok, _ = self.validar("2026-11-21", "2026-11-20", "media")
        self.assertFalse(ok)

    def test_TC03_plazo_minimo_gama_alta(self):
        ok, _ = self.validar("2026-11-20", "2026-11-21", "alta")
        self.assertFalse(ok)

        ok, _ = self.validar("2026-11-20", "2026-11-22", "alta")
        self.assertTrue(ok)

    def test_plazo_gama_media(self):
        ok, _ = self.validar("2026-11-20", "2026-11-22", "media")
        self.assertTrue(ok)

        ok, _ = self.validar("2026-11-20", "2026-11-23", "media")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
