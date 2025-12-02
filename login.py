import tkinter as tk
import customtkinter as ctk
import sqlite3
import hashlib
import os
import sys
from tkinter import messagebox
from menu_principal import MenuPrincipal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def get_db_path():
    """Obtiene la ruta correcta de la base de datos según el entorno"""
    # Si estamos en el .exe (PyInstaller)
    if getattr(sys, 'frozen', False):
        # Directorio del .exe
        exe_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(exe_dir, "InventarioBD_2.db")

        if os.path.exists(db_path):
            return db_path

        # Buscar en otras ubicaciones
        possible_paths = [
            db_path,
            os.path.join(os.getcwd(), "InventarioBD_2.db"),
            "InventarioBD_2.db",
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                return path

        return db_path  # Para crear nueva si no existe
    else:
        # En desarrollo - RUTA ABSOLUTA como tenías antes
        return "C:/Users/alexa/IdeaProjects/aplicacion/InventarioBD_2.db"

class LoginFrame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario - Login")
        self.root.geometry("1000x500")  # <-- TAMAÑO 1000x500
        self.root.resizable(False, False)  # Mantener tamaño fijo

        # Obtener ruta de BD
        self.db_path = get_db_path()
        print(f"📁 Ruta de BD: {self.db_path}")
        print(f"📂 ¿Existe?: {os.path.exists(self.db_path)}")

        # Conectar a BD
        self.conectar_bd()

        # Crear interfaz CON TUS COLORES ORIGINALES y tamaño 1000x500
        self.crear_interfaz()

    def conectar_bd(self):
        """Conecta a la base de datos y verifica tabla usuarios"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("✅ Conexión exitosa a BD")

            # VERIFICAR que la tabla 'usuarios' existe
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
            tabla_existe = self.cursor.fetchone()

            if not tabla_existe:
                print("❌ Tabla 'usuarios' NO existe")
                # Crear tabla si no existe
                self.crear_tabla_usuarios()

            # Verificar si hay usuarios
            self.cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = self.cursor.fetchone()[0]
            print(f"👥 Total usuarios en BD: {count}")

            if count == 0:
                print("⚠️ La tabla 'usuarios' está vacía, creando usuario admin...")
                self.crear_usuario_admin()

        except sqlite3.Error as e:
            print(f"❌ Error de SQLite: {e}")
            messagebox.showerror("Error BD", f"Error de base de datos:\n{str(e)}")
            self.root.destroy()
        except Exception as e:
            print(f"❌ Error general: {e}")
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
            self.root.destroy()

    def crear_tabla_usuarios(self):
        """Crea la tabla de usuarios si no existe"""
        try:
            self.cursor.execute('''
                                CREATE TABLE IF NOT EXISTS usuarios (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        usuario TEXT UNIQUE NOT NULL,
                                                                        contrasena TEXT NOT NULL,
                                                                        rol TEXT NOT NULL
                                )
                                ''')
            self.conn.commit()
            print("✅ Tabla 'usuarios' creada")
        except Exception as e:
            print(f"❌ Error creando tabla: {e}")

    def crear_usuario_admin(self):
        """Crea usuario admin por defecto"""
        try:
            contrasena_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                ("admin", contrasena_hash, "admin")
            )
            self.conn.commit()
            print("✅ Usuario admin creado (admin/admin123)")
        except Exception as e:
            print(f"❌ Error creando usuario admin: {e}")

    def crear_interfaz(self):
        """Crea la interfaz gráfica para 1000x500 con tus colores"""
        # Frame principal que ocupa toda la ventana
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#1e3c72")
        self.main_frame.pack(fill="both", expand=True)

        # Frame central para el formulario (centrado)
        center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título más grande para pantalla grande
        title_label = ctk.CTkLabel(
            center_frame,
            text="SISTEMA DE INVENTARIO",
            font=("Arial", 32, "bold"),
            text_color="white"
        )
        title_label.pack(pady=(0, 20))

        subtitle_label = ctk.CTkLabel(
            center_frame,
            text="INICIAR SESIÓN",
            font=("Arial", 24),
            text_color="white"
        )
        subtitle_label.pack(pady=(0, 40))

        # Frame del formulario
        form_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        form_frame.pack()

        # Usuario
        user_label = ctk.CTkLabel(
            form_frame,
            text="Usuario:",
            font=("Arial", 18),
            text_color="white"
        )
        user_label.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")

        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingrese su usuario",
            width=400,
            height=50,
            font=("Arial", 16),
            corner_radius=8
        )
        self.username_entry.grid(row=0, column=1, padx=(0, 0), pady=10)

        # Contraseña
        pass_label = ctk.CTkLabel(
            form_frame,
            text="Contraseña:",
            font=("Arial", 18),
            text_color="white"
        )
        pass_label.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")

        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingrese su contraseña",
            width=400,
            height=50,
            show="•",
            font=("Arial", 16),
            corner_radius=8
        )
        self.password_entry.grid(row=1, column=1, padx=(0, 0), pady=10)

        # Opciones (Remember me)
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0), sticky="w")

        self.remember_var = ctk.BooleanVar(value=False)
        remember_check = ctk.CTkCheckBox(
            options_frame,
            text="Recordar usuario",
            variable=self.remember_var,
            font=("Arial", 14),
            text_color="white",
            fg_color="#f8bb00",
            hover_color="#e0a800"
        )
        remember_check.pack(side="left")

        # Botón LOGIN más grande
        login_btn = ctk.CTkButton(
            form_frame,
            text="INICIAR SESIÓN",
            command=self.verificar_login,
            width=400,
            height=55,
            font=("Arial", 20, "bold"),
            fg_color="#f8bb00",
            hover_color="#e0a800",
            text_color="black",
            corner_radius=10
        )
        login_btn.grid(row=3, column=0, columnspan=2, pady=(30, 20))

        # Información de ayuda
        help_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        help_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        # Mostrar usuarios disponibles
        try:
            self.cursor.execute("SELECT usuario, rol FROM usuarios")
            usuarios = self.cursor.fetchall()

            if usuarios:
                users_text = "Usuarios disponibles: "
                users_list = []
                for usuario, rol in usuarios:
                    users_list.append(f"{usuario} ({rol})")

                users_label = ctk.CTkLabel(
                    help_frame,
                    text=users_text + " | ".join(users_list),
                    font=("Arial", 12),
                    text_color="#cccccc"
                )
                users_label.pack()

                demo_label = ctk.CTkLabel(
                    help_frame,
                    text="Demo: admin / admin123",
                    font=("Arial", 12, "italic"),
                    text_color="#aaaaaa"
                )
                demo_label.pack(pady=(5, 0))
        except:
            pass

        # Footer
        footer_label = ctk.CTkLabel(
            self.main_frame,
            text="© 2024 Sistema de Inventario - Universidad de Sonora",
            font=("Arial", 12),
            text_color="#aaaaaa"
        )
        footer_label.pack(side="bottom", pady=20)

        # Permitir login con Enter
        self.password_entry.bind("<Return>", lambda e: self.verificar_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

    def verificar_login(self):
        """Verifica las credenciales en la tabla 'usuarios'"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Campos vacíos",
                                   "Por favor ingrese usuario y contraseña")
            return

        try:
            print(f"🔍 Buscando usuario: '{username}'")

            # Buscar usuario y contraseña hash
            self.cursor.execute(
                "SELECT usuario, contraseña, rol FROM usuarios WHERE usuario = ?",
                (username,)
            )
            resultado = self.cursor.fetchone()

            if not resultado:
                print(f"❌ Usuario '{username}' no encontrado")
                messagebox.showerror("Error", "Usuario no encontrado")
                self.password_entry.delete(0, tk.END)
                return

            usuario_db, hash_almacenado, rol = resultado

            # Hashear la contraseña ingresada
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            print(f"🔐 Hash ingresado: {password_hash[:15]}...")
            print(f"🔐 Hash almacenado: {hash_almacenado[:15]}...")

            # Comparar hashes
            if password_hash == hash_almacenado:
                print(f"✅ Login exitoso: {username} (Rol: {rol})")
                messagebox.showinfo("¡Bienvenido!", f"Acceso concedido: {username}\nRol: {rol}")
                self.abrir_menu_principal(username, rol)
            else:
                print("❌ Contraseña incorrecta")
                messagebox.showerror("Error", "Contraseña incorrecta")
                self.password_entry.delete(0, tk.END)

        except sqlite3.Error as e:
            print(f"❌ Error SQLite: {e}")
            messagebox.showerror("Error BD", f"Error de base de datos:\n{str(e)}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")

    def abrir_menu_principal(self, usuario, rol):
        """Abre el menú principal"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Cambiar tamaño para menú principal
        self.root.geometry("1000x500")  # Mantener 1000x500

        # Abrir menú principal
        MenuPrincipal(self.root, usuario, rol, self)

    def volver_login(self):
        """Vuelve a la pantalla de login"""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.__init__(self.root)

    def __del__(self):
        """Cierra la conexión a BD"""
        if hasattr(self, 'conn'):
            self.conn.close()
            print("🔌 Conexión a BD cerrada")

if __name__ == "__main__":
    # Para pruebas directas
    root = ctk.CTk()
    app = LoginFrame(root)
    root.mainloop()