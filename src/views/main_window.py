# views/main_window.py
import os
import sys
import tkinter as tk
from datetime import datetime
from ttkthemes import ThemedTk
from tkinter import ttk, messagebox

# Configuración de paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

from src.models.rifa import Rifa
from src.models.ahorro import Ahorro
from src.models.database import Database
from src.models.prestamo import Prestamo
from src.models.ahorrador import Ahorrador



class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Natillera Johana Franco 👩🏻🦒")
        self.root.state('zoomed')
        
        # Cambiar el tamaño de la ventana a uno más grande
        self.root.geometry("1200x700")  # Aumentamos el tamaño
        
        # Asegurar que la ventana se pueda redimensionar
        self.root.resizable(True, True)
        
        # Configurar el peso de las filas y columnas para expansión
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Colores del tema
        self.colors = {
            'background': '#FFE4E1',   # Rosa pastel (Misty Rose)
            'primary': '#DB7093',      # Rosa más oscuro para botones
            'secondary': '#FFB6C1',    # Rosa claro para hover
            'success': '#98FB98',      # Verde suave
            'warning': '#FFE4B5',      # Melocotón para advertencias
            'danger': '#FFB6C1',       # Rosa para errores
            'light': '#FFF0F5',        # Rosa muy claro para fondos
            'dark': '#000000',         # Negro para texto
            'border': '#FFB6C1'        # Rosa claro para bordes
        }
        
        # Establecer tema y estilos
        self.style = ttk.Style()
        
        # Configurar color de fondo para la ventana principal
        self.root.configure(bg=self.colors['background'])
        
        # Estilo para etiquetas de título
        self.style.configure(
            "Title.TLabel",
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['dark'],
            background=self.colors['background'],
            padding=10
        )
        
        # Estilo para subtítulos
        self.style.configure(
            "Subtitle.TLabel",
            font=('Segoe UI', 16),
            foreground=self.colors['dark'],
            background=self.colors['background'],
            padding=5
        )
        
        # Estilo para encabezados
        self.style.configure(
            "Header.TLabel",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colors['dark'],
            background=self.colors['background']
        )
        
        # Estilo para información
        self.style.configure(
            "Info.TLabel",
            font=('Segoe UI', 10),
            foreground=self.colors['dark'],
            background=self.colors['background']
        )
        
        # Estilo para botones de acción
        self.style.configure(
            "Action.TButton",
            font=('Segoe UI', 10, 'bold'),
            padding=10,
            background=self.colors['primary'],
            foreground=self.colors['dark']  # Texto negro
        )
        
        self.style.map(
            "Action.TButton",
            background=[('active', self.colors['secondary'])]
        )
        
        # Estilo para tablas
        self.style.configure(
            "Treeview",
            font=('Segoe UI', 10),
            rowheight=25,
            background=self.colors['light'],
            fieldbackground=self.colors['light'],
            foreground=self.colors['dark'],
            borderwidth=0
        )
        
        # Estilo para encabezados de tabla
        self.style.configure(
            "Treeview.Heading",
            font=('Segoe UI', 10, 'bold'),
            background=self.colors['secondary'],  # Fondo rosa claro
            foreground=self.colors['dark'],      # Texto negro
            padding=5
        )
        
        self.style.map(
            "Treeview",
            background=[('selected', self.colors['secondary'])],
            foreground=[('selected', self.colors['dark'])]
        )
        
        # Estilo para marcos
        self.style.configure(
            "Card.TFrame",
            background=self.colors['light'],
            relief='solid',
            borderwidth=1
        )
        
        # Estilo para entradas de texto
        self.style.configure(
            "TEntry",
            padding=5,
            relief="solid",
            borderwidth=1,
            foreground=self.colors['dark']
        )
        
        # Estilo para Combobox
        self.style.configure(
            "TCombobox",
            padding=5,
            relief="solid",
            borderwidth=1
        )
        
        # Estilo para marcos con etiqueta
        self.style.configure(
            "TLabelframe",
            background=self.colors['light'],
            relief="solid",
            borderwidth=1,
            padding=10
        )
        
        self.style.configure(
            "TLabelframe.Label",
            font=('Segoe UI', 10, 'bold'),
            foreground=self.colors['dark'],
            background=self.colors['light']
        )
        
        # Configuración para frame principal
        self.style.configure(
            "Main.TFrame",
            background=self.colors['background']
        )
        
        # Inicializar modelos
        self.db = Database()
        self.ahorrador_model = Ahorrador(self.db)
        self.ahorro_model = Ahorro(self.db)
        self.prestamo_model = Prestamo(self.db)
        self.rifa_model = Rifa(self.db)
        
        # Crear interfaz
        self.setup_ui()
        
    
    def setup_ui(self):
        # Frame principal con padding
        self.main_container = ttk.Frame(self.root, padding="20", style="Main.TFrame")
        self.main_container.grid(row=0, column=0, sticky='nsew')
        
        # Configurar pesos para expansión
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Barra superior
        self.setup_top_bar()
        
        # Frame de contenido principal
        self.content_frame = ttk.Frame(self.main_container, padding="10")
        self.content_frame.grid(row=1, column=0, sticky='nsew')
        
        # Configurar pesos para el content_frame
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(2, weight=1)
        
        # Crear menú
        self.create_menu()

        # Menú principal
        self.create_menu()
        
        # Mostrar estadpisticas inicialmente
        self.show_estadisticas()
    

    def setup_top_bar(self):
        
        
        # Diccionario de meses en español
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        
        top_frame = ttk.Frame(self.main_container, style="Main.TFrame")  # Aplicamos el estilo rosa
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Título
        ttk.Label(top_frame, text="Sistema de Natillera  Johana Franco 👩🏻🦒", 
                style="Title.TLabel").pack(side=tk.LEFT)
        
        # Fecha actual en español
        date_frame = ttk.Frame(top_frame, style="Main.TFrame")  # También aplicamos el estilo rosa
        date_frame.pack(side=tk.RIGHT)
        
        fecha_actual = datetime.now()
        fecha_texto = f"{fecha_actual.day} de {meses[fecha_actual.month]} de {fecha_actual.year}"
        
        ttk.Label(date_frame, 
                text=fecha_texto,
                style="Info.TLabel").pack()
    
    def create_menu(self):
        # Frame para el menú lateral con nuevo estilo
        menu_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding="20")
        menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.N, tk.S), padx=10, pady=10)
        
        buttons = [
            ("Estadísticas", self.show_estadisticas),
            ("Registrar Ahorrador", self.show_ahorradores_list),
            ("Registrar Ahorro", self.show_ahorro_form),
            ("Registrar Préstamo", self.show_prestamo_form),
            ("Rifas", self.show_rifa_form),
            ("Generar Reportes", self.show_reportes)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(menu_frame, 
                            text=text,
                            command=command,
                            style="Action.TButton",
                            width=20)
            btn.pack(pady=5, padx=5, fill=tk.X)
        
        # Separador vertical con nuevo estilo
        separator = ttk.Separator(self.content_frame, orient=tk.VERTICAL)
        separator.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10)
        
        # Frame para el contenido principal
        self.main_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding="20")
        self.main_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        self.content_frame.columnconfigure(2, weight=1)
    

    def clear_main_frame(self):
        """Limpia todos los widgets del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    

    def show_ahorradores_list(self):
        self.clear_main_frame()
    
        # Frame principal con padding y scroll
        main_container = ttk.Frame(self.main_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_container, text="Lista de Ahorradores", 
                style="Subtitle.TLabel").pack(pady=(0, 20))
        
        # Frame para la tabla con peso para expansión
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabla
        columns = ('ID', 'Nombre', 'Documento', 'Teléfono', 'Email')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')  # Quitamos height fijo
            
        # Configurar columnas
        tree.column('ID', width=50, anchor='center')
        tree.column('Nombre', width=200, anchor='w')
        tree.column('Documento', width=100, anchor='center')
        tree.column('Teléfono', width=100, anchor='center')
        tree.column('Email', width=200, anchor='w')
        
        for col in columns:
            tree.heading(col, text=col, anchor='center')
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid para la tabla y scrollbars
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configurar expansión del table_frame
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Obtener y mostrar ahorradores
        ahorradores = self.ahorrador_model.listar_ahorradores()
        for ahorrador in ahorradores:
            tree.insert('', tk.END, values=ahorrador)
        
        # Frame para botones en la parte inferior
        # Configurar columnas para que usen el espacio disponible
        total_width = table_frame.winfo_width()
        tree.column('ID', width=int(total_width * 0.1))
        tree.column('Nombre', width=int(total_width * 0.3))
        tree.column('Documento', width=int(total_width * 0.2))
        tree.column('Teléfono', width=int(total_width * 0.2))
        tree.column('Email', width=int(total_width * 0.2))
        
        # Botones al final
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=20, fill=tk.X)
        
        ttk.Button(button_frame, text="Nuevo Ahorrador", 
                command=self.show_ahorrador_form,
                style="Action.TButton").pack(pady=5)

    
    def show_ahorrador_form(self):
        self.clear_main_frame()
        
        # Título
        ttk.Label(self.main_frame, text="Nuevo Ahorrador", 
                 style="Subtitle.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame para el formulario
        form_frame = ttk.Frame(self.main_frame, padding="20")
        form_frame.grid(row=1, column=0)
        
        # Variables para el formulario
        nombre_var = tk.StringVar()
        documento_var = tk.StringVar()
        telefono_var = tk.StringVar()
        email_var = tk.StringVar()
        
        # Campo Nombre
        ttk.Label(form_frame, text="Nombre Apellido:", style="Info.TLabel").grid(row=0, column=0, pady=5, sticky='e')
        nombre_entry = ttk.Entry(form_frame, textvariable=nombre_var, width=30, style='TEntry')
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Campo Documento
        ttk.Label(form_frame, text="Documento:", style="Info.TLabel").grid(row=1, column=0, pady=5, sticky='e')
        documento_entry = ttk.Entry(form_frame, textvariable=documento_var, width=30, style='TEntry')
        documento_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Campo Teléfono
        ttk.Label(form_frame, text="Teléfono:", style="Info.TLabel").grid(row=2, column=0, pady=5, sticky='e')
        telefono_entry = ttk.Entry(form_frame, textvariable=telefono_var, width=30, style='TEntry')
        telefono_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Campo Email
        ttk.Label(form_frame, text="Email:", style="Info.TLabel").grid(row=3, column=0, pady=5, sticky='e')
        email_entry = ttk.Entry(form_frame, textvariable=email_var, width=30, style='TEntry')
        email_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def guardar_ahorrador():
            try:
                # Verificar si hay números asignados
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM numeros_rifa')
                hay_numeros = cursor.fetchone()[0] > 0
                conn.close()
                
                # Guardar ahorrador
                ahorrador_id = self.ahorrador_model.crear_ahorrador(
                    nombre=nombre_var.get(),
                    documento=documento_var.get(),
                    telefono=telefono_var.get(),
                    email=email_var.get()
                )
                
                # Si hay números, asignar al nuevo ahorrador
                if hay_numeros:
                    try:
                        self.rifa_model.asignar_numeros_nuevo_ahorrador(ahorrador_id)
                        mensaje = "Ahorrador creado correctamente y números asignados"
                    except Exception as e:
                        mensaje = f"Ahorrador creado pero no se asignaron números: {str(e)}"
                else:
                    mensaje = "Ahorrador creado correctamente"
                
                messagebox.showinfo("Éxito", mensaje)
                self.show_ahorradores_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Frame para botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=guardar_ahorrador,
                  style="Action.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.show_ahorradores_list,
                  style="Action.TButton").pack(side=tk.LEFT, padx=5)
    
    def show_ahorro_form(self):
        self.clear_main_frame()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        from ahorro_view import AhorroForm
        AhorroForm(self.main_frame, self.ahorro_model, self.ahorrador_model)
    
    def show_prestamo_form(self):
        self.clear_main_frame()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        from prestamo_view import PrestamoForm
        PrestamoForm(self.main_frame, self.prestamo_model, self.ahorrador_model)
    
    def show_reportes(self):
        self.clear_main_frame()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        from reportes_view import ReportesView
        ReportesView(self.main_frame, self.ahorrador_model, 
                    self.ahorro_model, self.prestamo_model)
        
    def show_estadisticas(self):
        self.clear_main_frame()
        from views.estadisticas_view import EstadisticasView
        EstadisticasView(self.main_frame, self.db)


    def show_rifa_form(self):
        self.clear_main_frame()
        from views.rifa_view import RifaForm
        RifaForm(self.main_frame, self.rifa_model, self.ahorrador_model)


def main():
    root = ThemedTk(theme="arc")  # Usar un tema moderno
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()