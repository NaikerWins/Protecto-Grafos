import heapq
from utils.constants import Constants

class PathFinder:
    def __init__(self, graph):
        self.graph = graph
    
    def find_max_stars_route(self, start_star_id, initial_health, initial_age, 
                           initial_energy, initial_grass, death_age):
        """
        Encuentra la ruta que permite visitar la mayor cantidad de estrellas
        antes de que el burro muera
        """
        start_star = self.graph.get_star_by_id(start_star_id)
        if not start_star:
            return []
        
        # Implementación de BFS modificado considerando recursos
        visited = set()
        queue = [(start_star_id, initial_energy, initial_grass, initial_age, [start_star_id])]
        best_route = []
        
        while queue:
            current_star_id, current_energy, current_grass, current_age, route = queue.pop(0)
            
            if len(route) > len(best_route):
                best_route = route
            
            if current_age >= death_age:
                continue
            
            current_star = self.graph.get_star_by_id(current_star_id)
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id not in visited:
                    # Calcular nuevo estado después del viaje
                    travel_energy_cost = self._calculate_travel_energy_cost(distance, initial_health)
                    new_energy = current_energy - travel_energy_cost
                    new_age = current_age + distance
                    
                    if new_energy > 0 and new_age < death_age:
                        visited.add(neighbor_id)
                        new_route = route + [neighbor_id]
                        queue.append((neighbor_id, new_energy, current_grass, new_age, new_route))
        
        return best_route
    
    def find_optimal_route(self, start_star_id, initial_health, initial_energy, 
                          initial_grass, health_state):
        """
        Encuentra la ruta óptima considerando consumo de energía y pasto
        """
        # Implementación de Dijkstra modificado
        distances = {star_id: float('inf') for star_id in self.graph.all_stars}
        previous = {star_id: None for star_id in self.graph.all_stars}
        distances[start_star_id] = 0
        
        pq = [(0, start_star_id, initial_energy, initial_grass, [])]
        
        while pq:
            current_cost, current_star_id, current_energy, current_grass, current_route = heapq.heappop(pq)
            
            if current_cost > distances[current_star_id]:
                continue
            
            current_star = self.graph.get_star_by_id(current_star_id)
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id in current_route:  # Evitar ciclos
                    continue
                
                # Calcular costos de viaje y consumo
                travel_cost = self._calculate_travel_cost(distance, current_energy, health_state)
                energy_after_travel = current_energy - travel_cost['energy_cost']
                grass_after_travel = current_grass - travel_cost['grass_consumed']
                
                if energy_after_travel > 0 and grass_after_travel >= 0:
                    new_cost = current_cost + travel_cost['total_cost']
                    new_route = current_route + [current_star_id]
                    
                    if new_cost < distances[neighbor_id]:
                        distances[neighbor_id] = new_cost
                        previous[neighbor_id] = current_star_id
                        heapq.heappush(pq, (new_cost, neighbor_id, energy_after_travel, 
                                          grass_after_travel, new_route))
        
        # Reconstruir la ruta óptima
        return self._reconstruct_optimal_route(previous, start_star_id)
    
    def _calculate_travel_energy_cost(self, distance, health_state):
        """Calcula el costo de energía para viajar una distancia"""
        base_cost = distance * 0.1  # Costo base por año luz
        
        if health_state == Constants.HEALTH_EXCELLENT:
            return base_cost * 0.8
        elif health_state == Constants.HEALTH_GOOD:
            return base_cost
        elif health_state == Constants.HEALTH_POOR:
            return base_cost * 1.2
        else:
            return base_cost * 1.5
    
    def _calculate_travel_cost(self, distance, current_energy, health_state):
        """Calcula el costo total de viaje entre estrellas"""
        energy_cost = self._calculate_travel_energy_cost(distance, health_state)
        
        # Calcular consumo de pasto si la energía es baja
        grass_consumed = 0
        if current_energy - energy_cost < 50:  # Menos del 50% de energía
            grass_needed = min(1, (50 - (current_energy - energy_cost)) / Constants.ENERGY_FACTORS[health_state])
            grass_consumed = grass_needed
        
        total_cost = distance + energy_cost * 2 + grass_consumed * 10
        
        return {
            'energy_cost': energy_cost,
            'grass_consumed': grass_consumed,
            'total_cost': total_cost
        }
    
    def _reconstruct_optimal_route(self, previous, start_star_id):
        """Reconstruye la ruta óptima desde el diccionario de predecesores"""
        # Encontrar el nodo con la menor distancia
        if not any(previous.values()):
            return []
        
        end_star_id = min(previous.keys(), key=lambda x: previous[x] if previous[x] else float('inf'))
        
        route = []
        current = end_star_id
        while current is not None:
            route.append(current)
            current = previous[current]
        
        return route[::-1]  # Invertir para tener inicio -> fin