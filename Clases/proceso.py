from tarea import Tarea


class Proceso:
    def __init__(self, nombre: str, es_inicial: bool = False, es_final: bool = False):
        self.nombre = nombre
        self.es_inicial = es_inicial
        self.es_final = es_final
        self.tareas = []                  # lista ordenada de Tarea
        self.proceso_anterior = None
        self.proceso_siguiente = None

    # ── Gestión de tareas ────────────────────────────────────────────
    def agregar_tarea(self, tarea: Tarea):
        tarea.proceso = self
        self.tareas.append(tarea)

    def get_primera_tarea(self):
        if not self.tareas:
            raise ValueError(f"El proceso '{self.nombre}' no tiene tareas definidas.")
        return self.tareas[0]

    def get_ultima_tarea(self):
        if not self.tareas:
            raise ValueError(f"El proceso '{self.nombre}' no tiene tareas definidas.")
        return self.tareas[-1]

    # ── Avance de ciclo ──────────────────────────────────────────────
    def tick(self, ciclo_actual: int):
        """
        Avanza un ciclo en todas las tareas del proceso.
        Retorna lista de productos que terminaron la última tarea
        (listos para pasar al proceso siguiente).
        """
        productos_listos = []

        for i, tarea in enumerate(self.tareas):
            producto_terminado = tarea.tick(ciclo_actual)
            if producto_terminado is not None:
                es_ultima = (i == len(self.tareas) - 1)
                if es_ultima:
                    # Sale del proceso completo
                    productos_listos.append(producto_terminado)
                else:
                    # Pasa a la siguiente tarea dentro del mismo proceso
                    self.tareas[i + 1].agregar_producto(producto_terminado, ciclo_actual)

        return productos_listos

    # ── Estado ───────────────────────────────────────────────────────
    def get_estado(self):
        return {
            "proceso": self.nombre,
            "es_inicial": self.es_inicial,
            "es_final": self.es_final,
            "tareas": [t.get_estado() for t in self.tareas],
        }

    def get_cuello_botella(self):
        """Retorna la tarea con la cola máxima alcanzada."""
        if not self.tareas:
            return None
        return max(self.tareas, key=lambda t: t.max_cola_alcanzada)

    def __str__(self):
        flags = []
        if self.es_inicial:
            flags.append("INICIAL")
        if self.es_final:
            flags.append("FINAL")
        header = f"Proceso '{self.nombre}'" + (f" [{', '.join(flags)}]" if flags else "")
        tareas_str = "\n".join(str(t) for t in self.tareas)
        return f"{header}\n{tareas_str}"