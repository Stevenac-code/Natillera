# views/prestamo_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class PrestamoForm:
    def __init__(self, parent_frame, prestamo_model, ahorrador_model):
        self.frame = parent_frame
        self.prestamo_model = prestamo_model
        self.ahorrador_model = ahorrador_model
        
        # Variables del formulario principal
        self.ahorrador_var = tk.StringVar()
        self.monto_var = tk.StringVar()
        
        # Variables para pagos
        self.prestamo_seleccionado = None
        self.monto_pago_var = tk.StringVar()
        
        self.create_form()
    
    def create_form(self):
        # Notebook para pestañas
        notebook = ttk.Notebook(self.frame)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Tab para nuevo préstamo
        tab_nuevo = ttk.Frame(notebook)
        notebook.add(tab_nuevo, text='Nuevo Préstamo')
        self.create_nuevo_prestamo_form(tab_nuevo)
        
        # Tab para pagos
        tab_pagos = ttk.Frame(notebook)
        notebook.add(tab_pagos, text='Pagos')
        self.create_pagos_form(tab_pagos)
    
    def create_nuevo_prestamo_form(self, parent):
        # Título
        ttk.Label(parent, text="Registrar Préstamo", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Selector de Ahorrador
        ttk.Label(parent, text="Ahorrador:").grid(row=1, column=0, sticky='e', padx=5)
        self.ahorrador_combo = ttk.Combobox(parent, textvariable=self.ahorrador_var)
        self.ahorrador_combo.grid(row=1, column=1, sticky='w', padx=5)
        self.actualizar_lista_ahorradores()
        
        # Monto del préstamo
        ttk.Label(parent, text="Monto:").grid(row=2, column=0, sticky='e', padx=5)
        ttk.Entry(parent, textvariable=self.monto_var).grid(row=2, column=1, sticky='w', padx=5)
        
        # Tasa de interés (fija 3%)
        ttk.Label(parent, text="Tasa Interés:").grid(row=3, column=0, sticky='e', padx=5)
        ttk.Label(parent, text="3% mensual").grid(row=3, column=1, sticky='w', padx=5)
        
        # Botones
        ttk.Button(parent, text="Guardar", command=self.guardar_prestamo).grid(row=4, column=0, pady=20, padx=5)
        ttk.Button(parent, text="Limpiar", command=self.limpiar_form).grid(row=4, column=1, pady=20, padx=5)
    
    def create_pagos_form(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sección de búsqueda de préstamo
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Préstamo")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Nombre:").pack(side=tk.LEFT, padx=5)
        self.ahorrador_prestamo_var = tk.StringVar()
        self.ahorrador_prestamo_combo = ttk.Combobox(search_frame, 
                                                    textvariable=self.ahorrador_prestamo_var,
                                                    width=30)
        self.ahorrador_prestamo_combo.pack(side=tk.LEFT, padx=5)
        self.actualizar_lista_prestamos()
        
        ttk.Button(search_frame, text="Buscar", 
                command=self.buscar_prestamo).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Limpiar", 
                command=self.limpiar_busqueda).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Actualizar", 
              command=self.actualizar_lista_prestamos).pack(side=tk.LEFT, padx=5)
        
        # Sección de Información
        info_frame = ttk.LabelFrame(main_frame, text="Información del Préstamo")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="Ingrese un ID de préstamo...")
        self.info_label.pack(pady=5)
        
        # Sección de Pagos
        payment_frame = ttk.LabelFrame(main_frame, text="Registro de Pagos")
        payment_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para pago de interés
        interest_frame = ttk.Frame(payment_frame)
        interest_frame.pack(fill=tk.X, pady=5)
        self.interes_label = ttk.Label(interest_frame, text="Interés mensual: $0")
        self.interes_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(interest_frame, text="Pagar Interés", 
                command=self.registrar_pago_interes).pack(side=tk.LEFT, padx=5)
        
        # Frame para abonos
        abono_frame = ttk.Frame(payment_frame)
        abono_frame.pack(fill=tk.X, pady=5)
        ttk.Label(abono_frame, text="Monto abono:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(abono_frame, textvariable=self.monto_pago_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(abono_frame, text="Realizar Abono", 
                command=self.registrar_abono).pack(side=tk.LEFT, padx=5)
        
        # Historial de pagos
        history_frame = ttk.LabelFrame(main_frame, text="Historial de Pagos")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear Treeview para historial
        columns = ('Fecha', 'Tipo', 'Monto', 'Saldo Restante')
        self.tree_historial = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, width=100)
        
        self.tree_historial.pack(fill=tk.BOTH, expand=True)

    def actualizar_lista_prestamos(self):
        conn = self.prestamo_model.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, a.nombre, p.monto
            FROM prestamos p
            JOIN ahorradores a ON p.ahorrador_id = a.id
            WHERE p.estado = 'activo'
            ORDER BY a.nombre
        ''')
        prestamos = cursor.fetchall()
        conn.close()
        
        self.ahorrador_prestamo_combo['values'] = [
            f"{p[1]} - Préstamo: ${p[2]:,.2f} (ID: {p[0]})" 
            for p in prestamos
        ]
        self.prestamos_data = {
            f"{p[1]} - Préstamo: ${p[2]:,.2f} (ID: {p[0]})": p[0] 
        for p in prestamos
    }
    
    # Modificar también buscar_prestamo para actualizar el label de interés:
    def buscar_prestamo(self):
        try:
            seleccion = self.ahorrador_prestamo_var.get()
            if not seleccion:
                raise ValueError("Por favor seleccione un préstamo")
                
            prestamo_id = self.prestamos_data.get(seleccion)
            if not prestamo_id:
                raise ValueError("Préstamo no encontrado")
                
            self.prestamo_seleccionado = prestamo_id
            
            interes_pendiente = self.prestamo_model.calcular_interes_pendiente(prestamo_id)
            esta_al_dia = self.prestamo_model.esta_al_dia_intereses(prestamo_id)
            
            # Actualizar el label del interés
            self.interes_label.config(text=f"Interés mensual: ${interes_pendiente:,.2f}")
            
            info_text = f"Estado de intereses: " + ("Al día" if esta_al_dia else "Pendiente")
            self.info_label.config(text=info_text)
            
            self.cargar_historial_pagos(prestamo_id)
            
        except ValueError as e:
            messagebox.showwarning("Advertencia", str(e))
            self.limpiar_busqueda()

    def limpiar_busqueda(self):
        self.ahorrador_prestamo_var.set('')
        self.prestamo_seleccionado = None
        self.info_label.config(text="Seleccione un préstamo...")
        self.interes_label.config(text="Interés mensual: $0")
        self.tree_historial.delete(*self.tree_historial.get_children())
        self.monto_pago_var.set('')
        
    def cargar_historial_pagos(self, prestamo_id):
        pagos = self.prestamo_model.obtener_historial_pagos(prestamo_id)
        
        self.tree_historial.delete(*self.tree_historial.get_children())
        for pago in pagos:
            formatted_monto = f"${pago[2]:,.2f}"
            formatted_saldo = f"${pago[3]:,.2f}"
            self.tree_historial.insert('', 'end', values=(
                pago[0], pago[1].title(), formatted_monto, formatted_saldo
            ))
    
    def registrar_pago_interes(self):
        if not self.prestamo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un préstamo")
            return
        
        try:
            self.prestamo_model.registrar_pago_interes(self.prestamo_seleccionado)
            messagebox.showinfo("Éxito", "Pago de interés registrado correctamente")
            self.cargar_historial_pagos(self.prestamo_seleccionado)
            self.buscar_prestamo()  # Actualizar información
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def registrar_abono(self):
        if not self.prestamo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor busque un préstamo")
            return
        
        try:
            monto = float(self.monto_pago_var.get())
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a 0")
            
            self.prestamo_model.registrar_abono(self.prestamo_seleccionado, monto)
            messagebox.showinfo("Éxito", "Abono registrado correctamente")
            self.monto_pago_var.set('')
            self.cargar_historial_pagos(self.prestamo_seleccionado)
            self.buscar_prestamo()  # Actualizar información
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def actualizar_lista_ahorradores(self):
        ahorradores = self.ahorrador_model.listar_ahorradores()
        self.ahorrador_combo['values'] = [f"{a[1]} - {a[2]}" for a in ahorradores]
        self.ahorradores_data = {f"{a[1]} - {a[2]}": a[0] for a in ahorradores}
    
    def guardar_prestamo(self):
        try:
            if not all([self.ahorrador_var.get(), self.monto_var.get()]):
                raise ValueError("Todos los campos son obligatorios")
            
            ahorrador_id = self.ahorradores_data.get(self.ahorrador_var.get())
            if not ahorrador_id:
                raise ValueError("Seleccione un ahorrador válido")
            
            try:
                monto = float(self.monto_var.get())
                if monto <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("El monto debe ser un número positivo")
            
            # Quitamos el parámetro plazo_meses que ya no es necesario
            self.prestamo_model.crear_prestamo(
                ahorrador_id=ahorrador_id,
                monto=monto
            )
            
            messagebox.showinfo("Éxito", "Préstamo registrado correctamente")
            self.limpiar_form()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def limpiar_form(self):
        self.ahorrador_var.set('')
        self.monto_var.set('')

