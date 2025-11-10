import heapq
import copy
from utils.constants import Constants
from models.burro import Burro

class PathFinder:
    def __init__(self, graph):
        self.graph = graph
    
    def find_max_stars_route(self, start_star_id, initial_health, initial_age, 
                           initial_energy, initial_grass, death_age):
        """
        2. Encuentra la ruta que permite visitar la mayor cantidad de estrellas
        antes de morir, usando solo valores iniciales
        """
        start_star_id = str(start_star_id)
        start_star = self.graph.get_star_by_id(start_star_id)
        if not start_star:
            return [start_star_id]
        
        # Crear burro con estado inicial
        burro = Burro(initial_health, initial_energy, initial_grass, initial_age, death_age)
        
        best_route = [start_star_id]
        best_count = 1
        
        # Usar BFS para explorar todas las rutas posibles
        queue = [(start_star_id, [start_star_id], copy.deepcopy(burro))]
        
        while queue:
            current_star_id, current_route, current_burro = queue.pop(0)
            
            # Actualizar mejor ruta si encontramos más estrellas
            if len(current_route) > best_count:
                best_route = current_route
                best_count = len(current_route)
            
            # Explorar estrellas adyacentes
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id not in current_route:  # Visitar solo una vez
                    # Crear copia del burro para simular
                    new_burro = copy.deepcopy(current_burro)
                    
                    # Simular viaje a la estrella vecina
                    if new_burro.travel(distance) and not new_burro.is_dead():
                        # Visitar la estrella (comer e investigar automáticamente)
                        neighbor_star = self.graph.get_star_by_id(neighbor_id)
                        if neighbor_star:
                            # Investigación automática (50% del tiempo restante)
                            research_time = neighbor_star.time_to_eat * 0.5
                            new_burro.visit_star(neighbor_star, research_time)
                            
                            if not new_burro.is_dead():
                                new_route = current_route + [neighbor_id]
                                queue.append((neighbor_id, new_route, new_burro))
        
        return best_route
    
    def find_optimal_route(self, start_star_id, initial_health, initial_energy, 
                          initial_grass, health_state):
        """
        3. Encuentra la ruta óptima que maximiza estrellas con mínimo gasto
        Considera comer automáticamente cuando energía < 50%
        """
        start_star_id = str(start_star_id)
        
        # Crear burro simulado
        burro = Burro(initial_health, initial_energy, initial_grass, 0, float('inf'))
        
        visited = set([start_star_id])
        route = [start_star_id]
        current_star_id = start_star_id
        
        while not burro.is_dead() and len(visited) < len(self.graph.all_stars):
            # Encontrar la estrella más eficiente para visitar
            best_next_star = None
            best_efficiency = -1
            
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id not in visited:
                    # Calcular eficiencia (distancia vs energía disponible)
                    efficiency = self._calculate_star_efficiency(distance, burro)
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_next_star = neighbor_id
            
            if best_next_star and burro.travel(distance):
                # Visitar la estrella (comer automáticamente si es necesario)
                star = self.graph.get_star_by_id(best_next_star)
                if star:
                    research_time = star.time_to_eat * 0.5  # 50% para investigación
                    burro.visit_star(star, research_time)
                    
                    route.append(best_next_star)
                    visited.add(best_next_star)
                    current_star_id = best_next_star
                else:
                    break
            else:
                break
        
        return route
    
    def find_route_to_destination(self, start_star_id, end_star_id):
        """Encuentra ruta más corta a destino específico"""
        return self._a_star_search(start_star_id, end_star_id)
    
    def _a_star_search(self, start_star_id, end_star_id):
        """Algoritmo A* para encontrar el camino más corto"""
        start_star_id = str(start_star_id)
        end_star_id = str(end_star_id)
        
        if start_star_id == end_star_id:
            return [start_star_id]
        
        open_set = []
        heapq.heappush(open_set, (0, start_star_id))
        
        came_from = {}
        g_score = {star_id: float('inf') for star_id in self.graph.all_stars}
        g_score[start_star_id] = 0
        
        f_score = {star_id: float('inf') for star_id in self.graph.all_stars}
        f_score[start_star_id] = self._heuristic(start_star_id, end_star_id)
        
        while open_set:
            current_f, current_star_id = heapq.heappop(open_set)
            
            if current_star_id == end_star_id:
                return self._reconstruct_path(came_from, current_star_id)
            
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            for neighbor_id, distance in adjacent_stars:
                tentative_g_score = g_score[current_star_id] + distance
                
                if tentative_g_score < g_score[neighbor_id]:
                    came_from[neighbor_id] = current_star_id
                    g_score[neighbor_id] = tentative_g_score
                    f_score[neighbor_id] = tentative_g_score + self._heuristic(neighbor_id, end_star_id)
                    
                    if neighbor_id not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
        
        return []  # No se encontró camino
    
    def _heuristic(self, star1_id, star2_id):
        """Heurística para A* (distancia euclidiana)"""
        star1 = self.graph.get_star_by_id(star1_id)
        star2 = self.graph.get_star_by_id(star2_id)
        
        if star1 and star2:
            dx = star1.coordinates['x'] - star2.coordinates['x']
            dy = star1.coordinates['y'] - star2.coordinates['y']
            return (dx**2 + dy**2) ** 0.5
        return float('inf')
    
    def _reconstruct_path(self, came_from, current_star_id):
        """Reconstruye el camino desde el destino hasta el inicio"""
        path = [current_star_id]
        while current_star_id in came_from:
            current_star_id = came_from[current_star_id]
            path.append(current_star_id)
        return path[::-1]
    
    def _calculate_star_efficiency(self, distance, burro):
        """Calcula la eficiencia de visitar una estrella"""
        # Priorizar estrellas cercanas cuando la energía es baja
        if burro.current_energy < 30:
            return 1000 / distance  # Alta prioridad para estrellas cercanas
        else:
            return 100 / distance  # Prioridad normal