import heapq
import copy
from utils.constants import Constants
from models.burro import Burro

class PathFinder:
    def __init__(self, graph):
        self.graph = graph
    
    def find_max_stars_route(self, start_star_id, initial_health, initial_age, 
                           initial_energy, initial_grass, death_age):
       
        start_star_id = str(start_star_id)
        start_star = self.graph.get_star_by_id(start_star_id)
        if not start_star:
            return [start_star_id]
        
        burro = Burro(initial_health, initial_energy, initial_grass, initial_age, death_age)
        
        best_route = [start_star_id]
        best_count = 1
        
        queue = [(start_star_id, [start_star_id], copy.deepcopy(burro))]
        
        while queue:
            current_star_id, current_route, current_burro = queue.pop(0)
            
            if len(current_route) > best_count:
                best_route = current_route
                best_count = len(current_route)
            
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id not in current_route:  
                    new_burro = copy.deepcopy(current_burro)
                    
                    if new_burro.travel(distance) and not new_burro.is_dead():
                        neighbor_star = self.graph.get_star_by_id(neighbor_id)
                        if neighbor_star:
                            research_time = neighbor_star.time_to_eat * 0.5
                            new_burro.visit_star(neighbor_star, research_time)
                            
                            if not new_burro.is_dead():
                                new_route = current_route + [neighbor_id]
                                queue.append((neighbor_id, new_route, new_burro))
        
        return best_route
    
    def find_optimal_route(self, start_star_id, initial_health, initial_energy, initial_grass, health_state):
        
        start_star_id = str(start_star_id)
        start_star = self.graph.get_star_by_id(start_star_id)
        if not start_star:
            return [start_star_id]
        
        from models.burro import Burro
        simulated_burro = Burro(health_state, initial_energy, initial_grass, 0, float('inf'))
        
        visited = set([start_star_id])
        route = [start_star_id]
        current_star_id = start_star_id
        
        while (not simulated_burro.is_dead() and 
               len(visited) < len(self.graph.all_stars)):
            
            best_next_star = None
            best_efficiency = -float('inf')
            min_distance = float('inf')
            
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            
            for neighbor_id, distance in adjacent_stars:
                if neighbor_id not in visited:
                    efficiency = self._calculate_star_efficiency(
                        distance, simulated_burro, neighbor_id
                    )
                    
                    if efficiency > best_efficiency or (efficiency == best_efficiency and distance < min_distance):
                        best_efficiency = efficiency
                        best_next_star = neighbor_id
                        min_distance = distance
            
            if best_next_star:
                if simulated_burro.travel(min_distance):
                    next_star = self.graph.get_star_by_id(best_next_star)
                    if next_star:
                        research_time = next_star.time_to_eat * 0.5
                        simulated_burro.visit_star(next_star, research_time)
                        
                        if not simulated_burro.is_dead():
                            route.append(best_next_star)
                            visited.add(best_next_star)
                            current_star_id = best_next_star
                        else:
                            break
                    else:
                        break
                else:
                    break 
            else:
                break  
        
        return route
    
    def _calculate_star_efficiency(self, distance, burro, star_id):
        star = self.graph.get_star_by_id(star_id)
        if not star:
            return -float('inf')
        
        distance_factor = 100.0 / (distance + 1)
        
        energy_factor = 1.0
        if burro.current_energy < 30:
            energy_factor = max(1.0, star.research_effect * 2)
        
        research_factor = 1.0 + (star.research_effect * 0.1)
        
        time_factor = 5.0 / (star.time_to_eat + 1)
        
        hypergiant_factor = 1.5 if star.hypergiant else 1.0
        
        efficiency = (distance_factor * 0.4 + 
                     energy_factor * 0.2 + 
                     research_factor * 0.2 + 
                     time_factor * 0.1 + 
                     hypergiant_factor * 0.1)
        
        if burro.current_energy < 20 and distance > 100:
            efficiency *= 0.5
        
        return efficiency
    
    def find_route_to_destination(self, start_star_id, end_star_id):
        start_star_id = str(start_star_id)
        end_star_id = str(end_star_id)
        
        start_star = self.graph.get_star_by_id(start_star_id)
        end_star = self.graph.get_star_by_id(end_star_id)
        
        if not start_star or not end_star:
            return []
        
        if start_star_id == end_star_id:
            return [start_star_id]
        
        distances = {star_id: float('inf') for star_id in self.graph.all_stars}
        previous = {star_id: None for star_id in self.graph.all_stars}
        distances[start_star_id] = 0
        
        import heapq
        pq = [(0, start_star_id)]
        
        while pq:
            current_distance, current_star_id = heapq.heappop(pq)
            
            if current_star_id == end_star_id:
                break
            
            if current_distance > distances[current_star_id]:
                continue
            
            adjacent_stars = self.graph.get_adjacent_stars(current_star_id)
            for neighbor_id, distance in adjacent_stars:
                if self.graph.is_edge_blocked(current_star_id, neighbor_id):
                    continue
                    
                new_distance = current_distance + distance
                
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_star_id
                    heapq.heappush(pq, (new_distance, neighbor_id))
        
        route = []
        current = end_star_id
        

        if distances[end_star_id] == float('inf'):
            return []
        
        while current is not None:
            route.append(current)
            current = previous.get(current)
        
        return route[::-1]  
    
    def _a_star_search(self, start_star_id, end_star_id):
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
        
        return [] 
    
    def _heuristic(self, star1_id, star2_id):
        star1 = self.graph.get_star_by_id(star1_id)
        star2 = self.graph.get_star_by_id(star2_id)
        
        if star1 and star2:
            dx = star1.coordinates['x'] - star2.coordinates['x']
            dy = star1.coordinates['y'] - star2.coordinates['y']
            return (dx**2 + dy**2) ** 0.5
        return float('inf')
    
    def _reconstruct_path(self, came_from, current_star_id):
        path = [current_star_id]
        while current_star_id in came_from:
            current_star_id = came_from[current_star_id]
            path.append(current_star_id)
        return path[::-1]
    
    def _calculate_star_efficiency(self, distance, burro):
 
        if burro.current_energy < 30:
            return 1000 / distance 
        else:
            return 100 / distance