class Validators:
    @staticmethod
    def validate_coordinates(x, y):
        """Valida que las coordenadas estén dentro del rango permitido"""
        return 0 <= x <= 200 and 0 <= y <= 200
    
    @staticmethod
    def validate_energy(energy):
        """Valida que la energía esté entre 0 y 100"""
        return 0 <= energy <= 100
    
    @staticmethod
    def validate_health_state(state):
        """Valida el estado de salud"""
        valid_states = ["Excelente", "Buena", "Mala", "Moribundo", "Muerto"]
        return state in valid_states