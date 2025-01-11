# views/rifa_view.py
import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox


class RifaForm:
    def __init__(self, parent_frame, rifa_model, ahorrador_model):
        self.frame = parent_frame
        self.rifa_model = rifa_model
        self.ahorrador_model = ahorrador_model
        
        # Variables para el formulario
        self.ahorrador_var = tk.StringVar()
        
        self.create_form()
    
    def create_form(self):
        notebook = ttk.Notebook(self.frame)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Tab para registro
        tab_registro = ttk.Frame(notebook)
        notebook.add(tab_registro, text='Registrar Pago')
        self.create_registro_form(tab_registro)
        
        # Tab para historial
        tab_historial = ttk.Frame(notebook)
        notebook.add(tab_historial, text='Historial General')
        self.create_historial_form(tab_historial)
        
        # Nueva tab para números
        tab_numeros = ttk.Frame(notebook)
        notebook.add(tab_numeros, text='Números Ahorradores')
        self.create_numeros_form(tab_numeros)

        # Nueva tab para fechas de rifa
        tab_fechas = ttk.Frame(notebook)
        notebook.add(tab_fechas, text='Fechas Rifa')
        self.create_fechas_form(tab_fechas)
        
    def create_registro_form(self, parent):
        # Título
        ttk.Label(parent, text="Registrar Pago de Rifa", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Frame para selección de ahorrador
        selection_frame = ttk.LabelFrame(parent, text="Seleccionar Ahorrador")
        selection_frame.pack(padx=10, pady=5, fill='x')
        
        # Selector de Ahorrador
        ttk.Label(selection_frame, text="Ahorrador:").pack(side=tk.LEFT, padx=5)
        self.ahorrador_combo = ttk.Combobox(selection_frame, 
                                          textvariable=self.ahorrador_var,
                                          width=40)
        self.ahorrador_combo.pack(side=tk.LEFT, padx=5)
        self.actualizar_lista_ahorradores()
        
        # Frame para botones
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)
        
        # Mostrar monto fijo
        ttk.Label(button_frame, 
                 text="Monto a pagar: $10,000",
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Botón de registro
        ttk.Button(button_frame, 
                  text="Registrar Pago",
                  command=self.registrar_pago).pack(pady=5)
        
        # Frame para historial individual
        history_frame = ttk.LabelFrame(parent, text="Historial de Pagos del Ahorrador")
        history_frame.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Tabla de historial individual
        columns = ('ID', 'Ahorrador', 'Fecha', 'Monto')
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100 if col != 'Ahorrador' else 200
            self.tree.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(history_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(0, weight=1)
        
        # Bind para actualizar historial al seleccionar ahorrador
        self.ahorrador_combo.bind('<<ComboboxSelected>>', self.actualizar_historial)
    
    def create_historial_form(self, parent):
        # Frame para filtros
        filter_frame = ttk.LabelFrame(parent, text="Filtros")
        filter_frame.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(filter_frame, text="Buscar por nombre:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Buscar", 
                  command=self.buscar_pagos).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Limpiar", 
                  command=self.limpiar_busqueda).pack(side=tk.LEFT, padx=5)
        
        # Frame para la tabla
        table_frame = ttk.Frame(parent)
        table_frame.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Tabla de historial general
        columns = ('ID', 'Ahorrador', 'Fecha', 'Monto')
        self.tree_general = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree_general.heading(col, text=col)
            width = 100 if col != 'Ahorrador' else 200
            self.tree_general.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_general.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_general.xview)
        self.tree_general.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree_general.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self.cargar_todos_pagos()
    
    def actualizar_lista_ahorradores(self):
        ahorradores = self.ahorrador_model.listar_ahorradores()
        self.ahorrador_combo['values'] = [f"{a[1]} - {a[2]}" for a in ahorradores]
        self.ahorradores_data = {f"{a[1]} - {a[2]}": a[0] for a in ahorradores}
    
    def registrar_pago(self):
        try:
            if not self.ahorrador_var.get():
                raise ValueError("Debe seleccionar un ahorrador")
            
            ahorrador_id = self.ahorradores_data.get(self.ahorrador_var.get())
            if not ahorrador_id:
                raise ValueError("Ahorrador no válido")
            
            self.rifa_model.registrar_pago(ahorrador_id)
            messagebox.showinfo("Éxito", "Pago registrado correctamente")
            
            # Actualizar historial
            self.actualizar_historial(None)
            self.cargar_todos_pagos()  # Actualizar también el historial general
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def actualizar_historial(self, event):
        try:
            ahorrador_id = self.ahorradores_data.get(self.ahorrador_var.get())
            if not ahorrador_id:
                return
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Cargar pagos
            pagos = self.rifa_model.obtener_pagos_ahorrador(ahorrador_id)
            for pago in pagos:
                self.tree.insert('', 'end', values=(
                    pago[0],  # ID
                    pago[1],  # nombre del ahorrador
                    pago[2],  # fecha
                    f"${pago[3]:,.2f}"  # monto formateado
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def cargar_todos_pagos(self):
        try:
            # Limpiar tabla
            for item in self.tree_general.get_children():
                self.tree_general.delete(item)
            
            # Cargar todos los pagos
            pagos = self.rifa_model.obtener_todos_pagos()
            for pago in pagos:
                self.tree_general.insert('', 'end', values=(
                    pago[0],  # ID
                    pago[1],  # nombre del ahorrador
                    pago[2],  # fecha
                    f"${pago[3]:,.2f}"  # monto formateado
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def buscar_pagos(self):
        try:
            # Limpiar tabla
            for item in self.tree_general.get_children():
                self.tree_general.delete(item)
            
            # Buscar pagos
            pagos = self.rifa_model.buscar_pagos(self.search_var.get())
            for pago in pagos:
                self.tree_general.insert('', 'end', values=(
                    pago[0],  # ID
                    pago[1],  # nombre del ahorrador
                    pago[2],  # fecha
                    f"${pago[3]:,.2f}"  # monto formateado
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_numeros_form(self, parent):
        # Frame para botón de repartir
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=10, padx=10, fill='x')
        
        ttk.Button(button_frame, 
                text="Repartir Números", 
                command=self.repartir_numeros).pack(side=tk.LEFT, padx=5)
        
        # Frame para la tabla
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear tabla
        columns = ('Ahorrador', 'Números')
        self.tree_numeros = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configurar columnas
        self.tree_numeros.heading('Ahorrador', text='Ahorrador')
        self.tree_numeros.heading('Números', text='Números')
        
        self.tree_numeros.column('Ahorrador', width=200)
        self.tree_numeros.column('Números', width=300)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_numeros.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_numeros.xview)
        self.tree_numeros.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree_numeros.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Cargar números actuales
        self.cargar_numeros()

    def repartir_numeros(self):
        try:
            if messagebox.askyesno("Confirmar", 
                                "¿Está seguro de querer repartir nuevamente los números? " +
                                "Esto eliminará la asignación actual."):
                self.rifa_model.repartir_numeros()
                self.cargar_numeros()
                messagebox.showinfo("Éxito", "Números repartidos correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def cargar_numeros(self):
        try:
            # Limpiar tabla
            for item in self.tree_numeros.get_children():
                self.tree_numeros.delete(item)
            
            # Obtener y mostrar números
            numeros = self.rifa_model.obtener_numeros_asignados()
            
            natillera_style = ('natillera_row',)
            for nombre, nums in numeros:
                # Si es una fila de NATILLERA, usar el estilo especial
                tags = natillera_style if nombre == 'NATILLERA' else ()
                
                # Separar los números por " - "
                num_list = [f"{str(n).zfill(2)}" for n in nums.split(",")]
                num_str = " - ".join(num_list)
                
                self.tree_numeros.insert('', 'end', values=(nombre, num_str), tags=tags)
            
            # Configurar el estilo para las filas de NATILLERA
            self.tree_numeros.tag_configure('natillera_row', background='#fff0f5')  # Rosa muy claro
            
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def create_fechas_form(self, parent):
        # Frame principal
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame superior para registro
        registro_frame = ttk.LabelFrame(main_frame, text="Registrar Nueva Fecha")
        registro_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos de registro
        input_frame = ttk.Frame(registro_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # Campo fecha (reemplazar el Entry por DateEntry)
        ttk.Label(input_frame, text="Fecha:").grid(row=0, column=0, padx=5)
        self.fecha_entry = DateEntry(input_frame, width=12, 
                                background='white',
                                foreground='black',
                                borderwidth=2,
                                locale='es_ES',  # Para que muestre los meses en español
                                date_pattern='yyyy-mm-dd')  # Formato de fecha
        self.fecha_entry.grid(row=0, column=1, padx=5)
        
        # Campo valor
        ttk.Label(input_frame, text="Valor Premio:").grid(row=1, column=0, padx=5)
        self.valor_var = tk.StringVar()
        valor_entry = ttk.Entry(input_frame, textvariable=self.valor_var)
        valor_entry.grid(row=1, column=1, padx=5)
        
        # Botón registrar
        ttk.Button(input_frame, text="Registrar Fecha", 
                command=self.registrar_fecha).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Frame para la tabla de fechas
        table_frame = ttk.LabelFrame(main_frame, text="Calendario de Rifas")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabla de fechas
        columns = ('ID', 'Fecha', 'Valor Premio', 'Estado', 'Ganador', 'Número Ganador')
        self.tree_fechas = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configurar columnas
        widths = {'ID': 50, 'Fecha': 100, 'Valor Premio': 100, 
                'Estado': 100, 'Ganador': 150, 'Número Ganador': 100}
        for col in columns:
            self.tree_fechas.heading(col, text=col)
            self.tree_fechas.column(col, width=widths.get(col, 100))
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_fechas.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_fechas.xview)
        self.tree_fechas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree_fechas.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Añadir botón para registrar ganador
        button_frame = ttk.Frame(table_frame)
        button_frame.grid(row=2, column=0, pady=5)
        
        ttk.Button(button_frame, text="Registrar Ganador", 
                command=self.mostrar_dialogo_ganador).pack(pady=5)
        
        # Cargar fechas existentes
        self.cargar_fechas()

    def registrar_fecha(self):
        try:
            fecha = self.fecha_entry.get_date().strftime('%Y-%m-%d')
            valor = float(self.valor_var.get())
            
            if not valor:
                raise ValueError("El valor del premio es obligatorio")
            
            self.rifa_model.registrar_fecha_rifa(fecha, valor)
            messagebox.showinfo("Éxito", "Fecha de rifa registrada correctamente")
            
            # Limpiar campos y actualizar tabla
            self.fecha_entry.set_date(None)  # Limpiar fecha
            self.valor_var.set('')
            self.cargar_fechas()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar fecha: {str(e)}")

    def cargar_fechas(self):
        try:
            # Limpiar tabla
            for item in self.tree_fechas.get_children():
                self.tree_fechas.delete(item)
            
            # Cargar fechas
            fechas = self.rifa_model.obtener_fechas_rifa()
            for fecha in fechas:
                self.tree_fechas.insert('', 'end', values=(
                    fecha[0],  # ID
                    fecha[1],  # Fecha
                    f"${fecha[2]:,.2f}",  # Valor
                    "Realizada" if fecha[3] else "Pendiente",  # Estado
                    fecha[4] or "No asignado",  # Ganador
                    fecha[5] or "N/A"  # Número ganador
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar fechas: {str(e)}")


    def mostrar_dialogo_ganador(self):
        # Verificar si hay una fecha seleccionada
        selected = self.tree_fechas.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una fecha de rifa")
            return
        
        item = self.tree_fechas.item(selected[0])
        fecha_id = item['values'][0]
        estado = item['values'][3]
        
        if estado == "Realizada":
            messagebox.showwarning("Advertencia", "Esta rifa ya tiene un ganador registrado")
            return
        
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self.frame)
        dialog.title("Registrar Ganador")
        dialog.geometry("400x200")
        
        # Asegurar que la ventana sea modal
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Frame para el formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selector de Ahorrador
        ttk.Label(form_frame, text="Ganador:").grid(row=0, column=0, padx=5, pady=5)
        ganador_var = tk.StringVar()
        ganador_combo = ttk.Combobox(form_frame, textvariable=ganador_var, width=30)
        ganador_combo['values'] = [f"{a[1]} - {a[2]}" for a in self.ahorrador_model.listar_ahorradores()]
        ganador_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Campo para número ganador
        ttk.Label(form_frame, text="Número Ganador:").grid(row=1, column=0, padx=5, pady=5)
        numero_var = tk.StringVar()
        numero_entry = ttk.Entry(form_frame, textvariable=numero_var, width=10)
        numero_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        def guardar_ganador():
            try:
                # Obtener ahorrador_id
                ganador = ganador_var.get()
                if not ganador:
                    raise ValueError("Debe seleccionar un ganador")
                
                ahorrador_id = self.ahorradores_data.get(ganador)
                if not ahorrador_id:
                    raise ValueError("Ganador no válido")
                
                # Validar número
                numero = numero_var.get()
                if not numero.isdigit() or not (0 <= int(numero) <= 99):
                    raise ValueError("El número debe estar entre 00 y 99")
                
                # Registrar ganador
                self.rifa_model.registrar_ganador(fecha_id, ahorrador_id, numero)
                messagebox.showinfo("Éxito", "Ganador registrado correctamente")
                
                # Cerrar diálogo y actualizar tabla
                dialog.destroy()
                self.cargar_fechas()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", 
                command=guardar_ganador).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Centrar la ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Esperar hasta que se cierre la ventana
        self.frame.wait_window(dialog)
    
    def limpiar_busqueda(self):
        self.search_var.set('')
        self.cargar_todos_pagos()