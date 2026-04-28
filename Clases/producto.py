class Producto:
    _contador = 0

    def __init__(self):
        Producto._contador += 1
        self.id = Producto._contador
        self.tiempo_entrada = 0      # ciclo en que entró a la línea
        self.tiempo_salida = None    # ciclo en que salió de la línea
        self.tarea_actual = None     # referencia a la tarea donde está ahora

    def get_tiempo_total(self):
        if self.tiempo_salida is not None:
            return self.tiempo_salida - self.tiempo_entrada
        return None

    def get_estado(self):
        if self.tiempo_salida is not None:
            return "completado"
        if self.tarea_actual is not None:
            return f"en tarea '{self.tarea_actual.nombre}'"
        return "en espera de iniciar"

    def __str__(self):
        return f"Producto #{self.id} [{self.get_estado()}]"

    @classmethod
    def reiniciar_contador(cls):
        cls._contador = 0