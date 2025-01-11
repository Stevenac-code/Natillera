# views/ahorro_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class AhorroForm:
    def __init__(self, parent_frame, ahorro_model, ahorrador_model):
        self.frame = parent_frame
        self.ahorro_model = ahorro_model
        self.ahorrador_model = ahorrador_model
        
        # Variables para el formulario
        self.ahorrador_var = tk.StringVar()
        self.monto_var = tk.StringVar()
        self.tipo_var = tk.StringVar(value='ingreso')
        
        self.create_form()
        
    def create_form(self):
        # Título
        ttk.Label(self.frame, text="Registrar Ahorro", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Selector de Ahorrador
        ttk.Label(self.frame, text="Ahorrador:").grid(row=1, column=0, sticky='e', padx=5)
        self.ahorrador_combo = ttk.Combobox(self.frame, textvariable=self.ahorrador_var)
        self.ahorrador_combo.grid(row=1, column=1, sticky='w', padx=5)
        self.actualizar_lista_ahorradores()
        
        # Campo Monto
        ttk.Label(self.frame, text="Monto:").grid(row=2, column=0, sticky='e', padx=5)
        monto_entry = ttk.Entry(self.frame, textvariable=self.monto_var)
        monto_entry.grid(row=2, column=1, sticky='w', padx=5)
        
        # Tipo de Transacción
        ttk.Label(self.frame, text="Tipo:").grid(row=3, column=0, sticky='e', padx=5)
        ttk.Radiobutton(self.frame, text="Ingreso", variable=self.tipo_var, value='ingreso').grid(row=3, column=1, sticky='w', padx=5)
        ttk.Radiobutton(self.frame, text="Retiro", variable=self.tipo_var, value='retiro').grid(row=4, column=1, sticky='w', padx=5)
        
        # Botones
        ttk.Button(self.frame, text="Guardar", command=self.guardar_ahorro).grid(row=5, column=0, pady=20, padx=5)
        ttk.Button(self.frame, text="Limpiar", command=self.limpiar_form).grid(row=5, column=1, pady=20, padx=5)

    def actualizar_lista_ahorradores(self):
        ahorradores = self.ahorrador_model.listar_ahorradores()
        self.ahorrador_combo['values'] = [f"{a[1]} - {a[2]}" for a in ahorradores]  # nombre - documento
        self.ahorradores_data = {f"{a[1]} - {a[2]}": a[0] for a in ahorradores}  # para obtener el ID
    
    def guardar_ahorro(self):
        try:
            # Validar campos
            if not self.ahorrador_var.get() or not self.monto_var.get():
                raise ValueError("Todos los campos son obligatorios")
            
            # Obtener ID del ahorrador
            ahorrador_id = self.ahorradores_data.get(self.ahorrador_var.get())
            if not ahorrador_id:
                raise ValueError("Seleccione un ahorrador válido")
            
            # Convertir monto a float
            try:
                monto = float(self.monto_var.get())
                if monto <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("El monto debe ser un número positivo")
            
            # Guardar el ahorro
            self.ahorro_model.registrar_ahorro(
                ahorrador_id=ahorrador_id,
                monto=monto,
                tipo=self.tipo_var.get()
            )
            
            messagebox.showinfo("Éxito", "Ahorro registrado correctamente")
            self.limpiar_form()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def limpiar_form(self):
        self.ahorrador_var.set('')
        self.monto_var.set('')
        self.tipo_var.set('ingreso')

class AhorrosList:
    def __init__(self, parent_frame, ahorro_model, ahorrador_model):
        self.frame = parent_frame
        self.ahorro_model = ahorro_model
        self.ahorrador_model = ahorrador_model
        
        self.create_list()
        
    def create_list(self):
        # Frame para el filtro
        filter_frame = ttk.Frame(self.frame)
        filter_frame.grid(row=0, column=0, pady=10)
        
        ttk.Label(filter_frame, text="Ahorrador:").pack(side=tk.LEFT, padx=5)
        self.ahorrador_filter = ttk.Combobox(filter_frame)
        self.ahorrador_filter.pack(side=tk.LEFT, padx=5)
        self.actualizar_lista_ahorradores()
        
        ttk.Button(filter_frame, text="Filtrar", command=self.actualizar_tabla).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Limpiar", command=self.limpiar_filtro).pack(side=tk.LEFT, padx=5)
        
        # Crear tabla
        columns = ('ID', 'Fecha', 'Ahorrador', 'Monto', 'Tipo')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.grid(row=1, column=0, sticky='nsew')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar datos
        self.actualizar_tabla()
    
    def actualizar_lista_ahorradores(self):
        ahorradores = self.ahorrador_model.listar_ahorradores()
        self.ahorrador_filter['values'] = ['Todos'] + [f"{a[1]} - {a[2]}" for a in ahorradores]
        self.ahorradores_data = {f"{a[1]} - {a[2]}": a[0] for a in ahorradores}
    
    def actualizar_tabla(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener ahorrador seleccionado
        selected_ahorrador = self.ahorrador_filter.get()
        ahorrador_id = self.ahorradores_data.get(selected_ahorrador) if selected_ahorrador != 'Todos' else None
        
        # Obtener y mostrar ahorros
        if ahorrador_id:
            ahorros = self.ahorro_model.obtener_ahorros_ahorrador(ahorrador_id)
        else:
            # Aquí necesitarías implementar un método para obtener todos los ahorros
            # Por ahora mostraremos un mensaje
            messagebox.showinfo("Info", "Función de mostrar todos los ahorros pendiente")
            return
        
        for ahorro in ahorros:
            ahorrador = self.ahorrador_model.obtener_ahorrador(ahorro[1])
            self.tree.insert('', tk.END, values=(
                ahorro[0],  # ID
                ahorro[3],  # Fecha
                ahorrador[1],  # Nombre del ahorrador
                f"${ahorro[2]:,.2f}",  # Monto formateado
                ahorro[4]   # Tipo
            ))
    
    def limpiar_filtro(self):
        self.ahorrador_filter.set('Todos')
        self.actualizar_tabla()