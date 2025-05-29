import time
import keyboard
import threading
import os

class WriterProcessManager:
    """
    Gestiona el proceso de escritura de texto en un hilo separado,
    permitiendo pausa, reanudación y detención.
    """
    def __init__(self, app_instance, debug=False, info_callback=None):
        self.app_instance = app_instance
        self._writing_thread = None
        self._paused = False
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self.debug = debug
        self.info_callback = info_callback

    def start(self, ruta_txt, delay_char, initial_wait):
        if self._writing_thread and self._writing_thread.is_alive():
            self._log("Proceso ya en ejecución.")
            return

        self._pause_event.set() # Asegura que no esté pausado al iniciar
        self._stop_event.clear() # Limpia cualquier señal de detención previa
        self._paused = False

        self._writing_thread = threading.Thread(
            target=self._run_writing_process,
            args=(ruta_txt, delay_char, initial_wait)
        )
        self._writing_thread.start()
        self._log(f"Lógica de escritura iniciada para: {os.path.basename(ruta_txt)}")

    def pause(self):
        if self.is_running:
            self._pause_event.clear() # Establece el evento a "False" (pausado)
            self._paused = True
            self._log("Lógica de escritura pausada.")

    def resume(self):
        if self.is_running:
            self._pause_event.set() # Establece el evento a "True" (reanudar)
            self._paused = False
            self._log("Lógica de escritura reanudada.")

    def stop(self):
        if self.is_running:
            self._stop_event.set() # Señala que se debe detener
            self._pause_event.set() # Asegura que si estaba en pausa, se reanude para que el hilo pueda ver la señal de stop
            self._log("Solicitud de detención enviada.")

    @property
    def is_running(self):
        return self._writing_thread is not None and self._writing_thread.is_alive()

    @property
    def is_paused(self):
        return self._paused

    def _wait_or_stop(self):
        """
        Espera si está pausado o detiene si se recibe la señal de stop.
        Retorna True si debe continuar, False si debe detenerse.
        """
        self._pause_event.wait() # Se bloqueará aquí si el evento de pausa no está establecido (está pausado)
        return not self._stop_event.is_set() # Una vez reanudado, verifica si se ha solicitado detener

    def _log(self, mensaje):
        """
        Imprime un mensaje en consola y lo envía al callback de la GUI si está definido.
        """
        print(mensaje)
        if self.info_callback:
            self.app_instance.after(0, lambda: self.info_callback(mensaje))

    def _run_writing_process(self, ruta_txt, delay_char, initial_wait):
        self._log("Iniciando cuenta regresiva...")
        for i in range(initial_wait, 0, -1):
            # Siempre verifica si se ha solicitado detener antes de cada paso.
            if self._stop_event.is_set():
                self._log("Proceso detenido durante la cuenta regresiva.")
                self.app_instance.after(0, self.app_instance._reset_gui_state)
                return

            self._log(f"Cuenta regresiva: {i}")
            
            # --- MODIFICACIÓN CLAVE: Manejo de pausa/detención durante la cuenta regresiva ---
            # En lugar de time.sleep(1), usamos un bucle con sleeps pequeños
            # y verificamos el estado de los eventos en cada iteración.
            sleep_duration_per_count = 1.0 # La duración total de la pausa para este número de la cuenta regresiva
            sleep_check_interval = 0.05    # Intervalo de tiempo para revisar el estado (50 ms)

            start_time_segment = time.time()
            while (time.time() - start_time_segment < sleep_duration_per_count):
                # Verificar detención
                if self._stop_event.is_set():
                    self._log("Proceso detenido durante la cuenta regresiva (en bucle de espera).")
                    self.app_instance.after(0, self.app_instance._reset_gui_state)
                    return
                
                # Bloquear si está pausado
                self._pause_event.wait() # Si _pause_event está claro (pausado), se bloqueará aquí.

                # Verificar detención de nuevo, por si se detuvo mientras estaba pausado y luego se reanudó
                if self._stop_event.is_set():
                    self._log("Proceso detenido durante la cuenta regresiva (tras reanudar de pausa).")
                    self.app_instance.after(0, self.app_instance._reset_gui_state)
                    return
                
                # Pequeña siesta para no consumir CPU y permitir al sistema responder
                time.sleep(sleep_check_interval)
            # --- FIN DE LA MODIFICACIÓN DE LA CUENTA REGRESIVA ---

        # Después de la cuenta regresiva, una última verificación de stop
        if self._stop_event.is_set():
            self.app_instance.after(0, self.app_instance._reset_gui_state)
            return
        
        self._log("Iniciando escritura...")

        try:
            with open(ruta_txt, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines() 
        except FileNotFoundError:
            self._log(f"Error: El archivo '{ruta_txt}' no fue encontrado.")
            self.app_instance.after(0, self.app_instance._reset_gui_state)
            return
        except Exception as e:
            self._log(f"Error al leer el archivo: {e}")
            self.app_instance.after(0, self.app_instance._reset_gui_state)
            return

        time.sleep(delay_char) # Delay inicial antes de empezar a escribir

        for num_linea, linea in enumerate(lineas, start=1):
            if self._stop_event.is_set():
                self._log("Proceso detenido.")
                break

            if not self._wait_or_stop(): # Verifica pausa/detención antes de cada línea
                self._log("Proceso detenido tras una pausa o solicitud de detención.")
                break 

            self._log(f"Escribiendo línea {num_linea}...")

            i = 0
            while i < len(linea):
                if self._stop_event.is_set():
                    self._log("Proceso detenido durante escritura de línea.")
                    break 

                if not self._wait_or_stop(): # Verifica pausa/detención antes de cada caracter
                    self._log("Proceso detenido tras una pausa.")
                    break 

                char = linea[i]

                if char == ' ':
                    count = 1
                    while i + count < len(linea) and linea[i + count] == ' ':
                        count += 1
                    if count >= 4:
                        for _ in range(count // 4):
                            keyboard.press_and_release('tab')
                        i += count
                    else:
                        keyboard.write(' ' * count)
                        i += count
                elif char == '\n':
                    keyboard.press_and_release('enter')
                    i += 1
                else:
                    keyboard.write(char)
                    i += 1

                # Asegurarse de que SIEMPRE haya un delay después de CADA acción de teclado
                time.sleep(delay_char)
            else: # Este else se ejecuta si el bucle while interno termina normalmente (sin break)
                # Aquí podrías añadir una lógica para asegurar un ENTER al final de cada línea
                # si el archivo .txt no siempre termina con '\n'.
                # Por ahora, se asume que 'char == '\n'' ya lo maneja.
                pass 

        self._log("Proceso de escritura terminado.")
        self.app_instance.after(0, self.app_instance._reset_gui_state)