import math
import winsound
import threading
from utils.constants import Constants

class Burro:
    def __init__(self, health_state, initial_energy, grass, start_age, death_age):
        self.health_state = health_state
        self.current_energy = initial_energy
        self.grass = grass  # kg
        self.current_age = start_age  # years
        self.death_age = death_age
        self.remaining_life = death_age - start_age
        self.visited_stars = []
        self.total_research_time = 0
        self.total_food_consumed = 0
        self.total_distance_traveled = 0
        self.stars_visited_count = 0
        self.current_galaxy = "Vía Láctea"  
        self.research_effects_log = []  
        
        self._update_health_state()
        
    def travel(self, distance, target_galaxy=None):
        if self.is_dead():
            return False
            
        self.remaining_life -= distance
        self.total_distance_traveled += distance
        
        if target_galaxy and target_galaxy != self.current_galaxy:
            self.current_galaxy = target_galaxy
        
        energy_cost = self._calculate_travel_energy_cost(distance)
        self.current_energy = max(0, self.current_energy - energy_cost)
        
        self._update_health_state()
        
        return not self.is_dead()
    
    def visit_star(self, star, research_time=0, research_effect_override=None):
        if self.is_dead():
            return False
            
        if star and star.id not in [s.id for s in self.visited_stars]:
            self.visited_stars.append(star)
            self.stars_visited_count += 1
        
        if self.current_energy < 50 and self.grass > 0:
            self._auto_eat_grass(star)
        
        if research_time > 0:
            effect = research_effect_override if research_effect_override is not None else star.research_effect
            self.do_research(research_time, effect, star.label)
        
        return not self.is_dead()
    
    def _auto_eat_grass(self, star):
        energy_needed = 50 - self.current_energy
        
        max_eating_time = star.time_to_eat * Constants.MAX_EATING_TIME_RATIO
        max_grass_to_eat = min(max_eating_time, self.grass, energy_needed / Constants.ENERGY_FACTORS.get(self.health_state, 2))
        
        if max_grass_to_eat > 0:
            energy_gain = max_grass_to_eat * Constants.ENERGY_FACTORS.get(self.health_state, 2)
            self.current_energy = min(100, self.current_energy + energy_gain)
            
            self.grass -= max_grass_to_eat
            self.total_food_consumed += max_grass_to_eat
            
            self._update_health_state()
    
    def do_research(self, research_time, research_effect, star_name=""):
        research_energy_cost = self._calculate_research_energy_cost(research_time)
        self.current_energy = max(0, self.current_energy - research_energy_cost)
        
        life_effect = research_effect
        self.remaining_life += life_effect
        
        self.total_research_time += research_time
        
        effect_type = "GANANCIA" if life_effect > 0 else "PÉRDIDA" if life_effect < 0 else "NEUTRO"
        self.research_effects_log.append({
            'star': star_name,
            'effect': life_effect,
            'type': effect_type,
            'research_time': research_time
        })
        
        self._update_health_state()
        
        return life_effect
    
    def use_hypergiant(self, target_galaxy=None, target_star_id=None):
        self.current_energy += self.current_energy * 0.5
        self.current_energy = min(100, self.current_energy)
        
        self.grass *= 2
        
        if target_galaxy:
            self.current_galaxy = target_galaxy
        
        self._update_health_state()
        
        return True
    
    def feed_grass(self, kg, star_time_to_eat):
        if kg > self.grass:
            kg = self.grass 
            
        max_eating_time = star_time_to_eat * Constants.MAX_EATING_TIME_RATIO
        actual_eating_time = min(max_eating_time, kg)
        
        energy_gain = kg * Constants.ENERGY_FACTORS.get(self.health_state, 2)
        self.current_energy = min(100, self.current_energy + energy_gain)
        
        self.grass -= kg
        self.total_food_consumed += kg
        
        self._update_health_state()
        
        return energy_gain
    
    def _calculate_travel_energy_cost(self, distance):
        base_cost = distance * 0.1 
        
        health_multiplier = {
            Constants.HEALTH_EXCELLENT: 0.5,  
            Constants.HEALTH_GOOD: 0.8,       
            Constants.HEALTH_POOR: 1.5,       
            Constants.HEALTH_DYING: 3.0,  
            Constants.HEALTH_DEAD: 0.0
        }
        
        return base_cost * health_multiplier.get(self.health_state, 1.0)
    
    def _calculate_research_energy_cost(self, research_time):
        base_cost = research_time * 0.2
        
        health_multiplier = {
            Constants.HEALTH_EXCELLENT: 0.7,
            Constants.HEALTH_GOOD: 1.0,
            Constants.HEALTH_POOR: 1.8,
            Constants.HEALTH_DYING: 3.0
        }
        
        return base_cost * health_multiplier.get(self.health_state, 1.0)
    
    def _update_health_state(self):
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
        
        if self.health_state != new_state:
            self.health_state = new_state
    
    def is_dead(self):
        return (self.health_state == Constants.HEALTH_DEAD or 
                self.remaining_life <= 0 or 
                self.current_age >= self.death_age)
    
    def play_death_sound(self):
        try:
            def play_sound():
                winsound.Beep(200, 1000) 
                winsound.Beep(150, 800)   
            
            sound_thread = threading.Thread(target=play_sound)
            sound_thread.daemon = True
            sound_thread.start()
        except:
            pass
    
    def get_status(self):
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