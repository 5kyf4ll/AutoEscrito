import os
import glob
import shutil
from tkinter import filedialog # Importado específicamente para askopenfilename

def validate_numeric_input(P):
    """Valida que la entrada de un string sea un número (entero o flotante)."""
    if P == "" or P == "-" or P == ".": # Permitir entrada vacía o solo signos para empezar a escribir
        return True
    try:
        float(P) # Intenta convertir a flotante
        return True
    except ValueError:
        return False

def get_latest_files(directory):
    """
    Obtiene la lista de archivos .txt más recientes en un directorio,
    ordenados por fecha de modificación descendente.
    """
    list_of_files = glob.glob(os.path.join(directory, "*.txt"))
    list_of_files.sort(key=os.path.getmtime, reverse=True)
    return list_of_files

def copy_file_to_directory(source_path, destination_directory):
    """
    Copia un archivo desde una ruta de origen a un directorio de destino.
    Devuelve True si la copia fue exitosa, False en caso contrario.
    """
    if source_path:
        file_name = os.path.basename(source_path)
        destination_path = os.path.join(destination_directory, file_name)
        try:
            shutil.copy(source_path, destination_path)
            print(f"Archivo copiado: {file_name} a {destination_directory}")
            return True
        except Exception as e:
            print(f"Error al copiar archivo {file_name}: {e}")
            return False
    return False