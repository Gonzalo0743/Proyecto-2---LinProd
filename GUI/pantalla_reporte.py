import sys, os
_GUI_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_GUI_DIR)
if _GUI_DIR  not in sys.path: sys.path.insert(0, _GUI_DIR)
if _ROOT_DIR not in sys.path: sys.path.insert(0, _ROOT_DIR)

"""
PantallaReporte — muestra las estadisticas finales de forma visual.
"""
import pygame
from tema import *
from widgets import Boton, dibujar_panel, dibujar_barra
from Clases.reporte import Reporte


class PantallaReporte:
    def __init__(self, fuentes, simulador):
        self.f_tit   = fuentes["titulo"]
        self.f_sub   = fuentes["subtitulo"]
        self.f_norm  = fuentes["normal"]
        self.f_small = fuentes["small"]

        self.sim = simulador
        self.rep = Reporte(simulador)
        self.rep.calcular_estadisticas()
        self.d   = self.rep.datos

        self.on_reiniciar   = None
        self.on_nueva_linea = None
        self._export_msg    = ""
        self._export_timer  = 0

        self._build_ui()

    def _build_ui(self):
        y = ALTO - 65
        self.btn_reiniciar = Boton((40,  y, 230, 44), "[R] Reinicializar (misma linea)",
                                   color=COLOR_NORMAL, color_texto=BLANCO)
        self.btn_nueva     = Boton((280, y, 160, 44), "[+] Nueva linea",
                                   color=ACENTO, color_texto=NEGRO)
        self.btn_exportar  = Boton((450, y, 160, 44), "[E] Exportar .txt",
                                   color=ACENTO2, color_texto=NEGRO)
        self.btn_exportar_csv = Boton((620, y, 160, 44), "[C] Exportar .csv",
                                      color=(0, 170, 160), color_texto=NEGRO)
        self.btn_reiniciar.on_click    = lambda: self.on_reiniciar   and self.on_reiniciar()
        self.btn_nueva.on_click        = lambda: self.on_nueva_linea and self.on_nueva_linea()
        self.btn_exportar.on_click     = self._exportar_txt
        self.btn_exportar_csv.on_click = self._exportar_csv

    def _exportar_txt(self):
        ruta = self.rep.exportar("reporte_linprod.txt")
        self._export_msg   = f"Exportado: {ruta}"
        self._export_timer = 4000

    def _exportar_csv(self):
        ruta = self.rep.exportar("reporte_linprod.csv")
        self._export_msg   = f"Exportado: {ruta}"
        self._export_timer = 4000

    def handle(self, event):
        self.btn_reiniciar.handle(event)
        self.btn_nueva.handle(event)
        self.btn_exportar.handle(event)
        self.btn_exportar_csv.handle(event)

    def update(self, dt):
        if self._export_timer > 0:
            self._export_timer -= dt

    def update(self, dt):
        pass

    def draw(self, surf):
        surf.fill(BG)

        # Header
        pygame.draw.rect(surf, PANEL, (0, 0, ANCHO, 80))
        pygame.draw.line(surf, PANEL_BORDE, (0, 80), (ANCHO, 80), 1)
        surf.blit(self.f_tit.render("LinProd", True, ACENTO), (30, 16))
        surf.blit(self.f_sub.render("Reporte Final", True, BLANCO), (200, 22))

        d = self.d
        if "error" in d:
            msg = self.f_norm.render(d["error"], True, ROJO)
            surf.blit(msg, msg.get_rect(center=(ANCHO // 2, ALTO // 2)))
            return

        # Tarjetas de metricas
        metricas = [
            ("Productos completados", f"{d['productos_completados']} / {d['total_productos']}",     VERDE),
            ("Ciclos totales",        str(d["ciclos_totales"]),                                     ACENTO2),
            ("1er producto",          f"{d['tiempo_primer_producto']} ciclos",                      AMARILLO),
            ("Ultimo producto",       f"{d['tiempo_ultimo_producto']} ciclos",                      AMARILLO),
            ("Tiempo promedio",       f"{d['tiempo_promedio']} ciclos",                             ACENTO),
            ("Espera promedio",       f"{d['promedio_espera_global']} ciclos",                      GRIS_CLR),
            ("Tiempo total proc.",    f"{d.get('tiempo_total_procesamiento', '—')} ciclos",         VERDE),
        ]

        COLS = 4
        CW   = (ANCHO - 60) // COLS
        CH   = 90
        for idx, (titulo, valor, color) in enumerate(metricas):
            col = idx % COLS
            row = idx // COLS
            cx  = 30 + col * CW
            cy  = 100 + row * (CH + 12)
            dibujar_panel(surf, pygame.Rect(cx, cy, CW - 10, CH), radio=10)
            t1 = self.f_small.render(titulo.upper(), True, GRIS_CLR)
            t2 = self.f_sub.render(valor, True, color)
            surf.blit(t1, (cx + 16, cy + 14))
            surf.blit(t2, (cx + 16, cy + 36))

        # Cuello de botella
        y0 = 100 + 2 * (CH + 12) + 16
        dibujar_panel(surf, pygame.Rect(30, y0, ANCHO - 60, 70), radio=10)
        surf.blit(self.f_small.render("CUELLO DE BOTELLA", True, ROJO), (50, y0 + 10))
        surf.blit(self.f_norm.render(d["cuello_de_botella"], True, BLANCO), (50, y0 + 32))

        # Tarea con mayor espera
        y1 = y0 + 82
        dibujar_panel(surf, pygame.Rect(30, y1, ANCHO - 60, 70), radio=10)
        surf.blit(self.f_small.render("TAREA CON MAYOR ESPERA", True, AMARILLO), (50, y1 + 10))
        surf.blit(self.f_norm.render(d["tarea_mayor_espera"], True, BLANCO), (50, y1 + 32))

        # Detalle por proceso
        y2 = y1 + 90
        if y2 + 30 < ALTO - 80:
            surf.blit(self.f_small.render("DETALLE POR PROCESO", True, GRIS_CLR), (30, y2))
            xd = 30
            for proc in self.sim.linea.procesos:
                cb       = proc.get_cuello_botella()
                max_c    = cb.max_cola_alcanzada if cb else 0
                total_at = sum(t.productos_atendidos for t in proc.tareas)
                pr = pygame.Rect(xd, y2 + 20, 200, 60)
                dibujar_panel(surf, pr, radio=8)

                if proc.es_inicial:
                    col = COLOR_INICIAL
                elif proc.es_final:
                    col = COLOR_FINAL
                else:
                    col = COLOR_NORMAL

                surf.blit(self.f_small.render(proc.nombre,              True, col),     (xd + 10, y2 + 26))
                surf.blit(self.f_small.render(f"Atendidos: {total_at}", True, BLANCO),  (xd + 10, y2 + 42))
                surf.blit(self.f_small.render(f"Max cola:  {max_c}",
                          True, AMARILLO if max_c > 0 else GRIS_CLR),                   (xd + 10, y2 + 58))
                xd += 210
                if xd + 200 > ANCHO - 20:
                    break

        # Barra de control inferior
        pygame.draw.rect(surf, PANEL, (0, ALTO - 70, ANCHO, 70))
        pygame.draw.line(surf, PANEL_BORDE, (0, ALTO - 70), (ANCHO, ALTO - 70), 1)
        self.btn_reiniciar.draw(surf, self.f_norm)
        self.btn_nueva.draw(surf, self.f_norm)
        self.btn_exportar.draw(surf, self.f_norm)
        self.btn_exportar_csv.draw(surf, self.f_norm)

        if self._export_timer > 0:
            msg = self.f_small.render(self._export_msg, True, VERDE)
            surf.blit(msg, (800, ALTO - 45))
