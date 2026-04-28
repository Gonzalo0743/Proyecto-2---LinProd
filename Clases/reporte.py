from simulador import Simulador


class Reporte:
    def __init__(self, simulador: Simulador):
        self.simulador = simulador
        self.datos = {}

    def calcular_estadisticas(self):
        completados = self.simulador.productos_completados

        if not completados:
            self.datos = {"error": "No hay productos completados."}
            return

        tiempos = [p.get_tiempo_total() for p in completados]

        self.datos = {
            "total_productos": len(self.simulador.productos),
            "productos_completados": len(completados),
            "ciclos_totales": self.simulador.ciclo_actual,
            "tiempo_primer_producto": min(tiempos),
            "tiempo_ultimo_producto": max(tiempos),
            "tiempo_promedio": round(sum(tiempos) / len(tiempos), 2),
            "cuello_de_botella": self._get_cuello_botella(),
            "tarea_mayor_espera": self._get_tarea_mayor_espera(),
            "promedio_espera_global": self._get_promedio_espera_global(),
        }

    def _get_cuello_botella(self):
        peor_proceso = None
        peor_tarea = None
        max_cola = 0
        for proceso in self.simulador.linea.procesos:
            t = proceso.get_cuello_botella()
            if t and t.max_cola_alcanzada > max_cola:
                max_cola = t.max_cola_alcanzada
                peor_tarea = t
                peor_proceso = proceso
        if peor_proceso:
            return f"Proceso '{peor_proceso.nombre}' — Tarea '{peor_tarea.nombre}' (max cola: {max_cola})"
        return "Sin congestión"

    def _get_tarea_mayor_espera(self):
        peor = None
        max_espera = 0
        for proceso in self.simulador.linea.procesos:
            for tarea in proceso.tareas:
                if tarea.t_espera_acumulado > max_espera:
                    max_espera = tarea.t_espera_acumulado
                    peor = (proceso.nombre, tarea.nombre, max_espera)
        if peor:
            return f"Proceso '{peor[0]}' — Tarea '{peor[1]}' (espera acumulada: {peor[2]} ciclos)"
        return "Sin datos"

    def _get_promedio_espera_global(self):
        total_espera = sum(
            t.t_espera_acumulado
            for p in self.simulador.linea.procesos
            for t in p.tareas
        )
        total_atendidos = sum(
            t.productos_atendidos
            for p in self.simulador.linea.procesos
            for t in p.tareas
        )
        if total_atendidos == 0:
            return 0
        return round(total_espera / total_atendidos, 2)

    def mostrar(self):
        if not self.datos:
            self.calcular_estadisticas()

        d = self.datos
        if "error" in d:
            print(f"\n[Reporte] {d['error']}")
            return

        print(f"\n{'═'*52}")
        print(f"  REPORTE FINAL DE PRODUCCIÓN")
        print(f"{'═'*52}")
        print(f"  Total de productos            : {d['total_productos']}")
        print(f"  Productos completados         : {d['productos_completados']}")
        print(f"  Ciclos totales de simulación  : {d['ciclos_totales']}")
        print(f"{'─'*52}")
        print(f"  Tiempo primer producto        : {d['tiempo_primer_producto']} ciclos")
        print(f"  Tiempo último producto        : {d['tiempo_ultimo_producto']} ciclos")
        print(f"  Tiempo promedio por producto  : {d['tiempo_promedio']} ciclos")
        print(f"{'─'*52}")
        print(f"  Cuello de botella             : {d['cuello_de_botella']}")
        print(f"  Tarea con mayor espera        : {d['tarea_mayor_espera']}")
        print(f"  Promedio de espera global     : {d['promedio_espera_global']} ciclos")
        print(f"{'═'*52}\n")