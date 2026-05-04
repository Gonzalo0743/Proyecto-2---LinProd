from .producto import Producto
from .lineaproduccion import LineaDeProduccion


class Simulador:
    def __init__(self, linea: LineaDeProduccion):
        self.linea = linea
        self.ciclo_actual = 0
        self.productos = []           # todos los productos creados
        self.cola_entrada = []        # productos que aún no entraron a la línea
        self.productos_completados = []
        self.pausado = False

    # ── Iniciar simulación ───────────────────────────────────────────
    def iniciar(self, n_productos: int):
        """Prepara n productos en la cola de entrada."""
        self.linea.validar()
        self.linea.reinicializar()
        self.ciclo_actual = 0
        self.productos = []
        self.cola_entrada = []
        self.productos_completados = []

        for _ in range(n_productos):
            p = Producto()
            self.productos.append(p)
            self.cola_entrada.append(p)

    # ── Ciclo principal ──────────────────────────────────────────────
    def tick(self):
        """Avanza un ciclo completo en toda la línea."""
        if self.pausado:
            return

        self.ciclo_actual += 1
        primer_proceso = self.linea.proceso_inicial

        # Ingresar un producto a la línea si hay en cola de entrada
        if self.cola_entrada:
            producto = self.cola_entrada.pop(0)
            producto.tiempo_entrada = self.ciclo_actual
            primer_proceso.get_primera_tarea().agregar_producto(producto, self.ciclo_actual)

        # Avanzar cada proceso y mover productos entre procesos
        for i, proceso in enumerate(self.linea.procesos):
            productos_listos = proceso.tick(self.ciclo_actual)
            for producto in productos_listos:
                if proceso.es_final:
                    # Producto terminó toda la línea
                    producto.tiempo_salida = self.ciclo_actual
                    producto.tarea_actual = None
                    self.productos_completados.append(producto)
                else:
                    # Pasa al proceso siguiente
                    proceso.proceso_siguiente.get_primera_tarea().agregar_producto(
                        producto, self.ciclo_actual
                    )

    def esta_terminado(self):
        """True cuando todos los productos han completado la línea."""
        return (
            len(self.cola_entrada) == 0
            and len(self.productos_completados) == len(self.productos)
        )

    # ── Control ──────────────────────────────────────────────────────
    def pausar(self):
        self.pausado = True

    def reanudar(self):
        self.pausado = False

    # ── Snapshot del estado actual ───────────────────────────────────
    def get_snapshot(self):
        """Retorna un dict con el estado completo de la línea en este ciclo."""
        snap = {
            "ciclo": self.ciclo_actual,
            "productos_completados": len(self.productos_completados),
            "productos_en_linea": len(self.productos) - len(self.productos_completados) - len(self.cola_entrada),
            "productos_por_entrar": len(self.cola_entrada),
            "procesos": [],
        }
        for proceso in self.linea.procesos:
            p_info = {
                "nombre": proceso.nombre,
                "es_inicial": proceso.es_inicial,
                "es_final": proceso.es_final,
                "tareas": [],
            }
            for tarea in proceso.tareas:
                p_info["tareas"].append({
                    "nombre": tarea.nombre,
                    "procesando": str(tarea.producto_actual) if tarea.producto_actual else "—",
                    "ciclos_restantes": tarea.ciclos_restantes,
                    "en_cola": len(tarea.cola),
                })
            snap["procesos"].append(p_info)
        return snap

    def imprimir_snapshot(self):
        snap = self.get_snapshot()
        print(f"\n{'═'*50}")
        print(f"  SNAPSHOT — Ciclo {snap['ciclo']}")
        print(f"{'═'*50}")
        print(f"  Completados : {snap['productos_completados']}")
        print(f"  En línea    : {snap['productos_en_linea']}")
        print(f"  Por entrar  : {snap['productos_por_entrar']}")
        for p in snap["procesos"]:
            flags = " [INICIAL]" if p["es_inicial"] else (" [FINAL]" if p["es_final"] else "")
            print(f"\n  ▶ Proceso '{p['nombre']}'{flags}")
            for t in p["tareas"]:
                print(f"    • {t['nombre']:20s} | procesando: {t['procesando']:15s} | "
                      f"ciclos rest: {t['ciclos_restantes']} | cola: {t['en_cola']}")
        print(f"{'═'*50}\n")