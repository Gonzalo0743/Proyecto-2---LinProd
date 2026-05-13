"""
LinProd GUI — Etapa 4
App principal pygame. Orquesta Config → Simulación → Reporte.
Ejecutar con:  python gui_app.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import pygame
from GUI.tema import *
from pantalla_config  import PantallaConfig
from pantalla_sim     import PantallaSimulacion
from pantalla_reporte import PantallaReporte
from Clases.simulador import Simulador
from Clases.motorciclos import MotorCiclos


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("LinProd — Simulador de Línea de Producción")

        # Fuentes
        self.fuentes = self._cargar_fuentes()

        # Estado
        self.pantalla_actual = "config"   # "config" | "sim" | "reporte"
        self.linea_actual    = None
        self.sim             = None
        self.motor           = None

        # Pantallas
        self.p_config  = PantallaConfig(self.fuentes)
        self.p_sim     = None
        self.p_reporte = None

        # Conectar callbacks de config
        self.p_config.on_iniciar = self._iniciar_simulacion

        self.clock = pygame.time.Clock()

    # ── Fuentes ───────────────────────────────────────────────────────

    def _cargar_fuentes(self):
        # Usa la fuente monoespaciada del sistema como fallback robusto
        try:
            ruta = pygame.font.match_font("consolas,dejavusansmono,ubuntumono,monospace")
            return {
                "titulo":    pygame.font.Font(ruta, T_TITULO),
                "subtitulo": pygame.font.Font(ruta, T_SUBTIT),
                "normal":    pygame.font.Font(ruta, T_NORMAL),
                "small":     pygame.font.Font(ruta, T_SMALL),
            }
        except Exception:
            return {
                "titulo":    pygame.font.SysFont("monospace", T_TITULO,  bold=True),
                "subtitulo": pygame.font.SysFont("monospace", T_SUBTIT,  bold=True),
                "normal":    pygame.font.SysFont("monospace", T_NORMAL),
                "small":     pygame.font.SysFont("monospace", T_SMALL),
            }

    # ── Transiciones de pantalla ──────────────────────────────────────

    def _iniciar_simulacion(self, linea, n_prod, vel, breakpoints):
        self.linea_actual = linea
        self.sim          = Simulador(linea)
        self.sim.iniciar(n_prod)

        self.motor = MotorCiclos(self.sim, velocidad=vel)
        for bp in breakpoints:
            self.motor.agregar_breakpoint(bp)

        def on_fin(s):
            pass   # la pantalla de sim detecta terminación y ofrece ir al reporte

        self.motor.on_fin = on_fin

        self.p_sim = PantallaSimulacion(self.fuentes, self.sim, self.motor)
        self.p_sim.on_fin = self._ir_a_reporte

        self.motor.correr_en_hilo()
        self.pantalla_actual = "sim"

    def _ir_a_reporte(self):
        if self.motor.esta_corriendo():
            self.motor.detener()
        self.p_reporte = PantallaReporte(self.fuentes, self.sim)
        self.p_reporte.on_reiniciar   = self._reiniciar
        self.p_reporte.on_nueva_linea = self._nueva_linea
        self.pantalla_actual = "reporte"

    def _reiniciar(self):
        """Vuelve a la pantalla de config con la misma línea cargada."""
        # Pre-poblar campos con los datos anteriores
        self.p_config = PantallaConfig(self.fuentes)
        self.p_config.on_iniciar = self._iniciar_simulacion
        # Reconstruir procesos_data desde la línea actual
        if self.linea_actual:
            for p in self.linea_actual.procesos:
                self.p_config.procesos_data.append({
                    "nombre": p.nombre,
                    "tareas": [{"nombre": t.nombre, "ciclo": t.tiempo_ciclo}
                               for t in p.tareas]
                })
        self.pantalla_actual = "config"

    def _nueva_linea(self):
        self.p_config = PantallaConfig(self.fuentes)
        self.p_config.on_iniciar = self._iniciar_simulacion
        self.pantalla_actual = "config"

    # ── Loop principal ────────────────────────────────────────────────

    def run(self):
        while True:
            dt = self.clock.tick(FPS)

            # ── Verificar terminación automática en sim ───────────────
            if (self.pantalla_actual == "sim"
                    and self.sim is not None
                    and self.sim.esta_terminado()
                    and not self.motor.esta_corriendo()
                    and self.p_reporte is None):
                self._ir_a_reporte()

            # ── Eventos ───────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.motor and self.motor.esta_corriendo():
                        self.motor.detener()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.pantalla_actual == "sim":
                            self._ir_a_reporte()
                        elif self.pantalla_actual == "reporte":
                            self._nueva_linea()

                if self.pantalla_actual == "config":
                    self.p_config.handle(event)
                elif self.pantalla_actual == "sim" and self.p_sim:
                    self.p_sim.handle(event)
                elif self.pantalla_actual == "reporte" and self.p_reporte:
                    self.p_reporte.handle(event)

            # ── Update ────────────────────────────────────────────────
            if self.pantalla_actual == "config":
                self.p_config.update(dt)
            elif self.pantalla_actual == "sim" and self.p_sim:
                self.p_sim.update(dt)
            elif self.pantalla_actual == "reporte" and self.p_reporte:
                self.p_reporte.update(dt)

            # ── Draw ──────────────────────────────────────────────────
            if self.pantalla_actual == "config":
                self.p_config.draw(self.screen)
            elif self.pantalla_actual == "sim" and self.p_sim:
                self.p_sim.draw(self.screen)
            elif self.pantalla_actual == "reporte" and self.p_reporte:
                self.p_reporte.draw(self.screen)

            pygame.display.flip()


if __name__ == "__main__":
    App().run()