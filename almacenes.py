import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox
import datetime


class AlmacenesFrame(ctk.CTkFrame):
    def __init__(self, master, rol, login_frame=None, db_path="C:/Users/alexa/IdeaProjects/aplicacion/InventarioBD_2.db"):
        super().__init__(master, fg_color="#1e3c72")
        self.db_path = db_path
        self.master = master
        self.rol = rol
        self.login_frame = login_frame
        self.usuario_actual = getattr(master, 'usuario', 'admin')  # Usuario por defecto

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.crear_tabla_actualizada()
        self.registro_seleccionado = None  # Para almacenar el registro seleccionado

        self.vista_actual = None
        self.mostrar_vista_lista()

    # ===========================================================
    # ACTUALIZAR TABLA EXISTENTE
    # ===========================================================
    def crear_tabla_actualizada(self):
        # Verificar si la tabla existe
        self.cursor.execute("PRAGMA table_info(almacenes)")
        columnas_existentes = [col[1] for col in self.cursor.fetchall()]

        # Si la tabla no existe, crearla con la nueva estructura
        if not columnas_existentes:
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS almacenes (
                                                                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                         nombre TEXT NOT NULL,
                                                                         fechamodificacion INTEGER NOT NULL,
                                                                         usuario INTEGER NOT NULL
                                )
                                """)
        else:
            # Si existe pero no tiene las nuevas columnas, agregarlas
            if 'fechamodificacion' not in columnas_existentes:
                self.cursor.execute("ALTER TABLE almacenes ADD COLUMN fechamodificacion INTEGER")
            if 'usuario' not in columnas_existentes:
                self.cursor.execute("ALTER TABLE almacenes ADD COLUMN usuario INTEGER")

            # Actualizar registros existentes con valores por defecto
            timestamp_actual = int(datetime.datetime.now().timestamp())
            self.cursor.execute("""
                                UPDATE almacenes
                                SET fechamodificacion = COALESCE(fechamodificacion, ?),
                                    usuario = COALESCE(usuario, 1)
                                WHERE fechamodificacion IS NULL OR usuario IS NULL
                                """, (timestamp_actual,))

        self.conn.commit()

    # ===========================================================
    # OBTENER DATOS DE AUDITORÍA
    # ===========================================================
    def obtener_datos_auditoria(self):
        timestamp = int(datetime.datetime.now().timestamp())

        # Obtener ID de usuario de forma segura
        if self.login_frame and hasattr(self.login_frame, 'obtener_id_usuario'):
            usuario_id = self.login_frame.obtener_id_usuario(self.login_frame.usuario_actual)
        else:
            # Si no hay login_frame, usar usuario por defecto (admin)
            self.cursor.execute("SELECT id FROM usuarios WHERE usuario=?", ("admin",))
            resultado = self.cursor.fetchone()
            usuario_id = resultado[0] if resultado else 1

        return timestamp, usuario_id

    # ===========================================================
    # CAMBIO DE VISTAS
    # ===========================================================
    def limpiar_vista(self):
        if self.vista_actual:
            self.vista_actual.destroy()

    def mostrar_vista_lista(self):
        self.limpiar_vista()
        self.vista_actual = ctk.CTkFrame(self, fg_color="#1e3c72")
        self.vista_actual.pack(fill="both", expand=True)
        self.crear_interfaz_lista(self.vista_actual)
        self.mostrar_datos()

    def mostrar_vista_agregar(self):
        self.limpiar_vista()
        self.vista_actual = ctk.CTkFrame(self, fg_color="#1e3c72")
        self.vista_actual.pack(fill="both", expand=True)
        self.crear_interfaz_agregar(self.vista_actual)

    def mostrar_vista_editar(self, registro):
        self.limpiar_vista()
        self.vista_actual = ctk.CTkFrame(self, fg_color="#1e3c72")
        self.vista_actual.pack(fill="both", expand=True)
        self.crear_interfaz_editar(self.vista_actual, registro)

    # ===========================================================
    # VISTA PRINCIPAL (TABLA + FILTROS)
    # ===========================================================
    def crear_interfaz_lista(self, frame):

        # ------------ FILTROS ------------
        filtro = ctk.CTkFrame(frame, fg_color="#1e3c72")
        filtro.pack(fill="x", padx=10, pady=10)

        self.f_id = ctk.CTkEntry(filtro, placeholder_text="ID", width=80)
        self.f_id.grid(row=0, column=0, padx=5)

        self.f_nombre = ctk.CTkEntry(filtro, placeholder_text="Nombre", width=150)
        self.f_nombre.grid(row=0, column=1, padx=5)

        ctk.CTkButton(filtro, text="Filtrar", fg_color="#f8bb00", text_color="black",
                      command=self.aplicar_filtros).grid(row=0, column=2, padx=10)
        ctk.CTkButton(filtro, text="Limpiar", fg_color="#f8bb00", text_color="black",
                      command=self.limpiar_filtros).grid(row=0, column=3, padx=10)

        # ------------ TABLA ------------
        tabla_frame = ctk.CTkFrame(frame, fg_color="#1e3c72")
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("id", "nombre", "fecha_modificacion", "usuario")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

        # Configurar estilo para la tabla (fondo blanco)
        estilo = ttk.Style()
        estilo.configure("Treeview",
                         background="white",
                         foreground="black",
                         fieldbackground="white",
                         rowheight=25)

        estilo.configure("Treeview.Heading",
                         background="#f8bb00",
                         foreground="black",
                         relief="flat",
                         font=('Arial', 10, 'bold'))

        estilo.map("Treeview.Heading",
                   background=[('active', '#e6a900')])

        # Configurar encabezados
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("fecha_modificacion", text="Fecha Modificación")
        self.tabla.heading("usuario", text="Usuario")

        # Configurar anchos de columnas
        self.tabla.column("id", width=50)
        self.tabla.column("nombre", width=200)
        self.tabla.column("fecha_modificacion", width=180)
        self.tabla.column("usuario", width=150)

        self.tabla.pack(fill="both", expand=True)

        # Bind para selección
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        # ------------ BOTONES ------------
        botones = ctk.CTkFrame(frame, fg_color="#1e3c72")
        botones.pack(fill="x", pady=10)

        botones_superiores = ctk.CTkFrame(botones, fg_color="#1e3c72")
        botones_superiores.pack(fill="x", pady=5)

        if self.rol in ("admin", "almacenes"):
            ctk.CTkButton(botones_superiores, text="Agregar nuevo",
                          fg_color="#f8bb00",
                          text_color="black",
                          command=self.mostrar_vista_agregar).pack(side="left", padx=10)

            ctk.CTkButton(botones_superiores, text="Editar seleccionado",
                          fg_color="#f8bb00",
                          text_color="black",
                          command=self.editar_seleccionado).pack(side="left", padx=10)

            ctk.CTkButton(botones_superiores, text="Eliminar seleccionado",
                          fg_color="#c0392b",
                          text_color="white",
                          command=self.eliminar_seleccionado).pack(side="left", padx=10)

        botones_inferiores = ctk.CTkFrame(botones, fg_color="#1e3c72")
        botones_inferiores.pack(fill="x", pady=5)

        ctk.CTkButton(botones_inferiores, text="Volver al menú",
                      fg_color="#f8bb00",
                      text_color="black",
                      command=self.master.mostrar_inicio).pack(side="right", padx=10)

    # ===========================================================
    # SELECCIÓN DE REGISTRO
    # ===========================================================
    def seleccionar_registro(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            item = seleccion[0]
            self.registro_seleccionado = self.tabla.item(item, "values")
        else:
            self.registro_seleccionado = None

    def editar_seleccionado(self):
        if not self.registro_seleccionado:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un registro para editar.")
            return
        self.mostrar_vista_editar(self.registro_seleccionado)

    def eliminar_seleccionado(self):
        if not self.registro_seleccionado:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un registro para eliminar.")
            return

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el almacén '{self.registro_seleccionado[1]}'?"
        )

        if respuesta:
            try:
                self.cursor.execute("DELETE FROM almacenes WHERE id=?", (self.registro_seleccionado[0],))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Almacén eliminado correctamente.")
                self.mostrar_vista_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el almacén: {str(e)}")

    # ===========================================================
    # DATOS
    # ===========================================================
    def mostrar_datos(self):
        for elem in self.tabla.get_children():
            self.tabla.delete(elem)

        self.cursor.execute("""
                            SELECT
                                a.id,
                                a.nombre,
                                datetime(a.fechamodificacion, 'unixepoch') as fecha_modificacion,
                                u.usuario
                            FROM almacenes a
                                     LEFT JOIN usuarios u ON a.usuario = u.id
                            """)

        for row in self.cursor.fetchall():
            self.tabla.insert("", "end", values=row)

    # ===========================================================
    # FILTROS
    # ===========================================================
    def aplicar_filtros(self):
        filtros = []
        vals = []

        if self.f_id.get():
            filtros.append("a.id=?")
            vals.append(self.f_id.get())

        if self.f_nombre.get():
            filtros.append("a.nombre LIKE ?")
            vals.append("%" + self.f_nombre.get() + "%")

        query = """
                SELECT
                    a.id,
                    a.nombre,
                    datetime(a.fechamodificacion, 'unixepoch') as fecha_modificacion,
                    u.usuario
                FROM almacenes a
                         LEFT JOIN usuarios u ON a.usuario = u.id \
                """

        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.cursor.execute(query, vals)
        for row in self.cursor.fetchall():
            self.tabla.insert("", "end", values=row)

    def limpiar_filtros(self):
        self.f_id.delete(0, "end")
        self.f_nombre.delete(0, "end")
        self.mostrar_datos()

    # ===========================================================
    # VISTA AGREGAR
    # ===========================================================
    def crear_interfaz_agregar(self, frame):

        ctk.CTkLabel(frame, text="Agregar nuevo almacén", font=("Arial", 20),
                     text_color="white", bg_color="#1e3c72").pack(pady=10)

        form = ctk.CTkFrame(frame, fg_color="#1e3c72")
        form.pack(pady=20)

        ctk.CTkLabel(form, text="Nombre:", text_color="white", bg_color="#1e3c72").grid(row=0, column=0, padx=5, pady=5)
        self.nuevo_nombre = ctk.CTkEntry(form, width=300)
        self.nuevo_nombre.grid(row=0, column=1, padx=5, pady=5)

        botones = ctk.CTkFrame(frame, fg_color="#1e3c72")
        botones.pack(pady=10)

        ctk.CTkButton(botones, text="Guardar", fg_color="#f8bb00", text_color="black",
                      command=self.guardar_nuevo).pack(side="left", padx=10)

        ctk.CTkButton(botones, text="Cancelar", fg_color="#f8bb00", text_color="black",
                      command=self.mostrar_vista_lista).pack(side="right", padx=10)

    def guardar_nuevo(self):
        try:
            nombre = self.nuevo_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un nombre para el almacén.")
                return

            # Obtener datos de auditoría
            timestamp, usuario_id = self.obtener_datos_auditoria()

            self.cursor.execute("""
                                INSERT INTO almacenes(
                                    nombre,
                                    fechamodificacion,
                                    usuario
                                ) VALUES (?, ?, ?)
                                """, (nombre, timestamp, usuario_id))
            self.conn.commit()

            messagebox.showinfo("Éxito", "Almacén agregado correctamente.")
            self.mostrar_vista_lista()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===========================================================
    # VISTA EDITAR
    # ===========================================================
    def crear_interfaz_editar(self, frame, registro):
        ctk.CTkLabel(frame, text="Editar almacén", font=("Arial", 20),
                     text_color="white", bg_color="#1e3c72").pack(pady=10)

        form = ctk.CTkFrame(frame, fg_color="#1e3c72")
        form.pack(pady=20)

        ctk.CTkLabel(form, text="ID:", text_color="white", bg_color="#1e3c72").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(form, text=registro[0], text_color="white", bg_color="#1e3c72").grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Nombre:", text_color="white", bg_color="#1e3c72").grid(row=1, column=0, padx=5, pady=5)
        self.editar_nombre = ctk.CTkEntry(form, width=300)
        self.editar_nombre.insert(0, registro[1])
        self.editar_nombre.grid(row=1, column=1, padx=5, pady=5)

        botones = ctk.CTkFrame(frame, fg_color="#1e3c72")
        botones.pack(pady=10)

        ctk.CTkButton(botones, text="Guardar cambios", fg_color="#f8bb00", text_color="black",
                      command=lambda: self.guardar_edicion(registro[0])).pack(side="left", padx=10)

        ctk.CTkButton(botones, text="Cancelar", fg_color="#f8bb00", text_color="black",
                      command=self.mostrar_vista_lista).pack(side="right", padx=10)

    def guardar_edicion(self, registro_id):
        try:
            nuevo_nombre = self.editar_nombre.get().strip()
            if not nuevo_nombre:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un nombre para el almacén.")
                return

            # Obtener datos de auditoría para la actualización
            timestamp, usuario_id = self.obtener_datos_auditoria()

            self.cursor.execute("""
                                UPDATE almacenes
                                SET nombre=?, fechamodificacion=?, usuario=?
                                WHERE id=?
                                """, (nuevo_nombre, timestamp, usuario_id, registro_id))
            self.conn.commit()

            messagebox.showinfo("Éxito", "Almacén actualizado correctamente.")
            self.mostrar_vista_lista()

        except Exception as e:
            messagebox.showerror("Error", str(e))