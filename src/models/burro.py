import math
import winsound  # Para sonido en Windows
import threading
from utils.constants import Constants

class Burro:
    def __init__(self, health_state, initial_energy, grass, start_age, death_age):
        self.health_state = health_state
        self.current_energy = initial_energy
        self.grass = grass  # kg
        self.current_age = start_age  # años
        self.death_age = death_age
        self.remaining_life = death_age - start_age  # años luz restantes
        self.visited_stars = []
        self.total_research_time = 0
        self.total_food_consumed = 0
        self.total_distance_traveled = 0
        self.stars_visited_count = 0
        self.current_galaxy = "Vía Láctea"  # 3c. Galaxia actual
        self.research_effects_log = []  # 3a. Log de efectos de investigación
        
        # Actualizar estado de salud inicial basado en energía
        self._update_health_state()
        
    def travel(self, distance, target_galaxy=None):
        """Realiza un viaje entre estrellas - consume VIDA (años luz)"""
        if self.is_dead():
            return False
            
        # 3b. Reducir TIEMPO DE VIDA por distancia (años luz)
        self.remaining_life -= distance
        self.total_distance_traveled += distance
        
        # 3c. Cambiar de galaxia si es necesario
        if target_galaxy and target_galaxy != self.current_galaxy:
            self.current_galaxy = target_galaxy
        
        # Reducir energía por viaje (depende del estado de salud)
        energy_cost = self._calculate_travel_energy_cost(distance)
        self.current_energy = max(0, self.current_energy - energy_cost)
        
        # Actualizar estado de salud AUTOMÁTICAMENTE
        self._update_health_state()
        
        return not self.is_dead()
    
    def visit_star(self, star, research_time=0, research_effect_override=None):
        """Visita una estrella y realiza actividades automáticamente"""
        if self.is_dead():
            return False
            
        # Registrar visita (solo una vez por estrella)
        if star and star.id not in [s.id for s in self.visited_stars]:
            self.visited_stars.append(star)
            self.stars_visited_count += 1
        
        # 3. COMER PASTO AUTOMÁTICAMENTE si tiene menos del 50% de energía
        if self.current_energy < 50 and self.grass > 0:
            self._auto_eat_grass(star)
        
        # 3a. Realizar investigación automáticamente
        if research_time > 0:
            effect = research_effect_override if research_effect_override is not None else star.research_effect
            self.do_research(research_time, effect, star.label)
        
        return not self.is_dead()
    
    def _auto_eat_grass(self, star):
        """Come pasto automáticamente cuando la energía es < 50%"""
        # Calcular cuánto pasto necesita para llegar al 50%
        energy_needed = 50 - self.current_energy
        
        # 3. Calcular cuánto pasto puede comer según tiempo disponible
        max_eating_time = star.time_to_eat * Constants.MAX_EATING_TIME_RATIO
        max_grass_to_eat = min(max_eating_time, self.grass, energy_needed / Constants.ENERGY_FACTORS.get(self.health_state, 2))
        
        if max_grass_to_eat > 0:
            # Calcular energía ganada según estado de salud
            energy_gain = max_grass_to_eat * Constants.ENERGY_FACTORS.get(self.health_state, 2)
            self.current_energy = min(100, self.current_energy + energy_gain)
            
            # Reducir pasto
            self.grass -= max_grass_to_eat
            self.total_food_consumed += max_grass_to_eat
            
            # Actualizar estado de salud
            self._update_health_state()
    
    def do_research(self, research_time, research_effect, star_name=""):
        """3a. Realiza labores de investigación - puede ganar/perder VIDA"""
        # Consumir energía por investigación
        research_energy_cost = self._calculate_research_energy_cost(research_time)
        self.current_energy = max(0, self.current_energy - research_energy_cost)
        
        # Efecto en tiempo de vida (positivo gana vida, negativo pierde)
        life_effect = research_effect
        self.remaining_life += life_effect
        
        self.total_research_time += research_time
        
        # Registrar efecto de investigación
        effect_type = "GANANCIA" if life_effect > 0 else "PÉRDIDA" if life_effect < 0 else "NEUTRO"
        self.research_effects_log.append({
            'star': star_name,
            'effect': life_effect,
            'type': effect_type,
            'research_time': research_time
        })
        
        # Actualizar estado de salud
        self._update_health_state()
        
        return life_effect
    
    def use_hypergiant(self, target_galaxy=None, target_star_id=None):
        """3c. Usa una estrella hipergigante - efectos AUTOMÁTICOS"""
        # Recargar energía (50% de la actual)
        self.current_energy += self.current_energy * 0.5
        self.current_energy = min(100, self.current_energy)
        
        # Duplicar pasto
        self.grass *= 2
        
        # Cambiar de galaxia si se especifica
        if target_galaxy:
            self.current_galaxy = target_galaxy
        
        # Actualizar estado de salud
        self._update_health_state()
        
        return True
    
    def feed_grass(self, kg, star_time_to_eat):
        """Método PÚBLICO para alimentar al burro manualmente"""
        if kg > self.grass:
            kg = self.grass  # No puede comer más de lo que tiene
            
        max_eating_time = star_time_to_eat * Constants.MAX_EATING_TIME_RATIO
        actual_eating_time = min(max_eating_time, kg)
        
        # Calcular energía ganada según estado de salud
        energy_gain = kg * Constants.ENERGY_FACTORS.get(self.health_state, 2)
        self.current_energy = min(100, self.current_energy + energy_gain)
        
        # Reducir pasto
        self.grass -= kg
        self.total_food_consumed += kg
        
        # Actualizar estado de salud
        self._update_health_state()
        
        return energy_gain
    
    def _calculate_travel_energy_cost(self, distance):
        """Calcula el costo de energía para viajar según estado de salud"""
        base_cost = distance * 0.1  # Costo base por año luz
        
        # El costo varía según el estado de salud
        health_multiplier = {
            Constants.HEALTH_EXCELLENT: 0.5,   # Excelente: menos costo
            Constants.HEALTH_GOOD: 0.8,        # Buena: costo moderado
            Constants.HEALTH_POOR: 1.5,        # Mala: más costo
            Constants.HEALTH_DYING: 3.0,       # Moribundo: mucho costo
            Constants.HEALTH_DEAD: 0.0
        }
        
        return base_cost * health_multiplier.get(self.health_state, 1.0)
    
    def _calculate_research_energy_cost(self, research_time):
        """Calcula el costo de energía por investigación"""
        base_cost = research_time * 0.2
        
        health_multiplier = {
            Constants.HEALTH_EXCELLENT: 0.7,
            Constants.HEALTH_GOOD: 1.0,
            Constants.HEALTH_POOR: 1.8,
            Constants.HEALTH_DYING: 3.0
        }
        
        return base_cost * health_multiplier.get(self.health_state, 1.0)
    
    def _update_health_state(self):
        """2. Actualiza AUTOMÁTICAMENTE el estado de salud basado en la energía actual"""
        # Asociación automática energía -> estado de salud (cada 25%)
        if self.current_energy >= 75:
            new_state = Constants.HEALTH_EXCELLENT
        elif self.current_energy >= 50:
            new_state = Constants.HEALTH_GOOD
        elif self.current_energy >= 25:
            new_state = Constants.HEALTH_POOR
        elif self.current_energy > 0:
            new_state = Constants.HEALTH_DYING
        else:
            new_state = Constants.HEALTH_DEAD
        
        # Solo actualizar si cambió
        if self.health_state != new_state:
            self.health_state = new_state
    
    def is_dead(self):
        """Verifica si el burro está muerto"""
        return (self.health_state == Constants.HEALTH_DEAD or 
                self.remaining_life <= 0 or 
                self.current_age >= self.death_age)
    
    def play_death_sound(self):
        """3b. Reproduce sonido de muerte del burro"""
        try:
            # Sonido simple (beep) - puedes reemplazar con archivo de sonido
            def play_sound():
                winsound.Beep(200, 1000)  # Frecuencia 200Hz por 1 segundo
                winsound.Beep(150, 800)   # Frecuencia 150Hz por 0.8 segundos
            
            # Ejecutar en hilo separado para no bloquear la interfaz
            sound_thread = threading.Thread(target=play_sound)
            sound_thread.daemon = True
            sound_thread.start()
        except:
            # Si winsound no está disponible, ignorar
            pass
    
    def get_status(self):
        """Obtiene el estado actual AUTOMÁTICO del burro"""
        return {
            'health_state': self.health_state,
            'current_energy': self.current_energy,
            'grass': self.grass,
            'current_age': self.current_age,
            'remaining_life': self.remaining_life,
            'visited_stars_count': self.stars_visited_count,
            'total_distance': self.total_distance_traveled,
            'total_research_time': self.total_research_time,
            'total_food_consumed': self.total_food_consumed,
            'current_galaxy': self.current_galaxy,
            'research_effects': self.research_effects_log,
            'is_alive': not self.is_dead()
        }