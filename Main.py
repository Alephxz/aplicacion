import customtkinter as ctk
from login import LoginFrame

if __name__ == "__main__":
    # Configurar apariencia
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    # Crear ventana principal
    root = ctk.CTk()
    root.title("Sistema de Inventario")

    # Crear login - se encarga de todo automáticamente
    app = LoginFrame(root)  # Esto establecerá 1000x500 automáticamente

    # Iniciar aplicación
    root.mainloop()