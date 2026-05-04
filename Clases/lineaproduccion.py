from .proceso import Proceso


class LineaDeProduccion:
    def __init__(self):
        self.procesos = []
        self.proceso_inicial = None
        self.proceso_final = None

    # ── Gestión de procesos ──────────────────────────────────────────
    def agregar_proceso(self, proceso: Proceso):
        """Agrega un proceso y actualiza las referencias inicial/final."""
        if proceso.es_inicial:
            if self.proceso_inicial is not None:
                raise ValueError("Ya existe un proceso inicial en la línea.")
            self.proceso_inicial = proceso
        if proceso.es_final:
            if self.proceso_final is not None:
                raise ValueError("Ya existe un proceso final en la línea.")
            self.proceso_final = proceso
        self.procesos.append(proceso)

    def enlazar_procesos(self):
        """
        Encadena los procesos en el orden en que fueron agregados,
        asignando proceso_anterior y proceso_siguiente a cada uno.
        """
        for i, proceso in enumerate(self.procesos):
            proceso.proceso_anterior = self.procesos[i - 1] if i > 0 else None
            proceso.proceso_siguiente = self.procesos[i + 1] if i < len(self.procesos) - 1 else None

    def validar(self):
        """Verifica que la línea esté correctamente configurada antes de simular."""
        if not self.procesos:
            raise ValueError("La línea no tiene procesos.")
        if self.proceso_inicial is None:
            raise ValueError("No se ha definido un proceso inicial.")
        if self.proceso_final is None:
            raise ValueError("No se ha definido un proceso final.")
        for p in self.procesos:
            if not p.tareas:
                raise ValueError(f"El proceso '{p.nombre}' no tiene tareas.")

    def reinicializar(self):
        """Reinicia el estado de todas las tareas para volver a simular."""
        from collections import deque
        from .producto import Producto
        Producto.reiniciar_contador()
        for proceso in self.procesos:
            for tarea in proceso.tareas:
                tarea.cola = deque()
                tarea.esta_procesando = False
                tarea.producto_actual = None
                tarea.ciclos_restantes = 0
                tarea.productos_atendidos = 0
                tarea.t_espera_acumulado = 0
                tarea.max_cola_alcanzada = 0

    # ── Estado ───────────────────────────────────────────────────────
    def get_estado(self):
        return [p.get_estado() for p in self.procesos]

    def __str__(self):
        separador = "\n" + "─" * 40 + "\n"
        return separador.join(str(p) for p in self.procesos)