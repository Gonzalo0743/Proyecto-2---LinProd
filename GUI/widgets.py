"""
Widgets básicos reutilizables para LinProd GUI.
Cada widget se dibuja llamando a .draw(surface) y recibe eventos con .handle(event).
"""
import pygame
from GUI.tema import *


# ── Botón ────────────────────────────────────────────────────────────

class Boton:
    def __init__(self, rect, texto, color=ACENTO, color_texto=NEGRO,
                 radio=8, fuente=None, activo=True):
        self.rect       = pygame.Rect(rect)
        self.texto      = texto
        self.color      = color
        self.color_txt  = color_texto
        self.radio      = radio
        self.fuente     = fuente
        self.activo     = activo
        self._hover     = False
        self.on_click   = None          # callback sin argumentos

    def handle(self, event):
        if not self.activo:
            return
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

    def draw(self, surf, fuente):
        f = self.fuente or fuente
        color = self.color if self.activo else GRIS_OSC
        if self._hover and self.activo:
            color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(surf, color, self.rect, border_radius=self.radio)
        txt = f.render(self.texto, True, self.color_txt if self.activo else GRIS_CLR)
        surf.blit(txt, txt.get_rect(center=self.rect.center))


# ── Campo de texto ────────────────────────────────────────────────────

class Campo:
    def __init__(self, rect, placeholder="", solo_numeros=False, fuente=None):
        self.rect          = pygame.Rect(rect)
        self.placeholder   = placeholder
        self.solo_numeros  = solo_numeros
        self.fuente        = fuente
        self.texto         = ""
        self.activo        = False
        self._cursor_vis   = True
        self._cursor_timer = 0

    def get_valor(self):
        return self.texto.strip()

    def get_int(self, defecto=1):
        try:
            return max(1, int(self.texto.strip()))
        except ValueError:
            return defecto

    def get_float(self, defecto=0.2):
        try:
            return max(0.0, float(self.texto.strip()))
        except ValueError:
            return defecto

    def limpiar(self):
        self.texto = ""

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.activo:
            if event.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif event.key == pygame.K_RETURN:
                self.activo = False
            else:
                ch = event.unicode
                if self.solo_numeros:
                    if ch.isdigit() or (ch == '.' and '.' not in self.texto):
                        self.texto += ch
                else:
                    if ch.isprintable():
                        self.texto += ch

    def update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer > 500:
            self._cursor_vis   = not self._cursor_vis
            self._cursor_timer = 0

    def draw(self, surf, fuente):
        f = self.fuente or fuente
        borde = ACENTO2 if self.activo else PANEL_BORDE
        pygame.draw.rect(surf, PANEL, self.rect, border_radius=6)
        pygame.draw.rect(surf, borde, self.rect, width=2, border_radius=6)

        mostrar = self.texto
        if not mostrar:
            txt = f.render(self.placeholder, True, GRIS_CLR)
        else:
            cursor = "|" if (self.activo and self._cursor_vis) else ""
            txt = f.render(mostrar + cursor, True, BLANCO)
        surf.blit(txt, (self.rect.x + 10, self.rect.centery - txt.get_height() // 2))


# ── Etiqueta ─────────────────────────────────────────────────────────

class Label:
    def __init__(self, pos, texto, color=BLANCO, fuente=None, alineacion="izq"):
        self.pos        = pos
        self.texto      = texto
        self.color      = color
        self.fuente     = fuente
        self.alineacion = alineacion

    def draw(self, surf, fuente):
        f = self.fuente or fuente
        txt = f.render(str(self.texto), True, self.color)
        if self.alineacion == "centro":
            surf.blit(txt, txt.get_rect(centerx=self.pos[0], y=self.pos[1]))
        elif self.alineacion == "der":
            surf.blit(txt, txt.get_rect(right=self.pos[0], y=self.pos[1]))
        else:
            surf.blit(txt, self.pos)


# ── Panel con borde redondeado ────────────────────────────────────────

def dibujar_panel(surf, rect, color=PANEL, borde=PANEL_BORDE, radio=10, grosor=1):
    pygame.draw.rect(surf, color, rect, border_radius=radio)
    if grosor:
        pygame.draw.rect(surf, borde, rect, width=grosor, border_radius=radio)


# ── Barra de progreso ─────────────────────────────────────────────────

def dibujar_barra(surf, rect, progreso, color=VERDE, fondo=GRIS_OSC, radio=4):
    """progreso: 0.0 a 1.0"""
    pygame.draw.rect(surf, fondo, rect, border_radius=radio)
    if progreso > 0:
        w = max(radio * 2, int(rect.width * min(1.0, progreso)))
        relleno = pygame.Rect(rect.x, rect.y, w, rect.height)
        pygame.draw.rect(surf, color, relleno, border_radius=radio)


# ── Texto multilínea ──────────────────────────────────────────────────

def dibujar_texto_ml(surf, texto, fuente, color, rect, interlineado=4):
    """Dibuja texto con saltos de línea respetando el ancho del rect."""
    palabras = texto.split(" ")
    lineas   = []
    linea    = ""
    for p in palabras:
        prueba = linea + (" " if linea else "") + p
        if fuente.size(prueba)[0] <= rect.width:
            linea = prueba
        else:
            if linea:
                lineas.append(linea)
            linea = p
    if linea:
        lineas.append(linea)

    y = rect.y
    for l in lineas:
        if y + fuente.get_height() > rect.bottom:
            break
        surf.blit(fuente.render(l, True, color), (rect.x, y))
        y += fuente.get_height() + interlineado