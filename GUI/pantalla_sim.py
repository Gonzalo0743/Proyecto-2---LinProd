"""
PantallaSimulacion — visualización en tiempo real de la línea de producción.
Muestra cada proceso/tarea con su estado, productos en cola y barra de progreso global.
"""
import pygame
import math
from tema import *
from widgets import Boton, dibujar_panel, dibujar_barra


class PantallaSimulacion:
    def __init__(self, fuentes, simulador, motor):
        self.f_tit   = fuentes["titulo"]
        self.f_sub   = fuentes["subtitulo"]
        self.f_norm  = fuentes["normal"]
        self.f_small = fuentes["small"]

        self.sim   = simulador
        self.motor = motor

        # Animación: partículas de producto completado
        self.particulas = []
        self._prev_completados = 0

        # Pulso de tareas activas
        self._tick_anim = 0

        self._build_ui()

    def _build_ui(self):
        BY = ALTO - 60
        self.btn_pausa    = Boton((40,  BY, 130, 40), "[||] Pausar",  color=AMARILLO, color_texto=NEGRO)
        self.btn_reanudar = Boton((180, BY, 130, 40), "[>] Reanudar", color=VERDE,   color_texto=NEGRO)
        self.btn_snapshot = Boton((320, BY, 130, 40), "[S] Snapshot", color=ACENTO2, color_texto=NEGRO)
        self.btn_fin      = Boton((ANCHO - 180, BY, 150, 40), "[X] Terminar", color=ROJO, color_texto=BLANCO)

        self.btn_pausa.on_click    = self.motor.pausar
        self.btn_reanudar.on_click = self.motor.reanudar
        self.btn_snapshot.on_click = self._tomar_snapshot
        self.btn_fin.on_click      = self._pedir_fin

        self.on_fin      = None   # callback → App
        self.snapshot_msg = ""
        self._snap_timer  = 0
        self._pedir_terminar = False

    def _tomar_snapshot(self):
        self.sim.imprimir_snapshot()   # imprime en consola
        self.snapshot_msg = f"Snapshot en ciclo {self.sim.ciclo_actual} (ver consola)"
        self._snap_timer  = 3000

    def _pedir_fin(self):
        self._pedir_terminar = True

    # ── Eventos ───────────────────────────────────────────────────────

    def handle(self, event):
        for b in [self.btn_pausa, self.btn_reanudar, self.btn_snapshot, self.btn_fin]:
            b.handle(event)

    # ── Update ────────────────────────────────────────────────────────

    def update(self, dt):
        self._tick_anim += dt * 0.003

        # Partículas al completar un producto
        completados = len(self.sim.productos_completados)
        if completados > self._prev_completados:
            for _ in range(12):
                import random
                self.particulas.append({
                    "x": ANCHO - 80, "y": 80,
                    "vx": random.uniform(-3, 3),
                    "vy": random.uniform(-4, -1),
                    "vida": 1.0,
                    "color": random.choice([VERDE, ACENTO, AMARILLO, ACENTO2]),
                    "r": random.randint(3, 7),
                })
            self._prev_completados = completados

        # Actualizar partículas
        for p in self.particulas:
            p["x"]   += p["vx"]
            p["y"]   += p["vy"]
            p["vy"]  += 0.15
            p["vida"] -= dt * 0.0015
        self.particulas = [p for p in self.particulas if p["vida"] > 0]

        if self._snap_timer > 0:
            self._snap_timer -= dt

        if self._pedir_terminar:
            self._pedir_terminar = False
            self.motor.detener()
            if self.on_fin:
                self.on_fin()

    # ── Dibujo ────────────────────────────────────────────────────────

    def draw(self, surf):
        surf.fill(BG)

        # Título y estado global
        self._dibujar_header(surf)

        # Línea de producción
        self._dibujar_linea(surf, pygame.Rect(20, 120, ANCHO - 40, ALTO - 200))

        # Partículas
        for p in self.particulas:
            alpha = int(p["vida"] * 255)
            color = (*p["color"][:3], alpha)
            pygame.draw.circle(surf, p["color"], (int(p["x"]), int(p["y"])), p["r"])

        # Barra de control inferior
        self._dibujar_barra_control(surf)

    def _dibujar_header(self, surf):
        # Fondo header
        pygame.draw.rect(surf, PANEL, (0, 0, ANCHO, 110))
        pygame.draw.line(surf, PANEL_BORDE, (0, 110), (ANCHO, 110), 1)

        estado_txt = "[||] PAUSADO" if self.motor.esta_pausado() else "[>] SIMULANDO"
        color_est  = AMARILLO    if self.motor.esta_pausado() else VERDE
        surf.blit(self.f_tit.render("LinProd", True, ACENTO), (30, 18))
        surf.blit(self.f_sub.render(estado_txt, True, color_est), (200, 26))

        # Ciclo actual
        ciclo_str = f"Ciclo  {self.sim.ciclo_actual}"
        surf.blit(self.f_sub.render(ciclo_str, True, BLANCO), (ANCHO - 300, 14))

        # Barra de progreso global
        total      = max(1, len(self.sim.productos))
        completado = len(self.sim.productos_completados)
        progreso   = completado / total

        surf.blit(self.f_small.render(
            f"Productos: {completado}/{total}  - por entrar: {len(self.sim.cola_entrada)}",
            True, GRIS_CLR), (ANCHO - 300, 48))

        dibujar_barra(surf, pygame.Rect(ANCHO - 300, 70, 260, 14), progreso)

    def _dibujar_linea(self, surf, contenedor):
        procesos = self.sim.linea.procesos
        n        = len(procesos)
        if n == 0:
            return

        PAD   = 16
        W_MAX = 200
        w_p   = min(W_MAX, (contenedor.width - PAD * (n + 1)) // n)
        h_max = contenedor.height - 20

        for i, proc in enumerate(procesos):
            n_tareas = len(proc.tareas)
            h_p      = min(h_max, 50 + n_tareas * 70 + 20)
            x        = contenedor.x + PAD + i * (w_p + PAD)
            y        = contenedor.y + (h_max - h_p) // 2

            # Color del proceso
            if proc.es_inicial:
                col_proc = COLOR_INICIAL
            elif proc.es_final:
                col_proc = COLOR_FINAL
            else:
                col_proc = COLOR_NORMAL

            # Flecha entre procesos
            if i > 0:
                ax = x - PAD
                ay = y + 25
                pygame.draw.line(surf, ACENTO, (x - PAD, ay), (x - 2, ay), 2)
                pygame.draw.polygon(surf, ACENTO,
                    [(x - 2, ay - 5), (x + 6, ay), (x - 2, ay + 5)])

            # Recuadro proceso
            proc_rect = pygame.Rect(x, y, w_p, h_p)
            dibujar_panel(surf, proc_rect, color=PANEL, borde=col_proc, radio=10, grosor=2)

            # Header proceso
            header = pygame.Rect(x, y, w_p, 34)
            pygame.draw.rect(surf, col_proc, header,
                             border_top_left_radius=10, border_top_right_radius=10)
            nt = self.f_small.render(proc.nombre, True, NEGRO)
            surf.blit(nt, nt.get_rect(center=header.center))

            # Tareas
            ty = y + 40
            for j, tarea in enumerate(proc.tareas):
                self._dibujar_tarea(surf, tarea, x + 8, ty, w_p - 16)
                ty += 68

    def _dibujar_tarea(self, surf, tarea, x, y, w):
        H = 60
        rect = pygame.Rect(x, y, w, H)

        # Color según estado
        if tarea.esta_procesando:
            pulso  = 0.5 + 0.5 * math.sin(self._tick_anim * 4 + id(tarea) * 0.001)
            r, g, b = ACENTO2
            col_borde = (int(r * pulso), int(g * pulso), int(b))
            col_bg    = (20, 40, 50)
        elif len(tarea.cola) > 0:
            col_borde = AMARILLO
            col_bg    = (40, 35, 15)
        else:
            col_borde = GRIS_OSC
            col_bg    = PANEL

        pygame.draw.rect(surf, col_bg,    rect, border_radius=6)
        pygame.draw.rect(surf, col_borde, rect, width=2, border_radius=6)

        # Nombre tarea
        nt = self.f_small.render(tarea.nombre, True, BLANCO)
        surf.blit(nt, (x + 6, y + 4))

        # Tiempo ciclo
        ct = self.f_small.render(f"{tarea.tiempo_ciclo}c", True, GRIS_CLR)
        surf.blit(ct, (x + w - ct.get_width() - 6, y + 4))

        # Producto en proceso
        if tarea.producto_actual:
            pid  = f"#{tarea.producto_actual.id}"
            pt   = self.f_norm.render(pid, True, ACENTO2)
            surf.blit(pt, (x + 6, y + 20))

            # Mini barra de progreso de la tarea
            prog = 1 - (tarea.ciclos_restantes / tarea.tiempo_ciclo)
            dibujar_barra(surf, pygame.Rect(x + 6, y + H - 14, w - 12, 8),
                          prog, color=ACENTO2)
            cr = self.f_small.render(f"{tarea.ciclos_restantes}c rest.", True, GRIS_CLR)
            surf.blit(cr, (x + w - cr.get_width() - 6, y + 20))
        else:
            libre = self.f_small.render("libre", True, GRIS_CLR)
            surf.blit(libre, libre.get_rect(centerx=x + w // 2, y=y + 22))

        # Cola de espera
        if tarea.cola:
            cola_str = f"cola: {len(tarea.cola)}"
            cola_surf = self.f_small.render(cola_str, True, AMARILLO)
            surf.blit(cola_surf, (x + 6, y + H - 18))

    def _dibujar_barra_control(self, surf):
        pygame.draw.rect(surf, PANEL, (0, ALTO - 70, ANCHO, 70))
        pygame.draw.line(surf, PANEL_BORDE, (0, ALTO - 70), (ANCHO, ALTO - 70), 1)

        for b in [self.btn_pausa, self.btn_reanudar, self.btn_snapshot, self.btn_fin]:
            b.draw(surf, self.f_norm)

        if self._snap_timer > 0:
            msg = self.f_small.render(self.snapshot_msg, True, ACENTO2)
            surf.blit(msg, (480, ALTO - 45))