"""
LinProd — main.py  (Etapa 3)
─────────────────────────────
Programa principal de consola.
Flujo:
  1. Configurar línea (interactivo o demo rápida)
  2. Configurar simulación (n productos, velocidad, breakpoints)
  3. Correr con control en tiempo real (p=pausa, r=reanuda, q=salir)
  4. Reporte final
  5. Opción de reinicializar o modificar la línea
"""
import sys
import os
import threading
import time
sys.path.insert(0, os.path.dirname(__file__))

from configurarconsola import configurar_linea
from simulador import Simulador
from motorciclos import MotorCiclos
from reporte import Reporte
from lineaproduccion import LineaDeProduccion
from proceso import Proceso
from tarea import Tarea


# ── Demo rápida (sin preguntas) ──────────────────────────────────────

def _linea_demo() -> LineaDeProduccion:
    """Línea prefabricada para pruebas rápidas."""
    linea = LineaDeProduccion()
    pA = Proceso("Corte",     es_inicial=True)
    pA.agregar_tarea(Tarea("Corte-1",  2))
    pA.agregar_tarea(Tarea("Corte-2",  3))
    linea.agregar_proceso(pA)

    pB = Proceso("Pintura")
    pB.agregar_tarea(Tarea("Pintura",  4))
    pB.agregar_tarea(Tarea("Secado",   2))
    linea.agregar_proceso(pB)

    pC = Proceso("Empaque",   es_final=True)
    pC.agregar_tarea(Tarea("Empaque",  2))
    pC.agregar_tarea(Tarea("Despacho", 1))
    linea.agregar_proceso(pC)

    linea.enlazar_procesos()
    return linea


# ── Input no bloqueante (detecta tecla sin Enter en Unix) ────────────

def _leer_comando_no_bloqueante() -> str:
    """
    Retorna el próximo carácter tipeado, o '' si no hay nada.
    Funciona en Linux/Mac. En Windows usa msvcrt.
    """
    try:
        import select
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            return sys.stdin.readline().strip().lower()
    except Exception:
        pass
    return ""


# ── Loop de consola con control en tiempo real ───────────────────────

def _correr_con_control(motor: MotorCiclos, sim: Simulador):
    """
    Corre el motor en un hilo separado.
    Lee comandos del usuario en un hilo aparte para no bloquear:
      p  → pausa
      r  → reanuda
      s  → snapshot inmediato
      q  → terminar
    """
    print("\n  Controles: [p] pausar  [r] reanudar  [s] snapshot  [q] salir")
    print("  (escribe el comando y presiona Enter)\n")

    cancelado = threading.Event()
    terminado = threading.Event()

    def leer_comandos():
        while not terminado.is_set():
            try:
                cmd = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                cancelado.set()
                terminado.set()
                motor.detener()
                return

            if cmd == "p":
                motor.pausar()
                print(f"\n  ⏸  Pausado en ciclo {sim.ciclo_actual}.")
                sim.imprimir_snapshot()
            elif cmd == "r":
                motor.reanudar()
                print(f"  ▶  Reanudando desde ciclo {sim.ciclo_actual}...\n")
            elif cmd == "s":
                sim.imprimir_snapshot()
            elif cmd == "q":
                cancelado.set()
                terminado.set()
                motor.detener()
                print("\n  Simulación cancelada por el usuario.")
                return

    hilo_input = threading.Thread(target=leer_comandos, daemon=True)
    hilo_input.start()

    motor.correr_en_hilo()

    # Esperar a que el motor termine o el usuario cancele
    while motor.esta_corriendo() and not cancelado.is_set():
        time.sleep(0.05)

    terminado.set()   # señala al hilo de input que puede salir

    if cancelado.is_set():
        return False
    return True


# ── Flujo principal ──────────────────────────────────────────────────

def main():
    print("\n" + "╔" + "═"*48 + "╗")
    print("║" + "  LinProd — Simulador de Línea de Producción  ".center(48) + "║")
    print("╚" + "═"*48 + "╝")

    # ── 1. Obtener línea ─────────────────────────────────────────────
    print("\n  ¿Cómo querés configurar la línea?")
    print("  [1] Configurar manualmente")
    print("  [2] Usar línea de demostración (3 procesos, 7 tareas)")
    opcion = input("\n  Opción: ").strip()

    linea = _linea_demo() if opcion != "1" else configurar_linea()

    while True:   # bucle para reinicializar / modificar
        # ── 2. Configurar simulación ─────────────────────────────────
        print("\n" + "═"*50)
        print("  CONFIGURACIÓN DE LA SIMULACIÓN")
        print("═"*50)
        n_prod = int(input("\n  ¿Cuántos productos entrarán a la línea? ").strip() or "5")
        vel    = float(input("  Velocidad (segundos entre ciclos, ej. 0.2): ").strip() or "0.2")

        bp_str = input("  Ciclos de pausa automática (ej: 5,10,20 — Enter para ninguno): ").strip()
        breakpoints = set()
        if bp_str:
            for token in bp_str.split(","):
                try:
                    breakpoints.add(int(token.strip()))
                except ValueError:
                    pass

        # ── 3. Iniciar ───────────────────────────────────────────────
        sim = Simulador(linea)
        sim.iniciar(n_productos=n_prod)

        motor = MotorCiclos(sim, velocidad=vel)
        for bp in breakpoints:
            motor.agregar_breakpoint(bp)

        # Callback de tick: imprime una línea de progreso
        def on_tick(s: Simulador):
            completados = len(s.productos_completados)
            total       = len(s.productos)
            barra       = "█" * completados + "░" * (total - completados)
            print(f"\r  Ciclo {s.ciclo_actual:4d}  [{barra}] {completados}/{total} completados   ",
                  end="", flush=True)

        def on_pausa(s: Simulador):
            pass   # el snapshot ya lo imprime _correr_con_control

        def on_fin(s: Simulador):
            print()   # salto de línea tras la barra de progreso

        motor.on_tick(on_tick)
        motor.on_pausa(on_pausa)
        motor.on_fin(on_fin)

        # Pausa automática en breakpoints: imprime snapshot
        def hacer_snapshot_en_bp(s: Simulador):
            s.imprimir_snapshot()
            print("  [Pausa automática — escribe 'r' para continuar]\n")

        # Wrappear on_pausa para detectar breakpoints
        _bp_orig = motor._on_pausa
        def on_pausa_bp(s: Simulador):
            if s.ciclo_actual in breakpoints:
                hacer_snapshot_en_bp(s)
        motor._on_pausa = on_pausa_bp

        termino_ok = _correr_con_control(motor, sim)

        # ── 4. Reporte ───────────────────────────────────────────────
        if termino_ok and sim.esta_terminado():
            rep = Reporte(sim)
            rep.mostrar()

        # ── 5. ¿Qué sigue? ───────────────────────────────────────────
        print("\n  ¿Qué querés hacer?")
        print("  [1] Reinicializar con la misma línea y nuevos parámetros")
        print("  [2] Configurar una nueva línea")
        print("  [3] Salir")
        sig = input("\n  Opción: ").strip()

        if sig == "1":
            continue                  # vuelve al inicio del while con la misma línea
        elif sig == "2":
            linea = configurar_linea()
            continue
        else:
            print("\n  ¡Hasta luego!\n")
            break


if __name__ == "__main__":
    main()