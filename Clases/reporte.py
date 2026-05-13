from .simulador import Simulador


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
            "tiempo_total_procesamiento": sum(tiempos),
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
        print(f"  Tiempo total procesamiento    : {d['tiempo_total_procesamiento']} ciclos")
        print(f"{'─'*52}")
        print(f"  Cuello de botella             : {d['cuello_de_botella']}")
        print(f"  Tarea con mayor espera        : {d['tarea_mayor_espera']}")
        print(f"  Promedio de espera global     : {d['promedio_espera_global']} ciclos")
        print(f"{'═'*52}\n")

    def exportar(self, ruta: str = "reporte_linprod.txt"):
        """
        Exporta el reporte a un archivo .txt o .csv.
        Si ruta termina en .csv genera formato separado por comas.
        """
        if not self.datos:
            self.calcular_estadisticas()

        d = self.datos
        es_csv = ruta.lower().endswith(".csv")

        with open(ruta, "w", encoding="utf-8") as f:
            if es_csv:
                f.write("campo,valor\n")
                if "error" in d:
                    f.write(f"error,{d['error']}\n")
                    return ruta
                for campo, valor in [
                    ("total_productos",           d["total_productos"]),
                    ("productos_completados",      d["productos_completados"]),
                    ("ciclos_totales",             d["ciclos_totales"]),
                    ("tiempo_primer_producto",     d["tiempo_primer_producto"]),
                    ("tiempo_ultimo_producto",     d["tiempo_ultimo_producto"]),
                    ("tiempo_promedio",            d["tiempo_promedio"]),
                    ("tiempo_total_procesamiento", d["tiempo_total_procesamiento"]),
                    ("cuello_de_botella",          d["cuello_de_botella"]),
                    ("tarea_mayor_espera",         d["tarea_mayor_espera"]),
                    ("promedio_espera_global",     d["promedio_espera_global"]),
                ]:
                    f.write(f"{campo},{valor}\n")
                f.write("\nproceso,tarea,atendidos,max_cola,espera_acumulada\n")
                for proc in self.simulador.linea.procesos:
                    for tarea in proc.tareas:
                        f.write(f"{proc.nombre},{tarea.nombre},"
                                f"{tarea.productos_atendidos},"
                                f"{tarea.max_cola_alcanzada},"
                                f"{tarea.t_espera_acumulado}\n")
            else:
                sep = "=" * 52
                f.write(f"{sep}\n  REPORTE FINAL DE PRODUCCION — LinProd\n{sep}\n")
                if "error" in d:
                    f.write(f"  {d['error']}\n")
                    return ruta
                f.write(f"  Total de productos            : {d['total_productos']}\n")
                f.write(f"  Productos completados         : {d['productos_completados']}\n")
                f.write(f"  Ciclos totales de simulacion  : {d['ciclos_totales']}\n")
                f.write(f"{'-'*52}\n")
                f.write(f"  Tiempo primer producto        : {d['tiempo_primer_producto']} ciclos\n")
                f.write(f"  Tiempo ultimo producto        : {d['tiempo_ultimo_producto']} ciclos\n")
                f.write(f"  Tiempo promedio por producto  : {d['tiempo_promedio']} ciclos\n")
                f.write(f"  Tiempo total procesamiento    : {d['tiempo_total_procesamiento']} ciclos\n")
                f.write(f"{'-'*52}\n")
                f.write(f"  Cuello de botella             : {d['cuello_de_botella']}\n")
                f.write(f"  Tarea con mayor espera        : {d['tarea_mayor_espera']}\n")
                f.write(f"  Promedio de espera global     : {d['promedio_espera_global']} ciclos\n")
                f.write(f"{'-'*52}\n  DETALLE POR PROCESO\n{'-'*52}\n")
                for proc in self.simulador.linea.procesos:
                    flags = []
                    if proc.es_inicial: flags.append("INICIAL")
                    if proc.es_final:   flags.append("FINAL")
                    tag = f" [{', '.join(flags)}]" if flags else ""
                    f.write(f"\n  > {proc.nombre}{tag}\n")
                    for tarea in proc.tareas:
                        f.write(f"    - {tarea.nombre:<20s} | "
                                f"atendidos: {tarea.productos_atendidos:3d} | "
                                f"max cola: {tarea.max_cola_alcanzada:3d} | "
                                f"espera acum: {tarea.t_espera_acumulado} ciclos\n")
                f.write(f"\n{sep}\n")

        return ruta
