"""
ConfiguradorConsola
───────────────────
Permite armar la LineaDeProduccion interactivamente desde la terminal.
Este módulo será reemplazado por la GUI en la Etapa 4,
pero comparte la misma interfaz de salida: devuelve una LineaDeProduccion lista.
"""
from tarea import Tarea
from proceso import Proceso
from lineaproduccion import LineaDeProduccion


# ── Helpers de input ─────────────────────────────────────────────────

def _pedir_str(prompt: str, minlen: int = 1) -> str:
    while True:
        val = input(prompt).strip()
        if len(val) >= minlen:
            return val
        print(f"  ✗ Debe tener al menos {minlen} carácter(es).")


def _pedir_int(prompt: str, minval: int = 1, maxval: int = None) -> int:
    while True:
        try:
            val = int(input(prompt).strip())
            if val < minval:
                raise ValueError
            if maxval is not None and val > maxval:
                raise ValueError
            return val
        except ValueError:
            rango = f"[{minval}..{maxval}]" if maxval else f"≥ {minval}"
            print(f"  ✗ Ingrese un entero {rango}.")


def _pedir_bool(prompt: str) -> bool:
    while True:
        val = input(prompt + " (s/n): ").strip().lower()
        if val in ("s", "si", "sí", "y", "yes"):
            return True
        if val in ("n", "no"):
            return False
        print("  ✗ Responda 's' o 'n'.")


# ── Configuración de tareas ──────────────────────────────────────────

def _configurar_tareas(nombre_proceso: str) -> list:
    tareas = []
    print(f"\n  Configurando tareas para '{nombre_proceso}'")
    n = _pedir_int("  ¿Cuántas tareas tendrá este proceso? ", minval=1)
    for i in range(1, n + 1):
        print(f"\n    Tarea {i}/{n}")
        nombre = _pedir_str(f"    Nombre de la tarea: ")
        ciclo  = _pedir_int(f"    Tiempo de ciclo (ciclos enteros): ", minval=1)
        tareas.append(Tarea(nombre, ciclo))
    return tareas


# ── Configuración de procesos ────────────────────────────────────────

def _configurar_proceso(indice: int, total: int) -> Proceso:
    print(f"\n{'─'*50}")
    print(f"  Proceso {indice}/{total}")
    nombre     = _pedir_str("  Nombre del proceso: ")
    es_inicial = (indice == 1)          # el primero siempre es inicial
    es_final   = (indice == total)      # el último siempre es final

    if es_inicial:
        print("  → Marcado automáticamente como proceso INICIAL")
    if es_final:
        print("  → Marcado automáticamente como proceso FINAL")

    proceso = Proceso(nombre, es_inicial=es_inicial, es_final=es_final)
    for tarea in _configurar_tareas(nombre):
        proceso.agregar_tarea(tarea)
    return proceso


# ── Punto de entrada principal ───────────────────────────────────────

def configurar_linea() -> LineaDeProduccion:
    """
    Guía al usuario paso a paso para armar una LineaDeProduccion.
    Retorna la línea lista para pasarla al Simulador.
    """
    print("\n" + "═"*50)
    print("  CONFIGURACIÓN DE LA LÍNEA DE PRODUCCIÓN")
    print("═"*50)

    n_procesos = _pedir_int("\n  ¿Cuántos procesos tendrá la línea? ", minval=1)

    linea = LineaDeProduccion()
    for i in range(1, n_procesos + 1):
        proceso = _configurar_proceso(i, n_procesos)
        linea.agregar_proceso(proceso)

    linea.enlazar_procesos()

    # Resumen
    print("\n" + "═"*50)
    print("  RESUMEN DE LA LÍNEA CONFIGURADA")
    print("═"*50)
    for p in linea.procesos:
        flags = []
        if p.es_inicial: flags.append("INICIAL")
        if p.es_final:   flags.append("FINAL")
        tag = f" [{', '.join(flags)}]" if flags else ""
        print(f"\n  ▶ {p.nombre}{tag}")
        for t in p.tareas:
            print(f"      • {t.nombre} — {t.tiempo_ciclo} ciclo(s)")

    print("\n" + "═"*50)
    return linea