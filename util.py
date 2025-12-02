# utils.py
import os
import sys


def resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_db_path():
    """Obtiene la ruta de la base de datos para el .exe"""
    # Si estamos en el .exe (PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        # Busca la base de datos en el directorio del .exe primero
        exe_dir = os.path.dirname(sys.executable)
        db_in_exe_dir = os.path.join(exe_dir, "InventarioBD_2.db")

        if os.path.exists(db_in_exe_dir):
            return db_in_exe_dir

        # Si no está en el directorio del .exe, usa la del paquete
        return os.path.join(sys._MEIPASS, "InventarioBD_2.db")

    # Si estamos en desarrollo, usa la ruta de desarrollo
    return "C:/Users/alexa/IdeaProjects/aplicacion/InventarioBD_2.db"


def get_image_path(relative_image_path):
    """Obtiene la ruta de una imagen para el .exe"""
    # Si estamos en el .exe (PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        # Busca en el directorio del .exe primero
        exe_dir = os.path.dirname(sys.executable)
        image_in_exe_dir = os.path.join(exe_dir, relative_image_path)

        if os.path.exists(image_in_exe_dir):
            return image_in_exe_dir

        # Si no está en el directorio del .exe, usa la del paquete
        return os.path.join(sys._MEIPASS, relative_image_path)

    # Si estamos en desarrollo, usa la ruta de desarrollo
    return relative_image_path