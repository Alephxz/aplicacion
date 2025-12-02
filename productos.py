import customtkinter as ctk
import sqlite3
from tkinter import messagebox, ttk, filedialog
import shutil
import datetime


class ProductosFrame(ctk.CTkFrame):
    def __init__(self, master, rol, login_frame=None, db_path="C:/Users/alexa/IdeaProjects/aplicacion/InventarioBD_2.db"):
        super().__init__(master, fg_color="#1e3c72")
        self.db_path = db_path
        self.master = master
        self.rol = rol
        self.login_frame = login_frame
        self.usuario_actual = getattr(master, 'usuario', 'admin')

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.crear_tabla_actualizada()
        self.almacenes_dict = self.cargar_almacenes()
        self.registro_seleccionado = None

        self.vista_actual = None
        self.mostrar_vista_lista()

    # ===========================================================
    # TABLA ACTUALIZADA
    # ===========================================================
    def crear_tabla_actualizada(self):
        # Verificar si la tabla existe
        self.cursor.execute("PRAGMA table_info(productos)")
        columnas_existentes = [col[1] for col in self.cursor.fetchall()]

        # Si la tabla no existe, crearla con la nueva estructura
        if not columnas_existentes:
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS productos (
                                                                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                         nombre TEXT NOT NULL,
                                                                         precio REAL NOT NULL,
                                                                         cantidad INTEGER NOT NULL,
                                                                         departamento TEXT NOT NULL,
                                                                         almacen INTEGER NOT NULL,
                                                                         fechamodificacion INTEGER NOT NULL,
                                                                         usuario INTEGER NOT NULL
                                )
                                """)
        else:
            # Si existe pero no tiene las nuevas columnas, agregarlas
            if 'fechamodificacion' not in columnas_existentes:
                self.cursor.execute("ALTER TABLE productos ADD COLUMN fechamodificacion INTEGER")
            if 'usuario' not in columnas_existentes:
                self.cursor.execute("ALTER TABLE productos ADD COLUMN usuario INTEGER")

            # Actualizar registros existentes con valores por defecto
            timestamp_actual = int(datetime.datetime.now().timestamp())
            self.cursor.execute("""
                                UPDATE productos
                                SET fechamodificacion = COALESCE(fechamodificacion, ?),
                                    usuario = COALESCE(usuario, 1)
                                WHERE fechamodificacion IS NULL OR usuario IS NULL
                                """, (timestamp_actual,))

        self.conn.commit()

    def cargar_almacenes(self):
        self.cursor.execute("SELECT id, nombre FROM almacenes")
        return {row[0]: row[1] for row in self.cursor.fetchall()}

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

        self.f_nombre = ctk.CTkEntry(filtro, placeholder_text="Nombre", width=120)
        self.f_nombre.grid(row=0, column=1, padx=5)

        self.f_precio = ctk.CTkEntry(filtro, placeholder_text="Precio", width=120)
        self.f_precio.grid(row=0, column=2, padx=5)

        self.f_cantidad = ctk.CTkEntry(filtro, placeholder_text="Cantidad", width=120)
        self.f_cantidad.grid(row=0, column=3, padx=5)

        self.f_departamento = ctk.CTkEntry(filtro, placeholder_text="Departamento", width=120)
        self.f_departamento.grid(row=0, column=4, padx=5)

        self.f_almacen = ctk.CTkComboBox(filtro, width=150, values=[""] + list(self.almacenes_dict.values()))
        self.f_almacen.grid(row=0, column=5, padx=5)

        ctk.CTkButton(filtro, text="Filtrar", fg_color="#f8bb00", text_color="black",
                      command=self.aplicar_filtros).grid(row=0, column=6, padx=10)
        ctk.CTkButton(filtro, text="Limpiar", fg_color="#f8bb00", text_color="black",
                      command=self.limpiar_filtros).grid(row=0, column=7, padx=10)

        # ------------ TABLA ------------
        tabla_frame = ctk.CTkFrame(frame, fg_color="#1e3c72")
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("id", "nombre", "precio", "cantidad", "departamento", "almacen", "fecha_modificacion", "usuario")
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
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("cantidad", text="Cantidad")
        self.tabla.heading("departamento", text="Departamento")
        self.tabla.heading("almacen", text="Almacén")
        self.tabla.heading("fecha_modificacion", text="Fecha Modificación")
        self.tabla.heading("usuario", text="Usuario")

        # Configurar anchos de columnas
        self.tabla.column("id", width=50)
        self.tabla.column("nombre", width=150)
        self.tabla.column("precio", width=100)
        self.tabla.column("cantidad", width=80)
        self.tabla.column("departamento", width=120)
        self.tabla.column("almacen", width=120)
        self.tabla.column("fecha_modificacion", width=150)
        self.tabla.column("usuario", width=120)

        self.tabla.pack(fill="both", expand=True)

        # Bind para selección
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        # ------------ BOTONES ------------
        botones = ctk.CTkFrame(frame, fg_color="#1e3c72")
        botones.pack(fill="x", pady=10)

        botones_superiores = ctk.CTkFrame(botones, fg_color="#1e3c72")
        botones_superiores.pack(fill="x", pady=5)

        if self.rol in ("admin", "productos"):
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
            f"¿Está seguro de que desea eliminar el producto '{self.registro_seleccionado[1]}'?"
        )

        if respuesta:
            try:
                self.cursor.execute("DELETE FROM productos WHERE id=?", (self.registro_seleccionado[0],))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                self.mostrar_vista_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el producto: {str(e)}")

    # ===========================================================
    # MOSTRAR DATOS (ACTUALIZADO)
    # ===========================================================
    def mostrar_datos(self):
        for elem in self.tabla.get_children():
            self.tabla.delete(elem)

        self.cursor.execute("""
                            SELECT
                                p.id,
                                p.nombre,
                                p.precio,
                                p.cantidad,
                                p.departamento,
                                a.nombre AS almacen,
                                datetime(p.fechamodificacion, 'unixepoch') as fecha_modificacion,
                                u.usuario
                            FROM productos p
                                     LEFT JOIN almacenes a ON p.almacen = a.id
                                     LEFT JOIN usuarios u ON p.usuario = u.id
                            """)

        for row in self.cursor.fetchall():
            self.tabla.insert("", "end", values=row)

    # ===========================================================
    # FILTROS (ACTUALIZADO)
    # ===========================================================
    def aplicar_filtros(self):
        filtros = []
        vals = []

        if self.f_id.get(): filtros.append("p.id=?"); vals.append(self.f_id.get())
        if self.f_nombre.get(): filtros.append("p.nombre LIKE ?"); vals.append("%" + self.f_nombre.get() + "%")
        if self.f_precio.get(): filtros.append("p.precio=?"); vals.append(self.f_precio.get())
        if self.f_cantidad.get(): filtros.append("p.cantidad=?"); vals.append(self.f_cantidad.get())
        if self.f_departamento.get(): filtros.append("p.departamento LIKE ?"); vals.append("%" + self.f_departamento.get() + "%")
        if self.f_almacen.get():
            nombre = self.f_almacen.get()
            almacen_id = next((i for i, n in self.almacenes_dict.items() if n == nombre), None)
            filtros.append("p.almacen=?")
            vals.append(almacen_id)

        query = """
                SELECT
                    p.id,
                    p.nombre,
                    p.precio,
                    p.cantidad,
                    p.departamento,
                    a.nombre AS almacen,
                    datetime(p.fechamodificacion, 'unixepoch') as fecha_modificacion,
                    u.usuario
                FROM productos p
                         LEFT JOIN almacenes a ON p.almacen = a.id
                         LEFT JOIN usuarios u ON p.usuario = u.id \
                """

        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        for elem in self.tabla.get_children():
            self.tabla.delete(elem)

        self.cursor.execute(query, vals)
        for row in self.cursor.fetchall():
            self.tabla.insert("", "end", values=row)

    def limpiar_filtros(self):
        self.f_id.delete(0, "end")
        self.f_nombre.delete(0, "end")
        self.f_precio.delete(0, "end")
        self.f_cantidad.delete(0, "end")
        self.f_departamento.delete(0, "end")
        self.f_almacen.set("")
        self.mostrar_datos()

    # ===========================================================
    # VISTA AGREGAR (MEJORADA)
    # ===========================================================
    def crear_interfaz_agregar(self, frame):
        ctk.CTkLabel(frame, text="Agregar nuevo producto", font=("Arial", 20),
                     text_color="white", bg_color="#1e3c72").pack(pady=10)

        form = ctk.CTkFrame(frame, fg_color="#1e3c72")
        form.pack(pady=20)

        labels = ["Nombre", "Precio", "Cantidad", "Departamento", "Almacén"]
        self.nuevos = {}

        for i, text in enumerate(labels):
            ctk.CTkLabel(form, text=text+":", text_color="white", bg_color="#1e3c72").grid(row=i, column=0, padx=5, pady=5)

            if text == "Almacén":
                entry = ctk.CTkComboBox(form, values=list(self.almacenes_dict.values()), width=300)
            elif text == "Precio" or text == "Cantidad":
                entry = ctk.CTkEntry(form, width=300, placeholder_text=f"Ingrese {text.lower()}")
            else:
                entry = ctk.CTkEntry(form, width=300)

            entry.grid(row=i, column=1, padx=5, pady=5)
            self.nuevos[text.lower()] = entry

        botones = ctk.CTkFrame(frame, fg_color="#1e3c72")
        botones.pack(pady=10)

        ctk.CTkButton(botones, text="Guardar", fg_color="#f8bb00",
                      text_color="black",
                      command=self.guardar_nuevo).pack(side="left", padx=10)

        ctk.CTkButton(botones, text="Cancelar", fg_color="#f8bb00",
                      text_color="black",
                      command=self.mostrar_vista_lista).pack(side="right", padx=10)

    def guardar_nuevo(self):
        try:
            nombre = self.nuevos["nombre"].get().strip()
            precio_str = self.nuevos["precio"].get().strip()
            cantidad_str = self.nuevos["cantidad"].get().strip()
            departamento = self.nuevos["departamento"].get().strip()
            almacen_nombre = self.nuevos["almacén"].get()

            # Validaciones
            if not nombre:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un nombre para el producto.")
                return
            if not precio_str:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un precio.")
                return
            if not cantidad_str:
                messagebox.showwarning("Campo vacío", "Por favor ingrese una cantidad.")
                return
            if not departamento:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un departamento.")
                return
            if not almacen_nombre:
                messagebox.showwarning("Campo vacío", "Por favor seleccione un almacén.")
                return

            precio = float(precio_str)
            cantidad = int(cantidad_str)
            almacen_id = next((i for i, n in self.almacenes_dict.items() if n == almacen_nombre), None)

            if almacen_id is None:
                messagebox.showerror("Error", "Almacén seleccionado no válido.")
                return

            # Obtener datos de auditoría
            timestamp, usuario_id = self.obtener_datos_auditoria()

            self.cursor.execute("""
                                INSERT INTO productos(nombre, precio, cantidad, departamento, almacen, fechamodificacion, usuario)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (nombre, precio, cantidad, departamento, almacen_id, timestamp, usuario_id))

            self.conn.commit()
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            self.mostrar_vista_lista()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para precio y cantidad.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===========================================================
    # VISTA EDITAR (NUEVA)
    # ===========================================================
    def crear_interfaz_editar(self, frame, registro):
        ctk.CTkLabel(frame, text="Editar producto", font=("Arial", 20),
                     text_color="white", bg_color="#1e3c72").pack(pady=10)

        form = ctk.CTkFrame(frame, fg_color="#1e3c72")
        form.pack(pady=20)

        # ID (no editable)
        ctk.CTkLabel(form, text="ID:", text_color="white", bg_color="#1e3c72").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(form, text=registro[0], text_color="white", bg_color="#1e3c72").grid(row=0, column=1, padx=5, pady=5)

        # Campos editables
        campos = [
            ("Nombre", registro[1]),
            ("Precio", registro[2]),
            ("Cantidad", registro[3]),
            ("Departamento", registro[4])
        ]

        self.editando = {}

        for i, (label, valor) in enumerate(campos, start=1):
            ctk.CTkLabel(form, text=label+":", text_color="white", bg_color="#1e3c72").grid(row=i, column=0, padx=5, pady=5)

            if label == "Precio" or label == "Cantidad":
                entry = ctk.CTkEntry(form, width=300)
            else:
                entry = ctk.CTkEntry(form, width=300)

            entry.insert(0, str(valor))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.editando[label.lower()] = entry

        # Almacén (combobox)
        ctk.CTkLabel(form, text="Almacén:", text_color="white", bg_color="#1e3c72").grid(row=5, column=0, padx=5, pady=5)
        self.editando_almacen = ctk.CTkComboBox(form, values=list(self.almacenes_dict.values()), width=300)
        self.editando_almacen.set(registro[5])  # Establecer el valor actual
        self.editando_almacen.grid(row=5, column=1, padx=5, pady=5)

        botones = ctk.CTkFrame(frame, fg_color="#1e3c72")
        botones.pack(pady=10)

        ctk.CTkButton(botones, text="Guardar cambios", fg_color="#f8bb00", text_color="black",
                      command=lambda: self.guardar_edicion(registro[0])).pack(side="left", padx=10)

        ctk.CTkButton(botones, text="Cancelar", fg_color="#f8bb00", text_color="black",
                      command=self.mostrar_vista_lista).pack(side="right", padx=10)

    def guardar_edicion(self, registro_id):
        try:
            nombre = self.editando["nombre"].get().strip()
            precio_str = self.editando["precio"].get().strip()
            cantidad_str = self.editando["cantidad"].get().strip()
            departamento = self.editando["departamento"].get().strip()
            almacen_nombre = self.editando_almacen.get()

            # Validaciones
            if not nombre:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un nombre para el producto.")
                return
            if not precio_str:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un precio.")
                return
            if not cantidad_str:
                messagebox.showwarning("Campo vacío", "Por favor ingrese una cantidad.")
                return
            if not departamento:
                messagebox.showwarning("Campo vacío", "Por favor ingrese un departamento.")
                return
            if not almacen_nombre:
                messagebox.showwarning("Campo vacío", "Por favor seleccione un almacén.")
                return

            precio = float(precio_str)
            cantidad = int(cantidad_str)
            almacen_id = next((i for i, n in self.almacenes_dict.items() if n == almacen_nombre), None)

            if almacen_id is None:
                messagebox.showerror("Error", "Almacén seleccionado no válido.")
                return

            # Obtener datos de auditoría para la actualización
            timestamp, usuario_id = self.obtener_datos_auditoria()

            self.cursor.execute("""
                                UPDATE productos
                                SET nombre=?, precio=?, cantidad=?, departamento=?, almacen=?, fechamodificacion=?, usuario=?
                                WHERE id=?
                                """, (nombre, precio, cantidad, departamento, almacen_id, timestamp, usuario_id, registro_id))
            self.conn.commit()

            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            self.mostrar_vista_lista()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para precio y cantidad.")
        except Exception as e:
            messagebox.showerror("Error", str(e))