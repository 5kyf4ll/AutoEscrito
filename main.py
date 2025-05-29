import customtkinter as ctk
from PIL import Image
import pywinstyles
import os
import threading 

# Importar las clases y funciones de los nuevos módulos
from writer_logic import WriterProcessManager
from utils import validate_numeric_input, get_latest_files, copy_file_to_directory

# --- NUEVAS IMPORTACIONES PARA MANEJAR LA BARRA DE TAREAS EN WINDOWS ---
import win32con
import win32gui
import ctypes

# Definir la función para ocultar/mostrar la ventana de la barra de tareas
# Necesitamos el HWND (handle de la ventana) que Tkinter nos da.
# Esto es específico de Windows.
def set_window_taskbar_visibility(hwnd, show_in_taskbar):
    GWL_EXSTYLE = -20
    # Obtenemos el estilo extendido actual de la ventana
    ex_style = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)

    if show_in_taskbar:
        # Remover el estilo WS_EX_TOOLWINDOW para que aparezca en la barra de tareas
        new_ex_style = ex_style & (~win32con.WS_EX_TOOLWINDOW)
    else:
        # Añadir el estilo WS_EX_TOOLWINDOW para que desaparezca de la barra de tareas
        new_ex_style = ex_style | win32con.WS_EX_TOOLWINDOW
    
    win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, new_ex_style)

    # Forzar el redibujado de la barra de tareas
    # Esto a veces es necesario para que el cambio sea instantáneo.
    win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoEscrito")
        self.geometry("400x120")
        self.resizable(False, False)
        
        # Obtener el HWND de la ventana principal de Tkinter
        # Esto solo estará disponible después de que la ventana se haya creado
        # y se haya procesado al menos un evento.
        # Lo haremos en un after() o justo antes de la llamada a mainloop
        self.after(100, self._get_hwnd_and_set_initial_visibility)
        self.hwnd = None # Inicializamos el HWND a None

        self.writer = WriterProcessManager(app_instance=self, debug=True, info_callback=self.actualizar_info)

        # Directorio de los archivos
        self.files_directory = "files"
        if not os.path.exists(self.files_directory):
            os.makedirs(self.files_directory)

        # Fondo
        self.bg_image = ctk.CTkImage(Image.open("assets/fondo.png"), size=(400, 160))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        ### BOTÓN SUBIR
        self.subir_img = ctk.CTkImage(Image.open("assets/subir.png"), size=(40, 40))
        self.subir_btn = ctk.CTkButton(self, image=self.subir_img, text="", width=40, height=40,
                                         bg_color="#000001", fg_color="#000001", hover=False,
                                         corner_radius=5, command=self.subir_archivo)
        self.subir_btn.place(x=10, y=20)
        pywinstyles.set_opacity(self.subir_btn, color="#000001")

        self.subir_lbl = ctk.CTkLabel(self, text="Subir", font=("Arial", 10), text_color="black", bg_color="#000001")
        self.subir_lbl.place(x=25, y=65)
        pywinstyles.set_opacity(self.subir_lbl, color="#000001")

        ### LABEL ARCHIVO
        self.file_label = ctk.CTkLabel(self, text="Archivo:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.file_label.place(x=65, y=20)
        pywinstyles.set_opacity(self.file_label, color="#000001")

        ### COMBOBOX DE ARCHIVOS
        self.file_options = get_latest_files(self.files_directory) # Usando función de utils
        if not self.file_options:
            self.file_options = ["No files found"]
            latest_file = "No files found"
        else:
            latest_file = os.path.basename(self.file_options[0])

        self.file_combobox = ctk.CTkComboBox(self, width=200, height=25,
                                              values=[os.path.basename(f) for f in self.file_options],
                                              fg_color="white", bg_color="#000001",
                                              border_color="gray", text_color="black",
                                              state="readonly")
        self.file_combobox.place(x=110, y=20)
        self.file_combobox.set(latest_file)
        pywinstyles.set_opacity(self.file_combobox, color="#000001")


        ### LABEL DELAY
        self.delay_label = ctk.CTkLabel(self, text="Delay:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.delay_label.place(x=72, y=55)
        pywinstyles.set_opacity(self.delay_label, color="#000001")

        ### ENTRY DELAY
        vcmd = (self.register(validate_numeric_input), '%P')
        self.delay_entry = ctk.CTkEntry(self, width=50, height=25, fg_color="white", bg_color="#000001",
                                         border_color="gray", validate="key", validatecommand=vcmd)
        self.delay_entry.insert(0, "0.15")
        self.delay_entry.place(x=110, y=55)
        pywinstyles.set_opacity(self.delay_entry, color="#000001")
        self.delay_entry.bind("<MouseWheel>", self.on_delay_scroll)
        self.delay_entry.bind("<Button-4>", self.on_delay_scroll)
        self.delay_entry.bind("<Button-5>", self.on_delay_scroll)


        ### LABEL ESPERA
        self.wait_label = ctk.CTkLabel(self, text="Espera:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.wait_label.place(x=170, y=55)
        pywinstyles.set_opacity(self.wait_label, color="#000001")

        ### ENTRY ESPERA
        vcmd_wait = (self.register(validate_numeric_input), '%P')
        self.wait_entry = ctk.CTkEntry(self, width=50, height=25, fg_color="white", bg_color="#000001",
                                        border_color="gray", validate="key", validatecommand=vcmd_wait)
        self.wait_entry.insert(0, "5")
        self.wait_entry.place(x=210, y=55)
        pywinstyles.set_opacity(self.wait_entry, color="#000001")
        self.wait_entry.bind("<MouseWheel>", self.on_wait_scroll)
        self.wait_entry.bind("<Button-4>", self.on_wait_scroll)
        self.wait_entry.bind("<Button-5>", self.on_wait_scroll)
        
        ### BOTÓN VISIBILIDAD EN BARRA DE TAREAS
        self.visible_img = ctk.CTkImage(Image.open("assets/visible.png"), size=(20, 20))
        self.invisible_img = ctk.CTkImage(Image.open("assets/invisible.png"), size=(20, 20))
        self.taskbar_visible = True # Estado inicial: visible en la barra de tareas

        # Cambiamos el nombre del botón y su comando para reflejar su nueva función
        self.toggle_taskbar_btn = ctk.CTkButton(self, image=self.visible_img, text="", width=25, height=25,
                                         bg_color="#000001", fg_color="transparent", 
                                         command=self.toggle_taskbar_visibility)
        self.toggle_taskbar_btn.place(x=265, y=55)
        pywinstyles.set_opacity(self.toggle_taskbar_btn, color="#000001")
        
        ### BOTÓN PLAY/PAUSA
        self.play_img = ctk.CTkImage(Image.open("assets/play.png"), size=(50, 50))
        self.pause_img = ctk.CTkImage(Image.open("assets/pausa.png"), size=(50, 50))

        self.play_pause_btn = ctk.CTkButton(self, image=self.play_img, text="", width=50, height=50,
                                         bg_color="#000001", fg_color="#000001", hover=False, corner_radius=5,
                                         command=self.toggle_play_pause)
        self.play_pause_btn.place(x=320, y=20)
        pywinstyles.set_opacity(self.play_pause_btn, color="#000001")

        ### BOTÓN DETENER
        self.stop_img = ctk.CTkImage(Image.open("assets/stop.png"), size=(50, 50))
        self.stop_btn = ctk.CTkButton(self, image=self.stop_img, text="", width=50, height=50,
                                         bg_color="#000001", fg_color="#000001", hover=False, corner_radius=5,
                                         command=self.stop_writing_process, state="disabled")
        self.stop_btn.place(x=320, y=70)
        pywinstyles.set_opacity(self.stop_btn, color="#000001")

        ### LABEL INFO
        self.info_label = ctk.CTkLabel(self, text="Listo para iniciar:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.info_label.place(x=120, y=85)
        pywinstyles.set_opacity(self.info_label, color="#000001")

    def _get_hwnd_and_set_initial_visibility(self):
        """
        Obtiene el handle de la ventana y establece la visibilidad inicial en la barra de tareas.
        Llamado con `self.after` para asegurar que la ventana ya está creada.
        """
        self.hwnd = win32gui.FindWindow(None, self.title()) # Busca la ventana por su título
        if self.hwnd:
            # Establece la visibilidad inicial en la barra de tareas (True por defecto)
            set_window_taskbar_visibility(self.hwnd, self.taskbar_visible)
        else:
            print("Advertencia: No se pudo encontrar el HWND de la ventana principal.")


    def update_file_combobox(self):
        """Actualiza las opciones del combobox de archivos."""
        self.file_options = get_latest_files(self.files_directory)
        if not self.file_options:
            self.file_combobox.configure(values=["No files found"])
            self.file_combobox.set("No files found")
        else:
            file_names = [os.path.basename(f) for f in self.file_options]
            self.file_combobox.configure(values=file_names)
            self.file_combobox.set(file_names[0])

    def subir_archivo(self):
        """Permite al usuario seleccionar y subir un archivo .txt."""
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if copy_file_to_directory(ruta, self.files_directory):
            self.update_file_combobox()

    def on_delay_scroll(self, event):
        """Maneja el evento de la rueda del mouse para cambiar el valor de delay_entry."""
        current_value = 0.0
        try:
            current_value = float(self.delay_entry.get())
        except ValueError:
            self.delay_entry.delete(0, ctk.END)
            self.delay_entry.insert(0, "0.0")
            current_value = 0.0

        if event.delta > 0 or event.num == 4:
            new_value = current_value + 0.05
        elif event.delta < 0 or event.num == 5:
            new_value = current_value - 0.05
        else:
            return

        if new_value < 0:
            new_value = 0.0

        self.delay_entry.delete(0, ctk.END)
        self.delay_entry.insert(0, f"{new_value:.2f}")

    def on_wait_scroll(self, event):
        """Maneja el evento de la rueda del mouse para cambiar el valor de wait_entry."""
        current_value = 0
        try:
            current_value = int(float(self.wait_entry.get()))
        except ValueError:
            self.wait_entry.delete(0, ctk.END)
            self.wait_entry.insert(0, "0")
            current_value = 0

        if event.delta > 0 or event.num == 4:
            new_value = current_value + 1
        elif event.delta < 0 or event.num == 5:
            new_value = current_value - 1
        else:
            return

        if new_value < 0:
            new_value = 0

        self.wait_entry.delete(0, ctk.END)
        self.wait_entry.insert(0, str(new_value))

    def toggle_play_pause(self):
        """Alterna entre iniciar, pausar y reanudar el proceso de escritura."""
        if not self.writer.is_running:
            selected_file_name = self.file_combobox.get()
            if selected_file_name == "No files found":
                self.actualizar_info("Error: Selecciona un archivo.")
                print("No se ha seleccionado ningún archivo para iniciar.")
                return

            full_path = os.path.join(self.files_directory, selected_file_name)
            
            delay_value = 0.0
            try:
                delay_value = float(self.delay_entry.get())
            except ValueError:
                self.actualizar_info("Error: Delay no válido. Usando 0.0.")
                print("Valor de Delay no válido. Usando 0.0 por defecto.")
                
            wait_value = 0
            try:
                wait_value = int(float(self.wait_entry.get()))
            except ValueError:
                self.actualizar_info("Error: Espera no válida. Usando 0.")
                print("Valor de Espera no válido. Usando 0 por defecto.")

            self.writer.start(full_path, delay_value, wait_value)
            
            self.play_pause_btn.configure(image=self.pause_img, state="normal")
            self.stop_btn.configure(state="normal")
        else:
            if self.writer.is_paused:
                self.writer.resume()
                self.play_pause_btn.configure(image=self.pause_img)
                self.actualizar_info("Escritura reanudada.")
            else:
                self.writer.pause()
                self.play_pause_btn.configure(image=self.play_img)
                self.actualizar_info("Escritura pausada.")

    def stop_writing_process(self):
        """Detiene completamente el proceso de escritura a través del gestor."""
        self.writer.stop()
        self.actualizar_info("Proceso detenido.")

    def _reset_gui_state(self):
        """
        Función auxiliar para resetear el estado de los botones de la GUI
        después de que el proceso de escritura termina (éxito, error o detención).
        Es llamada de forma segura desde el hilo secundario mediante `self.after()`.
        """
        self.play_pause_btn.configure(image=self.play_img, state="normal")
        self.stop_btn.configure(state="disabled")
        self.actualizar_info("Listo para iniciar:")

    def toggle_taskbar_visibility(self): # Renombrado de toggle_password
        """
        Alterna la visibilidad de la ventana de la aplicación en la barra de tareas de Windows.
        """
        if self.hwnd is None:
            # Intenta obtener el HWND de nuevo si no se pudo antes
            self.hwnd = win32gui.FindWindow(None, self.title())
            if self.hwnd is None:
                print("Error: No se pudo obtener el HWND de la ventana para alternar la visibilidad.")
                return

        if self.taskbar_visible:
            # Ocultar de la barra de tareas
            set_window_taskbar_visibility(self.hwnd, False)
            self.toggle_taskbar_btn.configure(image=self.invisible_img)
            self.actualizar_info("App oculta en barra de tareas.")
        else:
            # Mostrar en la barra de tareas
            set_window_taskbar_visibility(self.hwnd, True)
            self.toggle_taskbar_btn.configure(image=self.visible_img)
            self.actualizar_info("App visible en barra de tareas.")
            # Opcional: traer la ventana al frente cuando se hace visible de nuevo
            self.deiconify() # Si estaba minimizada
            self.lift() # La trae al frente
        self.taskbar_visible = not self.taskbar_visible
        
    def actualizar_info(self, mensaje):
        """Actualiza el texto del info_label."""
        self.info_label.configure(text=mensaje)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()