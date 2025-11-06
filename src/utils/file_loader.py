import json
import os
from exceptions.file_exceptions import FileLoadError, InvalidJSONError

class FileLoader:
    @staticmethod
    def load_constellations(file_path):
        """
        Carga el archivo JSON de constelaciones
        """
        try:
            if not os.path.exists(file_path):
                raise FileLoadError(f"El archivo {file_path} no existe")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Validar estructura básica
            if 'constellations' not in data:
                raise InvalidJSONError("El archivo JSON no contiene el campo 'constellations'")
            
            return data
            
        except json.JSONDecodeError as e:
            raise InvalidJSONError(f"Error al decodificar JSON: {str(e)}")
        except Exception as e:
            raise FileLoadError(f"Error al cargar el archivo: {str(e)}")
    
    @staticmethod
    def save_constellations(file_path, data):
        """
        Guarda los datos en un archivo JSON
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            raise FileLoadError(f"Error al guardar el archivo: {str(e)}")