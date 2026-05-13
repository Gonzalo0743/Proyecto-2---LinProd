"""
Prueba de consola — LinProd Etapa 2
Línea: ProcA (2 tareas) → ProcB (3 tareas) → ProcC (2 tareas)
5 productos, pausa en ciclo 8
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from producto import Producto
from tarea import Tarea
from proceso import Proceso
from lineaproduccion import LineaDeProduccion
from simulador import Simulador
from reporte import Reporte


def construir_linea():
    linea = LineaDeProduccion()

    # ── Proceso A (INICIAL) ──────────────────────────────────────────
    procA = Proceso("ProcA", es_inicial=True)
    procA.agregar_tarea(Tarea("A-Corte",    tiempo_ciclo=2))
    procA.agregar_tarea(Tarea("A-Pulido",   tiempo_ciclo=3))
    linea.agregar_proceso(procA)

    # ── Proceso B ────────────────────────────────────────────────────
    procB = Proceso("ProcB")
    procB.agregar_tarea(Tarea("B-Pintura",  tiempo_ciclo=4))
    procB.agregar_tarea(Tarea("B-Secado",   tiempo_ciclo=2))
    procB.agregar_tarea(Tarea("B-Revisión", tiempo_ciclo=1))
    linea.agregar_proceso(procB)

    # ── Proceso C (FINAL) ────────────────────────────────────────────
    procC = Proceso("ProcC", es_final=True)
    procC.agregar_tarea(Tarea("C-Empaque",  tiempo_ciclo=2))
    procC.agregar_tarea(Tarea("C-Despacho", tiempo_ciclo=1))
    linea.agregar_proceso(procC)

    linea.enlazar_procesos()
    return linea


def main():
    linea = construir_linea()
    sim = Simulador(linea)
    sim.iniciar(n_productos=5)

    print("\n" + "═"*50)
    print("  SIMULACIÓN LinProd — Etapa 2")
    print("═"*50)
    print(f"  Línea configurada con {len(linea.procesos)} procesos")
    print(f"  Productos a procesar: {len(sim.productos)}")
    print("═"*50)

    PAUSA_EN = 8   # ciclo en el que se tomará la "foto"
    MAX_CICLOS = 200

    ciclo = 0
    while not sim.esta_terminado() and ciclo < MAX_CICLOS:
        sim.tick()
        ciclo += 1

        # Pausa automática en ciclo PAUSA_EN
        if ciclo == PAUSA_EN:
            print(f"\n  [PAUSA solicitada en ciclo {PAUSA_EN}]")
            sim.imprimir_snapshot()
            input("  Presiona ENTER para continuar...\n")

    print(f"\n  Simulación terminada en {sim.ciclo_actual} ciclos.")

    rep = Reporte(sim)
    rep.mostrar()


if __name__ == "__main__":
    main()