import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import pywinstyles
import os
import glob # Para listar archivos con patrones

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoEscrito")
        self.geometry("400x120")
        self.resizable(False, False)

        # Directorio de los archivos
        self.files_directory = "files" 
        # Asegurarse de que la carpeta 'files' exista
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
        self.file_options = self.get_latest_files()
        # Asegúrate de que haya al menos una opción para evitar errores si la carpeta está vacía
        if not self.file_options:
            self.file_options = ["No files found"]
            latest_file = "No files found"
        else:
            latest_file = os.path.basename(self.file_options[0]) # Solo el nombre del archivo

        self.file_combobox = ctk.CTkComboBox(self, width=200, height=25,
                                             values=[os.path.basename(f) for f in self.file_options],
                                             fg_color="#000001", bg_color="#000001",
                                             border_color="gray", text_color="black")
        self.file_combobox.place(x=110, y=20)
        self.file_combobox.set(latest_file) # Establece el último archivo como el valor inicial
        pywinstyles.set_opacity(self.file_combobox, color="#000001")


        ### LABEL DELAY
        self.delay_label = ctk.CTkLabel(self, text="Delay:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.delay_label.place(x=72, y=55)
        pywinstyles.set_opacity(self.delay_label, color="#000001")

        ### ENTRY DELAY
        self.delay_entry = ctk.CTkEntry(self, width=50, height=25, fg_color="#000001", bg_color="#000001", border_color="gray")
        self.delay_entry.insert(0, "0.5")
        self.delay_entry.place(x=110, y=55)
        pywinstyles.set_opacity(self.delay_entry, color="#000001")

        ### LABEL ESPERA
        self.wait_label = ctk.CTkLabel(self, text="Espera:", text_color="black", font=("Arial", 10), bg_color="#000001")
        self.wait_label.place(x=170, y=55)
        pywinstyles.set_opacity(self.wait_label, color="#000001")

        ### ENTRY ESPERA
        self.wait_entry = ctk.CTkEntry(self, width=50, height=25, fg_color="#000001", bg_color="#000001", border_color="gray")
        self.wait_entry.insert(0, "5")
        self.wait_entry.place(x=210, y=55)
        pywinstyles.set_opacity(self.wait_entry, color="#000001")
        
        ### BOTÓN MOSTRAR
        self.visible_img = ctk.CTkImage(Image.open("assets/visible.png"), size=(20, 20))
        self.invisible_img = ctk.CTkImage(Image.open("assets/invisible.png"), size=(20, 20))
        self.ojo_estado = True

        self.ojo_btn = ctk.CTkButton(self, image=self.invisible_img, text="", width=25, height=25,
                                        bg_color="#000001", fg_color="transparent", command=self.toggle_password)
        self.ojo_btn.place(x=265, y=55)
        pywinstyles.set_opacity(self.ojo_btn, color="#000001")
        
        ### BOTÓN PLAY
        self.play_img = ctk.CTkImage(Image.open("assets/play.png"), size=(50, 50))
        self.play_btn = ctk.CTkButton(self, image=self.play_img, text="", width=50, height=50,
                                        bg_color="#000001", fg_color="#000001", hover=False, corner_radius=5,
                                        command=self.iniciar)
        self.play_btn.place(x=320, y=20)
        pywinstyles.set_opacity(self.play_btn, color="#000001")

    def get_latest_files(self):
        """Obtiene la lista de archivos .txt en la carpeta 'files' y los ordena por fecha de modificación."""
        list_of_files = glob.glob(os.path.join(self.files_directory, "*.txt"))
        # Ordena los archivos por fecha de modificación (el más reciente primero)
        list_of_files.sort(key=os.path.getmtime, reverse=True)
        return list_of_files

    def update_file_combobox(self):
        """Actualiza las opciones del combobox con los archivos más recientes."""
        self.file_options = self.get_latest_files()
        if not self.file_options:
            self.file_combobox.configure(values=["No files found"])
            self.file_combobox.set("No files found")
        else:
            # Solo muestra el nombre del archivo en el combobox
            file_names = [os.path.basename(f) for f in self.file_options]
            self.file_combobox.configure(values=file_names)
            self.file_combobox.set(file_names[0]) # Selecciona el archivo más reciente

    def subir_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if ruta:
            # Copia el archivo seleccionado a la carpeta 'files'
            file_name = os.path.basename(ruta)
            destination_path = os.path.join(self.files_directory, file_name)
            
            # Puedes agregar un control para evitar sobrescribir si el archivo ya existe
            # O simplemente sobrescribir si es el comportamiento deseado
            import shutil
            shutil.copy(ruta, destination_path)
            
            self.update_file_combobox() # Actualiza el combobox después de subir un archivo

    def iniciar(self):
        selected_file_name = self.file_combobox.get()
        if selected_file_name == "No files found":
            print("No se ha seleccionado ningún archivo para iniciar.")
        else:
            full_path = os.path.join(self.files_directory, selected_file_name)
            print(f"Iniciando con el archivo: {full_path}")
            # Aquí iría la lógica para procesar el archivo seleccionado
            # Por ejemplo, leer su contenido:
            # try:
            #     with open(full_path, 'r', encoding='utf-8') as f:
            #         content = f.read()
            #         print("Contenido del archivo:\n", content)
            # except FileNotFoundError:
            #     print(f"Error: El archivo {full_path} no fue encontrado.")
            # except Exception as e:
            #     print(f"Ocurrió un error al leer el archivo: {e}")

    def toggle_password(self):
        if self.ojo_estado:
            self.ojo_btn.configure(image=self.invisible_img)
        else:
            self.ojo_btn.configure(image=self.visible_img)
        self.ojo_estado = not self.ojo_estado
        
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = App()
    app.mainloop()