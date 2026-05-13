from collections import deque


class Tarea:
    def __init__(self, nombre: str, tiempo_ciclo: int):
        if tiempo_ciclo < 1:
            raise ValueError("El tiempo de ciclo debe ser al menos 1.")
        self.nombre = nombre
        self.tiempo_ciclo = tiempo_ciclo
        self.ciclos_restantes = 0
        self.esta_procesando = False
        self.cola = deque()              # productos esperando (FIFO)
        self.proceso = None              # referencia al proceso padre (se asigna al agregar)
        self.producto_actual = None      # producto que se está procesando ahora

        # Estadísticas
        self.productos_atendidos = 0
        self.t_espera_acumulado = 0      # suma de ciclos que productos esperaron en cola
        self.max_cola_alcanzada = 0      # mayor longitud de cola registrada

    # ── Entrada de producto ──────────────────────────────────────────
    def agregar_producto(self, producto, ciclo_actual: int):
        """Recibe un producto. Si está libre lo procesa de inmediato, si no lo encola."""
        producto.tarea_actual = self
        if not self.esta_procesando:
            self._iniciar_procesamiento(producto)
        else:
            producto._ciclo_entrada_cola = ciclo_actual   # para medir espera
            self.cola.append(producto)
            if len(self.cola) > self.max_cola_alcanzada:
                self.max_cola_alcanzada = len(self.cola)

    # ── Avance de un ciclo ───────────────────────────────────────────
    def tick(self, ciclo_actual: int):
        """
        Avanza un ciclo. Devuelve el producto terminado si en este ciclo
        se completó el procesamiento, o None si todavía está en curso.
        """
        if not self.esta_procesando:
            return None

        self.ciclos_restantes -= 1

        if self.ciclos_restantes == 0:
            producto_listo = self.producto_actual
            self.esta_procesando = False
            self.producto_actual = None
            self.productos_atendidos += 1

            # Si hay productos en cola, tomar el siguiente
            if self.cola:
                siguiente = self.cola.popleft()
                espera = ciclo_actual - getattr(siguiente, '_ciclo_entrada_cola', ciclo_actual)
                self.t_espera_acumulado += espera
                self._iniciar_procesamiento(siguiente)

            return producto_listo

        return None

    # ── Helpers ──────────────────────────────────────────────────────
    def _iniciar_procesamiento(self, producto):
        self.producto_actual = producto
        self.ciclos_restantes = self.tiempo_ciclo
        self.esta_procesando = True

    def get_estado(self):
        info = {
            "tarea": self.nombre,
            "tiempo_ciclo": self.tiempo_ciclo,
            "procesando": str(self.producto_actual) if self.producto_actual else "—",
            "ciclos_restantes": self.ciclos_restantes,
            "en_cola": len(self.cola),
            "atendidos": self.productos_atendidos,
        }
        return info

    def promedio_espera(self):
        if self.productos_atendidos == 0:
            return 0
        return round(self.t_espera_acumulado / self.productos_atendidos, 2)

    def __str__(self):
        estado = f"ocupada ({self.ciclos_restantes} ciclos restantes)" if self.esta_procesando else "libre"
        return f"  Tarea '{self.nombre}' | ciclo={self.tiempo_ciclo} | {estado} | cola={len(self.cola)}"