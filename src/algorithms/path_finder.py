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
    
    def find_optimal_route(self, start_star_id, initial_health, initial_energy, initial_grass, health_state):
        """
        3. Encuentra la ruta óptima que maximiza estrellas visitadas 
        con mínimo consumo de recursos
        """
        start_star_id = str(start_star_id)
        start_star = self.graph.get_star_by_id(start_star_id)
        if not start_star:
            return [start_star_id]
        
        # Crear burro simulado para calcular consumo
        from models.burro import Burro
        simulated_burro = Burro(health_state, initial_energy, initial_grass, 0, float('inf'))
        
        visited = set([start_star_id])
        route = [start_star_id]
        current_star_id = start_star_id
        
        # Continuar mientras el burro esté vivo y queden estrellas por visitar
        while (not simulated_burro.is_dead() and 
               len(visited) < len(self.graph.all_stars)):
            
            # Encontrar la mejor estrella siguiente basada en eficiencia
            best_next_star = None
            best_efficiency = -float('inf')
            min_distance = float('inf')
            
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id not in visited:
                    # Calcular eficiencia considerando múltiples factores
                    efficiency = self._calculate_star_efficiency(
                        distance, simulated_burro, neighbor_id
                    )
                    
                    # Preferir estrellas con mejor eficiencia y menor distancia
                    if efficiency > best_efficiency or (efficiency == best_efficiency and distance < min_distance):
                        best_efficiency = efficiency
                        best_next_star = neighbor_id
                        min_distance = distance
            
            if best_next_star:
                # Simular viaje a la estrella seleccionada
                if simulated_burro.travel(min_distance):
                    # Visitar la estrella (comer automáticamente si es necesario)
                    next_star = self.graph.get_star_by_id(best_next_star)
                    if next_star:
                        # Investigación automática (50% del tiempo)
                        research_time = next_star.time_to_eat * 0.5
                        simulated_burro.visit_star(next_star, research_time)
                        
                        # Si el burro sigue vivo después de la visita, añadir a la ruta
                        if not simulated_burro.is_dead():
                            route.append(best_next_star)
                            visited.add(best_next_star)
                            current_star_id = best_next_star
                        else:
                            break
                    else:
                        break
                else:
                    break  # Burro murió durante el viaje
            else:
                break  # No hay más estrellas accesibles
        
        return route
    
    def _calculate_star_efficiency(self, distance, burro, star_id):
        """Calcula la eficiencia de visitar una estrella considerando múltiples factores"""
        star = self.graph.get_star_by_id(star_id)
        if not star:
            return -float('inf')
        
        # Factor 1: Eficiencia energética (preferir estrellas cercanas)
        distance_factor = 100.0 / (distance + 1)  # +1 para evitar división por cero
        
        # Factor 2: Estado del burro (si tiene poca energía, priorizar estrellas con buen research_effect)
        energy_factor = 1.0
        if burro.current_energy < 30:
            # Priorizar estrellas que den energía positiva
            energy_factor = max(1.0, star.research_effect * 2)
        
        # Factor 3: Eficiencia de investigación (preferir estrellas con buen research_effect)
        research_factor = 1.0 + (star.research_effect * 0.1)
        
        # Factor 4: Tiempo de comida (preferir estrellas con menos tiempo de comida)
        time_factor = 5.0 / (star.time_to_eat + 1)
        
        # Factor 5: Hipergigantes (darles prioridad moderada)
        hypergiant_factor = 1.5 if star.hypergiant else 1.0
        
        # Combinar todos los factores
        efficiency = (distance_factor * 0.4 + 
                     energy_factor * 0.2 + 
                     research_factor * 0.2 + 
                     time_factor * 0.1 + 
                     hypergiant_factor * 0.1)
        
        # Penalizar si el burro tiene muy poca energía y la estrella está lejos
        if burro.current_energy < 20 and distance > 100:
            efficiency *= 0.5
        
        return efficiency
    
    def find_route_to_destination(self, start_star_id, end_star_id):
        """Encuentra ruta más corta a destino específico usando Dijkstra mejorado"""
        start_star_id = str(start_star_id)
        end_star_id = str(end_star_id)
        
        # Verificar que las estrellas existen
        start_star = self.graph.get_star_by_id(start_star_id)
        end_star = self.graph.get_star_by_id(end_star_id)
        
        if not start_star or not end_star:
            return []
        
        # Si es la misma estrella
        if start_star_id == end_star_id:
            return [start_star_id]
        
        # Usar Dijkstra para encontrar el camino más corto
        distances = {star_id: float('inf') for star_id in self.graph.all_stars}
        previous = {star_id: None for star_id in self.graph.all_stars}
        distances[start_star_id] = 0
        
        # Usar una cola de prioridad
        import heapq
        pq = [(0, start_star_id)]
        
        while pq:
            current_distance, current_star_id = heapq.heappop(pq)
            
            # Si llegamos al destino, terminar
            if current_star_id == end_star_id:
                break
            
            # Si la distancia actual es mayor que la almacenada, ignorar
            if current_distance > distances[current_star_id]:
                continue
            
            # Explorar vecinos
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            for neighbor_id, distance in adjacent_stars:
                # Verificar que la conexión no esté bloqueada
                if self.graph.is_edge_blocked(current_star_id, neighbor_id):
                    continue
                    
                new_distance = current_distance + distance
                
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_star_id
                    heapq.heappush(pq, (new_distance, neighbor_id))
        
        # Reconstruir el camino desde el destino hasta el inicio
        route = []
        current = end_star_id
        
        # Si no hay camino al destino
        if distances[end_star_id] == float('inf'):
            return []
        
        while current is not None:
            route.append(current)
            current = previous.get(current)
        
        return route[::-1]  # Invertir para que quede inicio->destino
    
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