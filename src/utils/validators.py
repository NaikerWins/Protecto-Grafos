class Validators:
    @staticmethod
    def validate_coordinates(x, y):
        # Validates that the coordinates are within the allowed range
        return 0 <= x <= 200 and 0 <= y <= 200
    
    @staticmethod
    def validate_energy(energy):
        # Validates that the energy is between 0 and 100
        return 0 <= energy <= 100
    
    @staticmethod
    def validate_health_state(state):
        # Validates the health state
        valid_states = ["Excelente", "Buena", "Mala", "Moribundo", "Muerto"]
        return state in valid_states