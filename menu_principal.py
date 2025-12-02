import tkinter as tk
import customtkinter as ctk
from PIL import Image
import os
import sys
from productos import ProductosFrame
from almacenes import AlmacenesFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def get_image_path(relative_path):
    """Obtiene la ruta de una imagen"""
    # Si estamos en el .exe (PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        # Busca en el directorio del .exe
        exe_dir = os.path.dirname(sys.executable)
        image_path = os.path.join(exe_dir, relative_path)

        if os.path.exists(image_path):
            return image_path

        # Busca en los datos del paquete
        return os.path.join(sys._MEIPASS, relative_path)

    # Si estamos en desarrollo
    return relative_path

class MenuPrincipal(ctk.CTkFrame):
    def __init__(self, root, usuario, rol, login_frame=None):
        super().__init__(root, fg_color="#1e3c72")
        self.root = root
        self.usuario = usuario
        self.rol = rol
        self.login_frame = login_frame
        self.pack(fill="both", expand=True)

        self.frame_actual = None

        # Carga la imagen
        try:
            imagen_path = get_image_path("logosunison/ESCUDO-COLOR.png")
            self.imagen_logo = ctk.CTkImage(
                dark_image=Image.open(imagen_path),
                size=(600, 300)
            )
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.imagen_logo = None

        self.crear_menu()  # <-- Esto llama al método
        self.mostrar_inicio()

    def limpiar_pantalla(self):
        if self.frame_actual:
            self.frame_actual.destroy()

    def mostrar_inicio(self):
        self.limpiar_pantalla()

        frame = ctk.CTkFrame(self, fg_color="#1e3c72")
        frame.pack(fill="both", expand=True)

        if self.imagen_logo:
            label_imagen = ctk.CTkLabel(frame, image=self.imagen_logo, text="", bg_color="#1e3c72")
            label_imagen.pack(pady=20)
        else:
            ctk.CTkLabel(frame, text="Sistema de Inventario",
                         font=("Arial", 24), text_color="white", bg_color="#1e3c72").pack(pady=20)

        # Mostrar información del usuario actual
        ctk.CTkLabel(frame, text=f"Usuario: {self.usuario}",
                     font=("Arial", 16), text_color="white", bg_color="#1e3c72").pack(pady=5)
        ctk.CTkLabel(frame, text=f"Rol: {self.rol}",
                     font=("Arial", 14), text_color="white", bg_color="#1e3c72").pack(pady=5)

        boton = ctk.CTkButton(frame, text="Alexander Morales Quiroz",
                              fg_color="#f8bb00", text_color="black")
        boton.pack(pady=(20, 10))

        self.frame_actual = frame

    def mostrar_productos(self):
        self.limpiar_pantalla()
        self.frame_actual = ProductosFrame(self, self.rol, self.login_frame)
        self.frame_actual.pack(fill="both", expand=True)

    def mostrar_almacenes(self):
        try:
            self.limpiar_pantalla()
            self.frame_actual = AlmacenesFrame(self, self.rol, self.login_frame)
            self.frame_actual.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            print(f"Error al cargar almacenes: {e}")
            traceback.print_exc()
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo cargar la ventana de almacenes: {str(e)}")
            self.mostrar_inicio()

    def volver_login(self):  # <-- MÉTODO CORRECTO DE LA CLASE
        for widget in self.root.winfo_children():
            widget.destroy()
        from login import LoginFrame
        import os
        import sys

        if hasattr(sys, '_MEIPASS'):
            db_path = os.path.join(os.path.dirname(sys.executable), "InventarioBD_2.db")
        else:
            db_path = "C:/Users/alexa/IdeaProjects/aplicacion/InventarioBD_2.db"

        LoginFrame(self.root)

    def crear_menu(self):  # <-- MÉTODO CORRECTO DE LA CLASE (nivel correcto)
        menu_barra = tk.Menu(self.root, background="#1e3c72", foreground="white",
                             activebackground="#f8bb00", activeforeground="black")

        menu_opciones = tk.Menu(menu_barra, tearoff=0, background="#1e3c72", foreground="white",
                                activebackground="#f8bb00", activeforeground="black")

        menu_opciones.add_command(label="Menú principal", command=self.mostrar_inicio)
        menu_opciones.add_separator()
        menu_opciones.add_command(label="Abrir ventana de productos", command=self.mostrar_productos)
        menu_opciones.add_command(label="Abrir ventana de almacenes", command=self.mostrar_almacenes)
        menu_opciones.add_separator()
        menu_opciones.add_command(label="Cerrar sesión", command=self.volver_login)
        menu_opciones.add_command(label="Salir", command=self.root.destroy)

        menu_barra.add_cascade(label="Menú", menu=menu_opciones)
        self.root.config(menu=menu_barra)