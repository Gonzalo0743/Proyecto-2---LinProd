"""
MotorCiclos
───────────
Orquesta el Simulador ciclo a ciclo.
Soporta:
  - Velocidad configurable (segundos reales entre ciclos, puede ser 0)
  - Pausa/reanudación en cualquier momento
  - Callbacks por ciclo (para que la GUI pueda refrescar la vista)
  - Pausa automática en ciclos específicos ("breakpoints")
  - Ejecución completa sin pausa (modo batch)
"""
import time
import threading
from typing import Callable, Optional
from .simulador import Simulador


class MotorCiclos:
    def __init__(self, simulador: Simulador, velocidad: float = 0.3):
        """
        simulador : instancia de Simulador ya inicializada
        velocidad : segundos reales entre ciclos (0 = lo más rápido posible)
        """
        self.simulador = simulador
        self.velocidad = velocidad          # segundos entre ticks
        self.breakpoints: set[int] = set()  # ciclos donde pausar automáticamente
        self.max_ciclos: int = 10_000       # tope de seguridad

        # Callbacks
        self._on_tick:     Optional[Callable] = None  # se llama tras cada tick
        self._on_pausa:    Optional[Callable] = None  # se llama al pausar
        self._on_fin:      Optional[Callable] = None  # se llama al terminar

        # Estado interno del hilo
        self._hilo:        Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()   # arranca en "no pausado"

    # ── Configuración ────────────────────────────────────────────────
    def agregar_breakpoint(self, ciclo: int):
        self.breakpoints.add(ciclo)

    def quitar_breakpoint(self, ciclo: int):
        self.breakpoints.discard(ciclo)

    def set_velocidad(self, segundos: float):
        self.velocidad = max(0.0, segundos)

    def on_tick(self, fn: Callable):
        """Registra callback fn(simulador) que se ejecuta después de cada tick."""
        self._on_tick = fn

    def on_pausa(self, fn: Callable):
        """Registra callback fn(simulador) al pausar."""
        self._on_pausa = fn

    def on_fin(self, fn: Callable):
        """Registra callback fn(simulador) al terminar toda la simulación."""
        self._on_fin = fn

    # ── Control ──────────────────────────────────────────────────────
    def pausar(self):
        self._pause_event.clear()
        self.simulador.pausar()
        if self._on_pausa:
            self._on_pausa(self.simulador)

    def reanudar(self):
        self.simulador.reanudar()
        self._pause_event.set()

    def detener(self):
        """Para el hilo por completo (no se puede reanudar)."""
        self._stop_event.set()
        self._pause_event.set()   # desbloquea el hilo si estaba en pausa

    def esta_pausado(self) -> bool:
        return not self._pause_event.is_set()

    def esta_corriendo(self) -> bool:
        return self._hilo is not None and self._hilo.is_alive()

    # ── Modos de ejecución ───────────────────────────────────────────
    def correr_en_hilo(self):
        """Lanza el loop en un hilo separado (útil para GUI)."""
        self._stop_event.clear()
        self._pause_event.set()
        self._hilo = threading.Thread(target=self._loop, daemon=True)
        self._hilo.start()

    def correr_sincrono(self):
        """Corre el loop en el hilo actual (útil para consola)."""
        self._stop_event.clear()
        self._pause_event.set()
        self._loop()

    def correr_batch(self) -> int:
        """
        Ejecuta toda la simulación sin delays ni pausas.
        Retorna el número de ciclos ejecutados.
        Útil para pruebas y para reinicializar con los mismos datos.
        """
        ciclos = 0
        while not self.simulador.esta_terminado() and ciclos < self.max_ciclos:
            self.simulador.tick()
            ciclos += 1
        if self._on_fin:
            self._on_fin(self.simulador)
        return ciclos

    # ── Loop interno ─────────────────────────────────────────────────
    def _loop(self):
        ciclos = 0
        while not self._stop_event.is_set() and ciclos < self.max_ciclos:

            # Esperar si está pausado
            self._pause_event.wait()
            if self._stop_event.is_set():
                break

            if self.simulador.esta_terminado():
                break

            # Avanzar un ciclo
            self.simulador.tick()
            ciclos += 1

            # Callback por ciclo
            if self._on_tick:
                self._on_tick(self.simulador)

            # Breakpoint automático
            if self.simulador.ciclo_actual in self.breakpoints:
                self.pausar()

            # Delay real entre ciclos
            if self.velocidad > 0:
                time.sleep(self.velocidad)

        # Fin natural
        if self._on_fin and self.simulador.esta_terminado():
            self._on_fin(self.simulador)