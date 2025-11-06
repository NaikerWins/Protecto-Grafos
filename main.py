import sys
import os

# Añadir las carpetas al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))

try:
    from gui.main_window import MainWindow
    import tkinter as tk
    
    def main():
        """Función principal que inicia la aplicación"""
        root = tk.Tk()
        root.title("Sistema de Navegación Estelar - NASA")
        root.geometry("1200x800")
        
        app = MainWindow(root)
        root.mainloop()

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de que todos los archivos __init__.py estén creados")