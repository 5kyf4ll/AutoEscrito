import time
import keyboard
import threading
import os

class WriterProcessManager:
    """
    Gestiona el proceso de escritura de texto en un hilo separado,
    permitiendo pausa, reanudación y detención.
    """
    def __init__(self, app_instance, debug=False):
        self.app_instance = app_instance
        self._writing_thread = None
        self._paused = False
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self.debug = debug

    def start(self, ruta_txt, delay_char, initial_wait):
        if self._writing_thread and self._writing_thread.is_alive():
            print("Proceso ya en ejecución.")
            return

        self._pause_event.set()
        self._stop_event.clear()
        self._paused = False

        self._writing_thread = threading.Thread(
            target=self._run_writing_process,
            args=(ruta_txt, delay_char, initial_wait)
        )
        self._writing_thread.start()
        print(f"Lógica de escritura iniciada en segundo plano para: {ruta_txt}")

    def pause(self):
        if self.is_running:
            self._pause_event.clear()
            self._paused = True
            print("Lógica de escritura pausada.")

    def resume(self):
        if self.is_running:
            self._pause_event.set()
            self._paused = False
            print("Lógica de escritura reanudada.")

    def stop(self):
        if self.is_running:
            self._stop_event.set()
            self._pause_event.set()
            self._writing_thread.join(timeout=2)
            print("Solicitud de detención enviada a la lógica de escritura.")

    @property
    def is_running(self):
        return self._writing_thread is not None and self._writing_thread.is_alive()

    @property
    def is_paused(self):
        return self._paused

    def _wait_or_stop(self):
        self._pause_event.wait()
        return not self._stop_event.is_set()

    def _run_writing_process(self, ruta_txt, delay_char, initial_wait):
        print("\nIniciando cuenta regresiva desde la lógica de escritura...")
        for i in range(initial_wait, 0, -1):
            if self._stop_event.is_set():
                print("Proceso detenido durante la espera inicial.")
                self.app_instance.after(0, self.app_instance._reset_gui_state)
                return
            print(f"Espera inicial: {i}...")
            time.sleep(1)

        if self._stop_event.is_set():
            self.app_instance.after(0, self.app_instance._reset_gui_state)
            return

        try:
            with open(ruta_txt, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            self.app_instance.after(0, self.app_instance._reset_gui_state)
            return

        time.sleep(delay_char)

        for num_linea, linea in enumerate(lineas, start=1):
            if self._stop_event.is_set():
                print("Proceso detenido.")
                break
            print(f"Línea {num_linea}:")

            i = 0
            while i < len(linea):
                if self._stop_event.is_set():
                    print("Proceso detenido durante la escritura de una línea.")
                    return

                if not self._wait_or_stop():
                    print("Proceso detenido tras la pausa.")
                    return

                char = linea[i]

                if char == ' ':
                    count = 1
                    while i + count < len(linea) and linea[i + count] == ' ':
                        count += 1
                    keyboard.write(' ' * count)
                    if self.debug:
                        print(f"Espacios: {' ' * count}")
                    i += count
                else:
                    keyboard.write(char)
                    if self.debug:
                        print(f"Caracter: {repr(char)}")
                    i += 1

                time.sleep(delay_char)

        print("Proceso de escritura terminado.")
        self.app_instance.after(0, self.app_instance._reset_gui_state)
