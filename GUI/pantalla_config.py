import sys, os
_GUI_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_GUI_DIR)
if _GUI_DIR  not in sys.path: sys.path.insert(0, _GUI_DIR)
if _ROOT_DIR not in sys.path: sys.path.insert(0, _ROOT_DIR)

"""
PantallaConfig — Etapa 4 LinProd
Permite crear procesos y tareas de forma visual antes de simular.
"""
import pygame
from tema import *
from widgets import Boton, Campo, Label, dibujar_panel, dibujar_texto_ml
from Clases.proceso import Proceso
from Clases.tarea import Tarea
from Clases.lineaproduccion import LineaDeProduccion


class PantallaConfig:
    def __init__(self, fuentes):
        self.f_tit   = fuentes["titulo"]
        self.f_sub   = fuentes["subtitulo"]
        self.f_norm  = fuentes["normal"]
        self.f_small = fuentes["small"]

        self.procesos_data = []
        self.error_msg     = ""
        self.scroll_y      = 0

        self._build_ui()

    # ── Construcción de UI ────────────────────────────────────────────

    def _build_ui(self):
        self.campo_proc  = Campo((40, 142, 280, 36), "Nombre del proceso")
        self.campo_tarea = Campo((40, 248, 200, 36), "Nombre de tarea")
        self.campo_ciclo = Campo((250, 248, 80, 36), "Ciclos", solo_numeros=True)

        self.btn_add_proc  = Boton((40, 188, 280, 38), "+ Agregar Proceso",
                                   color=COLOR_NORMAL, color_texto=BLANCO)
        self.btn_add_tarea = Boton((40, 294, 280, 38), "+ Agregar Tarea",
                                   color=ACENTO2, color_texto=NEGRO)
        self.btn_del_proc  = Boton((40, 342, 135, 34), "[X] Quitar ultimo",
                                   color=ROJO, color_texto=BLANCO)
        self.btn_del_tarea = Boton((185, 342, 135, 34), "[X] Quitar tarea",
                                   color=(160, 40, 40), color_texto=BLANCO)
        self.btn_iniciar   = Boton((40, 612, 280, 50), "[>] INICIAR SIMULACION",
                                   color=ACENTO, color_texto=NEGRO)
        self.btn_demo      = Boton((40, 672, 280, 36), "Cargar demo rapida",
                                   color=GRIS_OSC, color_texto=BLANCO)

        # Parámetros: etiquetas en Y=506, campos en Y=520, breakpoints en Y=568
        self.campo_n_prod  = Campo((40,  534, 130, 36), "Productos", solo_numeros=True)
        self.campo_vel     = Campo((180, 534, 140, 36), "Vel (seg)",  solo_numeros=True)
        self.campo_bp      = Campo((40,  580, 280, 28), "Breakpoints (ej: 5,10,20)")

        self.btn_add_proc.on_click  = self._agregar_proceso
        self.btn_add_tarea.on_click = self._agregar_tarea
        self.btn_del_proc.on_click  = self._quitar_proceso
        self.btn_del_tarea.on_click = self._quitar_ultima_tarea
        self.btn_demo.on_click      = self._cargar_demo

        self.on_iniciar = None

    # ── Acciones ──────────────────────────────────────────────────────

    def _agregar_proceso(self):
        nombre = self.campo_proc.get_valor()
        if not nombre:
            self.error_msg = "Escribi un nombre para el proceso."
            return
        self.procesos_data.append({"nombre": nombre, "tareas": []})
        self.campo_proc.limpiar()
        self.error_msg = ""

    def _agregar_tarea(self):
        if not self.procesos_data:
            self.error_msg = "Primero crea al menos un proceso."
            return
        nombre = self.campo_tarea.get_valor()
        ciclo  = self.campo_ciclo.get_int(1)
        if not nombre:
            self.error_msg = "Escribi un nombre para la tarea."
            return
        self.procesos_data[-1]["tareas"].append({"nombre": nombre, "ciclo": ciclo})
        self.campo_tarea.limpiar()
        self.campo_ciclo.limpiar()
        self.error_msg = ""

    def _quitar_proceso(self):
        if self.procesos_data:
            self.procesos_data.pop()
        self.error_msg = ""

    def _quitar_ultima_tarea(self):
        if self.procesos_data and self.procesos_data[-1]["tareas"]:
            self.procesos_data[-1]["tareas"].pop()
        self.error_msg = ""

    def _cargar_demo(self):
        self.procesos_data = [
            {"nombre": "Corte",   "tareas": [{"nombre": "Corte-1", "ciclo": 2},
                                              {"nombre": "Corte-2", "ciclo": 3}]},
            {"nombre": "Pintura", "tareas": [{"nombre": "Pintura",  "ciclo": 4},
                                              {"nombre": "Secado",   "ciclo": 2}]},
            {"nombre": "Empaque", "tareas": [{"nombre": "Empaque",  "ciclo": 2},
                                              {"nombre": "Despacho", "ciclo": 1}]},
        ]
        self.campo_n_prod.texto = "6"
        self.campo_vel.texto    = "0.15"
        self.error_msg = ""

    def _construir_linea(self):
        if not self.procesos_data:
            self.error_msg = "Agrega al menos un proceso."
            return None
        for pd in self.procesos_data:
            if not pd["tareas"]:
                self.error_msg = f"El proceso '{pd['nombre']}' no tiene tareas."
                return None

        linea = LineaDeProduccion()
        for i, pd in enumerate(self.procesos_data):
            es_ini = (i == 0)
            es_fin = (i == len(self.procesos_data) - 1)
            proc   = Proceso(pd["nombre"], es_inicial=es_ini, es_final=es_fin)
            for td in pd["tareas"]:
                proc.agregar_tarea(Tarea(td["nombre"], td["ciclo"]))
            linea.agregar_proceso(proc)
        linea.enlazar_procesos()
        return linea

    def intentar_iniciar(self):
        linea = self._construir_linea()
        if linea is None:
            return
        n_prod = self.campo_n_prod.get_int(5)
        vel    = self.campo_vel.get_float(0.2)
        bp_raw = self.campo_bp.get_valor()
        bps    = set()
        for tok in bp_raw.split(","):
            try:
                bps.add(int(tok.strip()))
            except ValueError:
                pass
        if self.on_iniciar:
            self.on_iniciar(linea, n_prod, vel, bps)

    # ── Eventos ───────────────────────────────────────────────────────

    def handle(self, event):
        for w in [self.campo_proc, self.campo_tarea, self.campo_ciclo,
                  self.campo_n_prod, self.campo_vel, self.campo_bp]:
            w.handle(event)
        for b in [self.btn_add_proc, self.btn_add_tarea, self.btn_del_proc,
                  self.btn_del_tarea, self.btn_demo]:
            b.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_iniciar.rect.collidepoint(event.pos):
                self.intentar_iniciar()
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, self.scroll_y - event.y * 20)

    def update(self, dt):
        for w in [self.campo_proc, self.campo_tarea, self.campo_ciclo,
                  self.campo_n_prod, self.campo_vel, self.campo_bp]:
            w.update(dt)

    # ── Dibujo ────────────────────────────────────────────────────────

    def draw(self, surf):
        surf.fill(BG)

        # Titulo
        tit = self.f_tit.render("LinProd", True, ACENTO)
        surf.blit(tit, (40, 30))
        sub = self.f_norm.render("Configuracion de la linea de produccion", True, GRIS_CLR)
        surf.blit(sub, (40, 68))
        pygame.draw.line(surf, PANEL_BORDE, (40, 95), (340, 95), 1)

        # Panel izquierdo
        dibujar_panel(surf, (20, 108, 320, 590), radio=12)

        # Seccion: Proceso
        surf.blit(self.f_small.render("NUEVO PROCESO", True, GRIS_CLR), (40, 120))
        self.campo_proc.draw(surf, self.f_norm)
        self.btn_add_proc.draw(surf, self.f_norm)

        # Seccion: Tarea
        pygame.draw.line(surf, PANEL_BORDE, (40, 232), (320, 232), 1)
        surf.blit(self.f_small.render("NUEVA TAREA (al ultimo proceso)", True, GRIS_CLR), (40, 235))
        self.campo_tarea.draw(surf, self.f_norm)
        self.campo_ciclo.draw(surf, self.f_norm)
        surf.blit(self.f_small.render("ciclos", True, GRIS_CLR), (256, 256))
        self.btn_add_tarea.draw(surf, self.f_norm)
        self.btn_del_proc.draw(surf, self.f_small)
        self.btn_del_tarea.draw(surf, self.f_small)

        # Seccion: Parametros
        pygame.draw.line(surf, PANEL_BORDE, (40, 514), (320, 514), 1)
        surf.blit(self.f_small.render("PARAMETROS DE SIMULACION", True, GRIS_CLR), (40, 517))
        # Etiquetas ENCIMA de los campos (con separacion clara)
        surf.blit(self.f_small.render("Productos", True, GRIS_CLR), (40,  522))
        surf.blit(self.f_small.render("Velocidad", True, GRIS_CLR), (180, 522))
        self.campo_n_prod.draw(surf, self.f_norm)
        self.campo_vel.draw(surf, self.f_norm)
        self.campo_bp.draw(surf, self.f_small)

        # Botones principales
        self.btn_iniciar.draw(surf, self.f_sub)
        self.btn_demo.draw(surf, self.f_small)

        # Error
        if self.error_msg:
            err = self.f_small.render(f"[!] {self.error_msg}", True, ROJO)
            surf.blit(err, (40, 596))

        # Panel derecho: vista previa
        self._dibujar_preview(surf, pygame.Rect(360, 20, ANCHO - 380, ALTO - 40))

    def _dibujar_preview(self, surf, rect):
        dibujar_panel(surf, rect, radio=12)
        surf.blit(self.f_sub.render("Vista previa de la linea", True, BLANCO),
                  (rect.x + 20, rect.y + 16))
        pygame.draw.line(surf, PANEL_BORDE,
                         (rect.x + 20, rect.y + 44),
                         (rect.right - 20, rect.y + 44), 1)

        if not self.procesos_data:
            msg = self.f_norm.render("Agrega procesos para ver la linea aqui.", True, GRIS_CLR)
            surf.blit(msg, msg.get_rect(center=rect.center))
            return

        n      = len(self.procesos_data)
        PAD    = 20
        w_proc = min(180, (rect.width - PAD * 2 - (n - 1) * 16) // n)
        x0     = rect.x + PAD
        y0     = rect.y + 60 - self.scroll_y

        for i, pd in enumerate(self.procesos_data):
            n_tareas = len(pd["tareas"])
            h_proc   = 60 + n_tareas * 28 + 16

            if i == 0:
                col = COLOR_INICIAL
            elif i == len(self.procesos_data) - 1:
                col = COLOR_FINAL
            else:
                col = COLOR_NORMAL

            px = x0 + i * (w_proc + 16)

            # Flecha entre procesos
            if i > 0:
                ax = px - 14
                ay = y0 + 30
                pygame.draw.polygon(surf, ACENTO,
                    [(ax, ay - 6), (ax + 12, ay), (ax, ay + 6)])

            # Recuadro proceso
            pygame.draw.rect(surf, col, (px, y0, w_proc, 32), border_radius=6)
            nombre_txt = self.f_small.render(pd["nombre"], True, NEGRO)
            surf.blit(nombre_txt, nombre_txt.get_rect(centerx=px + w_proc // 2, y=y0 + 8))

            # Badge inicial / final
            if i == 0:
                b = self.f_small.render("INICIAL", True, NEGRO)
                surf.blit(b, (px + 4, y0 + 4))
            if i == len(self.procesos_data) - 1:
                b = self.f_small.render("FINAL", True, NEGRO)
                surf.blit(b, (px + w_proc - b.get_width() - 4, y0 + 4))

            # Tareas
            ty = y0 + 38
            for td in pd["tareas"]:
                tr = pygame.Rect(px + 6, ty, w_proc - 12, 24)
                pygame.draw.rect(surf, PANEL_BORDE, tr, border_radius=4)
                pygame.draw.rect(surf, GRIS_OSC, tr, width=1, border_radius=4)
                tnombre = f"{td['nombre']} ({td['ciclo']}c)"
                tt = self.f_small.render(tnombre, True, BLANCO)
                surf.blit(tt, tt.get_rect(centery=tr.centery, x=tr.x + 6))
                ty += 28

            if not pd["tareas"]:
                msg = self.f_small.render("sin tareas", True, AMARILLO)
                surf.blit(msg, (px + 8, y0 + 40))