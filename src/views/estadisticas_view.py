# views/estadisticas_view.py
import tkinter as tk
from tkinter import ttk

class EstadisticasView:
    def __init__(self, parent_frame, db):
        self.frame = parent_frame
        self.db = db
        self.search_vars = {}
        self.create_view()
    
    def create_view(self):
        notebook = ttk.Notebook(self.frame)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Pestaña de Estadísticas Generales
        tab_general = ttk.Frame(notebook)
        notebook.add(tab_general, text='Estadísticas Generales')
        self.create_general_stats(tab_general)
        
        # Pestaña de Ahorradores
        tab_ahorradores = ttk.Frame(notebook)
        notebook.add(tab_ahorradores, text='Ahorradores')
        self.create_ahorradores_view(tab_ahorradores)
        
        # Pestaña de Ahorros
        tab_ahorros = ttk.Frame(notebook)
        notebook.add(tab_ahorros, text='Ahorros')
        self.create_ahorros_view(tab_ahorros)
        
        # Pestaña de Préstamos
        tab_prestamos = ttk.Frame(notebook)
        notebook.add(tab_prestamos, text='Préstamos')
        self.create_prestamos_view(tab_prestamos)

        # Pestaña de Préstamos Activos
        tab_prestamos_activos = ttk.Frame(notebook)
        notebook.add(tab_prestamos_activos, text='Préstamos Activos')
        self.create_prestamos_activos_view(tab_prestamos_activos)
    
    def create_search_frame(self, parent, table_name):
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar por nombre:").pack(side=tk.LEFT, padx=5)
        self.search_vars[table_name] = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_vars[table_name])
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Buscar", 
                  command=lambda: self.search_in_table(table_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Limpiar", 
                  command=lambda: self.clear_search(table_name)).pack(side=tk.LEFT, padx=5)
        
        return search_frame

    def create_ahorradores_view(self, parent):
        search_frame = self.create_search_frame(parent, 'ahorradores')
        
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        columns = ('ID', 'Nombre', 'Documento', 'Teléfono', 'Email', 'Fecha Registro')
        self.tree_ahorradores = self.create_treeview(table_frame, columns)
        self.load_ahorradores_data()

    def create_ahorros_view(self, parent):
        search_frame = self.create_search_frame(parent, 'ahorros')
        
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        columns = ('ID', 'Nombre', 'Monto', 'Fecha', 'Tipo')
        self.tree_ahorros = self.create_treeview(table_frame, columns)
        self.load_ahorros_data()

    def create_prestamos_view(self, parent):
        search_frame = self.create_search_frame(parent, 'prestamos')
        
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        columns = ('ID', 'Nombre', 'Monto', 'Tasa Interés', 'Fecha Préstamo', 'Estado')
        self.tree_prestamos = self.create_treeview(table_frame, columns)
        self.load_prestamos_data()

    def create_prestamos_activos_view(self, parent):
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        columns = ('ID', 'Nombre', 'Monto Original', 'Saldo Actual', 'Fecha Préstamo')
        self.tree_prestamos_activos = self.create_treeview(table_frame, columns)
        self.load_prestamos_activos_data()

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            width = 100
            if col in ['Nombre', 'Email']:
                width = 200
            elif col in ['Fecha Préstamo']:
                width = 150
            tree.column(col, width=width)
        
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        return tree

    def load_ahorradores_data(self, search_term=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, nombre, documento, telefono, email, fecha_registro 
            FROM ahorradores
        """
        params = []
        
        if search_term:
            query += " WHERE nombre LIKE ?"
            params = [f"%{search_term}%"]
            
        query += " ORDER BY nombre"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        self.tree_ahorradores.delete(*self.tree_ahorradores.get_children())
        for row in rows:
            self.tree_ahorradores.insert('', 'end', values=row)
        
        conn.close()

    def load_ahorros_data(self, search_term=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.id, ah.nombre, a.monto, a.fecha, a.tipo
            FROM ahorros a
            JOIN ahorradores ah ON a.ahorrador_id = ah.id
        """
        params = []
        
        if search_term:
            query += " WHERE ah.nombre LIKE ?"
            params = [f"%{search_term}%"]
            
        query += " ORDER BY a.fecha DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        self.tree_ahorros.delete(*self.tree_ahorros.get_children())
        for row in rows:
            formatted_row = list(row)
            formatted_row[2] = f"${formatted_row[2]:,.2f}"
            self.tree_ahorros.insert('', 'end', values=formatted_row)
        
        conn.close()

    def load_prestamos_data(self, search_term=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT p.id, ah.nombre, p.monto, p.tasa_interes, 
                   p.fecha_prestamo, p.estado
            FROM prestamos p
            JOIN ahorradores ah ON p.ahorrador_id = ah.id
        """
        params = []
        
        if search_term:
            query += " WHERE ah.nombre LIKE ?"
            params = [f"%{search_term}%"]
            
        query += " ORDER BY p.fecha_prestamo DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        self.tree_prestamos.delete(*self.tree_prestamos.get_children())
        for row in rows:
            formatted_row = list(row)
            formatted_row[2] = f"${formatted_row[2]:,.2f}"
            formatted_row[3] = f"{formatted_row[3]}%"
            self.tree_prestamos.insert('', 'end', values=formatted_row)
        
        conn.close()

    def load_prestamos_activos_data(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT p.id, ah.nombre, p.monto, p.saldo_actual, p.fecha_prestamo
            FROM prestamos p
            JOIN ahorradores ah ON p.ahorrador_id = ah.id
            WHERE p.estado = 'activo'
            ORDER BY ah.nombre
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        self.tree_prestamos_activos.delete(*self.tree_prestamos_activos.get_children())
        for row in rows:
            formatted_row = list(row)
            formatted_row[2] = f"${formatted_row[2]:,.2f}"  # Monto original
            formatted_row[3] = f"${formatted_row[3]:,.2f}" if formatted_row[3] else "N/A"  # Saldo actual
            self.tree_prestamos_activos.insert('', 'end', values=formatted_row)
        
        conn.close()

    def search_in_table(self, table_name):
        search_term = self.search_vars[table_name].get()
        if table_name == 'ahorradores':
            self.load_ahorradores_data(search_term)
        elif table_name == 'ahorros':
            self.load_ahorros_data(search_term)
        elif table_name == 'prestamos':
            self.load_prestamos_data(search_term)

    def clear_search(self, table_name):
        self.search_vars[table_name].set('')
        self.search_in_table(table_name)

    def create_general_stats(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Resumen General", padding="10")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ahorradores")
        total_ahorradores = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) as ingresos,
                SUM(CASE WHEN tipo = 'retiro' THEN monto ELSE 0 END) as retiros,
                COUNT(*) as total_transacciones
            FROM ahorros
        """)
        ahorros_stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                estado,
                COUNT(*) as cantidad,
                SUM(monto) as total
            FROM prestamos 
            GROUP BY estado
        """)
        prestamos_stats = cursor.fetchall()
        
        conn.close()
        
        ttk.Label(stats_frame, text=f"Total de Ahorradores: {total_ahorradores}",
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
        
        ttk.Label(stats_frame, text="\nEstadísticas de Ahorros:",
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
        if ahorros_stats[0]:
            ttk.Label(stats_frame, 
                     text=f"Total Ingresos: ${ahorros_stats[0]:,.2f}").pack(anchor='w')
        if ahorros_stats[1]:
            ttk.Label(stats_frame, 
                     text=f"Total Retiros: ${ahorros_stats[1]:,.2f}").pack(anchor='w')
        ttk.Label(stats_frame, 
                 text=f"Total Transacciones: {ahorros_stats[2]}").pack(anchor='w')
        
        if prestamos_stats:
            ttk.Label(stats_frame, text="\nEstadísticas de Préstamos:",
                     font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
            for estado, cantidad, total in prestamos_stats:
                ttk.Label(stats_frame,
                         text=f"{estado.title()}: {cantidad} préstamos, " +
                              f"Total: ${total:,.2f}").pack(anchor='w')