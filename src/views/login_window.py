# src/views/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.success = False
        
        # Color rosa para el fondo
        self.background_color = '#FFE4E1'  # Rosa pastel
        self.root.configure(bg=self.background_color)
        
        # Configurar ventana
        window_width = 260
        window_height = 340
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Hacer que la ventana no sea redimensionable
        self.root.resizable(False, False)
        
        # Estilo
        self.style = ttk.Style()
        self.style.configure("Main.TFrame", background=self.background_color)
        self.style.configure("Title.TLabel", 
                           font=('Helvetica', 16, 'bold'), 
                           foreground='black',
                           background=self.background_color)
        self.style.configure("TLabel", 
                           font=('Helvetica', 10), 
                           foreground='black',
                           background=self.background_color)
        self.style.configure("TEntry", foreground='black')
        self.style.configure("TButton", font=('Helvetica', 10), foreground='black')
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20", style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        ttk.Label(main_frame, text="Sistema de Natillera", 
                 style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(main_frame, text="Johana Franco 👩🏻🦒", 
                 style="Title.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Logo (si existe)
        if hasattr(self.root, 'logo_image'):
            logo_label = ttk.Label(main_frame, image=self.root.logo_image, background=self.background_color)
            logo_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Campo de contraseña
        ttk.Label(main_frame, text="Contraseña:", 
                 style="TLabel").grid(row=3, column=0, padx=5, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, 
                                      textvariable=self.password_var, 
                                      show="*",
                                      style="TEntry")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Botón de ingreso
        ttk.Button(main_frame, text="Ingresar", 
                  command=self.validate_password,
                  style="TButton",
                  width=20).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.validate_password())
        
        # Focus en el campo de contraseña
        self.password_entry.focus()
    
    def validate_password(self):
        CORRECT_PASSWORD = "nati2025"
        
        if self.password_var.get() == CORRECT_PASSWORD:
            self.success = True
            self.root.quit()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
            self.password_var.set("")
            self.password_entry.focus()

def show_login(root):
    login = LoginWindow(root)
    root.mainloop()
    success = login.success
    if not success:
        root.destroy()
    return success