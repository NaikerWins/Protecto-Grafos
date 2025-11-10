import sys
import os

# Añadir el directorio actual al path para que encuentre los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    print("Estructura de carpetas:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if file.endswith(".py"):
                print(f"{subindent}{file}")