import json
import os
from exceptions.file_exceptions import FileLoadError, InvalidJSONError
from models.star import Star
from models.constellation import Constellation

class FileLoader:
    @staticmethod
    def load_constellations(file_path):
        try:
            if not os.path.exists(file_path):
                raise FileLoadError(f"El archivo {file_path} no existe")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if 'constellations' not in data:
                raise InvalidJSONError("El archivo JSON no contiene el campo 'constellations'")
            
            return data
            
        except json.JSONDecodeError as e:
            raise InvalidJSONError(f"Error al decodificar JSON: {str(e)}")
        except Exception as e:
            raise FileLoadError(f"Error al cargar el archivo: {str(e)}")
    
    @staticmethod
    def process_star_data(star_data, constellation_name, galaxy):
        return Star(
            star_id=star_data['id'],
            label=star_data['label'],
            coordinates=star_data['coordenates'],
            radius=star_data['radius'],
            time_to_eat=star_data['timeToEat'],
            amount_of_energy=star_data['amountOfEnergy'],
            research_effect=star_data.get('researchEffect', 0),
            hypergiant=star_data.get('hypergiant', False),
            linked_to=star_data['linkedTo'],
            galaxy=galaxy 
        )