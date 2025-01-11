# main.py
import os
import sys
from ttkthemes import ThemedTk
from PIL import Image, ImageTk

# Configuración de paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))
sys.path.append(os.path.join(current_dir, 'src', 'views'))

# Importar la ventana principal y login
from src.views.main_window import MainWindow
from src.views.login_window import show_login


def main():    
    # Iniciar la aplicación
    root = ThemedTk(theme="arc")
    
    # Configurar los íconos
    icon_path = os.path.join(current_dir, 'src', 'assets', 'peso.ico')
    logo_path = os.path.join(current_dir, 'src', 'assets', 'icono.png')
    
    # Establecer ícono de la ventana
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    
    # Cargar logo para usar en la interfaz
    if os.path.exists(logo_path):
        # Cargar y redimensionar la imagen
        pil_image = Image.open(logo_path)
        # Redimensionar a un tamaño más pequeño (por ejemplo, 100x100)
        pil_image = pil_image.resize((100, 100), Image.Resampling.LANCZOS)
        root.logo_image = ImageTk.PhotoImage(pil_image)
    else:
        root.logo_image = None
    
    # Mostrar ventana de login
    if not show_login(root):
        return  # Si el login no es exitoso, terminar el programa
    
    # Configurar ventana principal
    root.title("Sistema de Natillera Johana Franco 👩🏻🦒")
    # root.state('zoomed')
    
    # Iniciar la aplicación principal
    app = MainWindow(root)
    
    # Centrar la ventana si no está maximizada
    if root.state() != 'zoomed':
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 1024) // 2
        y = (screen_height - 768) // 2
        root.geometry(f"1150x600+{x}+{y}")
    
    # Iniciar el loop principal
    try:
        root.mainloop()
    except Exception as e:
        import traceback
        print("Error en la aplicación:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()