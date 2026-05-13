"""
Tema visual para LinProd GUI (pygame)
Paleta industrial-futurista: fondo oscuro, acentos en naranja y cian.
"""

# ── Colores ──────────────────────────────────────────────────────────
BG          = (15,  18,  26)   # fondo principal casi negro
PANEL       = (24,  28,  40)   # paneles y cards
PANEL_BORDE = (40,  46,  64)   # borde de paneles
ACENTO      = (255, 140,  0)   # naranja — proceso activo / botón primario
ACENTO2     = ( 0,  210, 200)  # cian    — tarea activa
VERDE       = ( 50, 220, 120)  # completado
ROJO        = (220,  60,  60)  # error / alerta
AMARILLO    = (255, 210,  50)  # en cola / advertencia
BLANCO      = (230, 235, 245)
GRIS_CLR    = (120, 130, 155)
GRIS_OSC    = ( 55,  62,  82)
NEGRO       = (  0,   0,   0)

# Proceso inicial / final
COLOR_INICIAL = ( 80, 200, 120)
COLOR_FINAL   = (200,  80, 200)
COLOR_NORMAL  = ( 70, 130, 200)

# ── Tipografía (tamaños) ─────────────────────────────────────────────
T_TITULO  = 28
T_SUBTIT  = 18
T_NORMAL  = 14
T_SMALL   = 11

# ── Dimensiones ventana ──────────────────────────────────────────────
ANCHO  = 1100
ALTO   = 720

# ── FPS ─────────────────────────────────────────────────────────────
FPS = 60