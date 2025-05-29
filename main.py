import customtkinter as ctk
from PIL import Image
import pywinstyles
import os

# Importar las clases y funciones de los nuevos módulos
from writer_logic import WriterProcessManager
from utils import validate_numeric_input, get_latest_files, copy_file_to_directory


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoEscrito")
        self.geometry("400x120")
        self.resizable(False, False)

        # Inicializar el gestor de procesos de escritura
        # Se pasa 'self' (la instancia de App) para que WriterProcessManager
        # pueda llamar a '_reset_gui_state' de forma segura cuando el proceso termina.
        self.writer_manager = WriterProcessManager(self)

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
                                             border_color="gray", text_color="black")
        self.file_combobox.place(x=110, y=20)
        self.file_combobox.set(latest_file)
        pywinstyles.set_opacity(self.file_combobox, color="#000001")


        ### LABEL DELAY
        self.delay_label = ctk.CTkLabel(self, text="Delay:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.delay_label.place(x=72, y=55)
        pywinstyles.set_opacity(self.delay_label, color="#000001")

        ### ENTRY DELAY
        # Usando la función de validación importada de utils
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
        # Usando la función de validación importada de utils
        vcmd_wait = (self.register(validate_numeric_input), '%P')
        self.wait_entry = ctk.CTkEntry(self, width=50, height=25, fg_color="white", bg_color="#000001",
                                       border_color="gray", validate="key", validatecommand=vcmd_wait)
        self.wait_entry.insert(0, "5")
        self.wait_entry.place(x=210, y=55)
        pywinstyles.set_opacity(self.wait_entry, color="#000001")
        self.wait_entry.bind("<MouseWheel>", self.on_wait_scroll)
        self.wait_entry.bind("<Button-4>", self.on_wait_scroll)
        self.wait_entry.bind("<Button-5>", self.on_wait_scroll)
        
        ### BOTÓN MOSTRAR
        self.visible_img = ctk.CTkImage(Image.open("assets/visible.png"), size=(20, 20))
        self.invisible_img = ctk.CTkImage(Image.open("assets/invisible.png"), size=(20, 20))
        self.ojo_estado = True

        self.ojo_btn = ctk.CTkButton(self, image=self.invisible_img, text="", width=25, height=25,
                                        bg_color="#000001", fg_color="transparent", command=self.toggle_password)
        self.ojo_btn.place(x=265, y=55)
        pywinstyles.set_opacity(self.ojo_btn, color="#000001")
        
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
                                      command=self.stop_writing_process, state="disabled") # Inicialmente deshabilitado
        self.stop_btn.place(x=320, y=70) # Ubicación debajo del botón Play/Pausa
        pywinstyles.set_opacity(self.stop_btn, color="#000001")

    def update_file_combobox(self):
        """Actualiza las opciones del combobox de archivos."""
        self.file_options = get_latest_files(self.files_directory) # Usando función de utils
        if not self.file_options:
            self.file_combobox.configure(values=["No files found"])
            self.file_combobox.set("No files found")
        else:
            file_names = [os.path.basename(f) for f in self.file_options]
            self.file_combobox.configure(values=file_names)
            self.file_combobox.set(file_names[0])

    def subir_archivo(self):
        """Permite al usuario seleccionar y subir un archivo .txt."""
        from tkinter import filedialog # Se importa aquí para evitar circularidad en algunos setups
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if copy_file_to_directory(ruta, self.files_directory): # Usando función de utils
            self.update_file_combobox()

    # on_delay_scroll y on_wait_scroll manejan los ajustes de los Entrys con la rueda del mouse
    def on_delay_scroll(self, event):
        """Maneja el evento de la rueda del mouse para cambiar el valor de delay_entry."""
        current_value = 0.0
        try:
            current_value = float(self.delay_entry.get())
        except ValueError:
            self.delay_entry.delete(0, ctk.END)
            self.delay_entry.insert(0, "0.0")
            current_value = 0.0

        if event.delta > 0 or event.num == 4:  # Rueda hacia arriba (Windows/macOS: delta > 0, Linux: Button-4)
            new_value = current_value + 0.05
        elif event.delta < 0 or event.num == 5: # Rueda hacia abajo (Windows/macOS: delta < 0, Linux: Button-5)
            new_value = current_value - 0.05
        else:
            return

        if new_value < 0:
            new_value = 0.0

        self.delay_entry.delete(0, ctk.END)
        self.delay_entry.insert(0, f"{new_value:.2f}") # Formatear a 2 decimales

    def on_wait_scroll(self, event):
        """Maneja el evento de la rueda del mouse para cambiar el valor de wait_entry."""
        current_value = 0
        try:
            # Convertir a float primero para manejar posibles puntos decimales, luego a int
            current_value = int(float(self.wait_entry.get()))
        except ValueError:
            self.wait_entry.delete(0, ctk.END)
            self.wait_entry.insert(0, "0")
            current_value = 0

        if event.delta > 0 or event.num == 4: # Rueda hacia arriba
            new_value = current_value + 1
        elif event.delta < 0 or event.num == 5: # Rueda hacia abajo
            new_value = current_value - 1
        else:
            return

        if new_value < 0:
            new_value = 0 # No permitir valores negativos

        self.wait_entry.delete(0, ctk.END)
        self.wait_entry.insert(0, str(new_value)) # Insertar como string (entero)

    def toggle_play_pause(self):
        """Alterna entre iniciar, pausar y reanudar el proceso de escritura."""
        if not self.writer_manager.is_running:
            # Si no hay hilo de escritura activo, iniciamos uno nuevo
            selected_file_name = self.file_combobox.get()
            if selected_file_name == "No files found":
                print("No se ha seleccionado ningún archivo para iniciar.")
                return

            full_path = os.path.join(self.files_directory, selected_file_name)
            
            delay_value = 0.0
            try:
                delay_value = float(self.delay_entry.get())
            except ValueError:
                print("Valor de Delay no válido. Usando 0.0 por defecto.")
                
            wait_value = 0
            try:
                wait_value = int(float(self.wait_entry.get()))
            except ValueError:
                print("Valor de Espera no válido. Usando 0 por defecto.")

            # Inicia el proceso a través del gestor de escritura
            self.writer_manager.start(full_path, delay_value, wait_value)
            
            # Actualiza la GUI al iniciar el proceso
            self.play_pause_btn.configure(image=self.pause_img, state="normal")
            self.stop_btn.configure(state="normal") # Habilita el botón de detener
        else:
            # Si hay un hilo activo, alternamos entre pausa y reanudación
            if self.writer_manager.is_paused:
                self.writer_manager.resume()
                self.play_pause_btn.configure(image=self.pause_img)
            else:
                self.writer_manager.pause()
                self.play_pause_btn.configure(image=self.play_img)

    def stop_writing_process(self):
        """Detiene completamente el proceso de escritura a través del gestor."""
        self.writer_manager.stop()

    def _reset_gui_state(self):
        """
        Función auxiliar para resetear el estado de los botones de la GUI
        después de que el proceso de escritura termina (éxito, error o detención).
        Es llamada de forma segura desde el hilo secundario mediante `self.after()`.
        """
        self.play_pause_btn.configure(image=self.play_img, state="normal")
        self.stop_btn.configure(state="disabled")


    def toggle_password(self):
        """Alterna la visibilidad de un campo de contraseña (si lo hubiera)."""

        if self.ojo_estado:
            self.ojo_btn.configure(image=self.invisible_img)
        else:
            self.ojo_btn.configure(image=self.visible_img)
        self.ojo_estado = not self.ojo_estado
        
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()