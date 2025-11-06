from utils.constants import Constants

class EnergyCalculator:
    @staticmethod
    def calculate_energy_consumption(time_spent, health_state):
        """Calcula el consumo de energía basado en el tiempo y estado de salud"""
        base_consumption = time_spent * 0.1
        
        if health_state == Constants.HEALTH_EXCELLENT:
            return base_consumption * 0.8
        elif health_state == Constants.HEALTH_GOOD:
            return base_consumption
        elif health_state == Constants.HEALTH_POOR:
            return base_consumption * 1.3
        else:
            return base_consumption * 2.0
    
    @staticmethod
    def calculate_energy_gain_from_grass(grass_kg, health_state):
        """Calcula la energía ganada al consumir pasto"""
        energy_factor = Constants.ENERGY_FACTORS.get(health_state, 2)
        return grass_kg * energy_factor
    
    @staticmethod
    def calculate_eating_time(star_time_to_eat, max_time_ratio=Constants.MAX_EATING_TIME_RATIO):
        """Calcula el tiempo máximo que puede dedicar a comer"""
        return star_time_to_eat * max_time_ratio
    
    @staticmethod
    def calculate_research_energy_cost(research_time, health_state):
        """Calcula el costo de energía por investigación"""
        base_cost = research_time * 0.2
        
        if health_state == Constants.HEALTH_EXCELLENT:
            return base_cost * 0.7
        elif health_state == Constants.HEALTH_GOOD:
            return base_cost
        elif health_state == Constants.HEALTH_POOR:
            return base_cost * 1.5
        else:
            return base_cost * 2.0
    
    @staticmethod
    def update_health_state(current_energy, current_health):
        """Actualiza el estado de salud basado en la energía actual"""
        if current_energy >= 75:
            return Constants.HEALTH_EXCELLENT
        elif current_energy >= 50:
            return Constants.HEALTH_GOOD
        elif current_energy >= 25:
            return Constants.HEALTH_POOR
        elif current_energy > 0:
            return Constants.HEALTH_DYING
        else:
            return Constants.HEALTH_DEAD