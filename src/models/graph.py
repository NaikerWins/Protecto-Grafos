from models.star import Star
from models.constellation import Constellation

class StarGraph:
    def __init__(self):
        self.constellations = []
        self.all_stars = {}
        self.blocked_edges = set()
        self.galaxies = set()  
    
    def add_constellation(self, constellation):
        self.constellations.append(constellation)
        
        for star in constellation.stars:
            star_id = str(star.id)
            if star_id in self.all_stars:
               
                original_id = star_id
                counter = 1
                while star_id in self.all_stars:
                    star_id = f"{original_id}_{counter}"
                    counter += 1
                star.id = star_id
            
            self.all_stars[star_id] = star
         
            if hasattr(star, 'galaxy'):
                self.galaxies.add(star.galaxy)
    
    def get_star_by_id(self, star_id):
        return self.all_stars.get(str(star_id))
    
    def get_all_stars(self):
        return list(self.all_stars.values())
    
    def get_constellation_for_star(self, star_id):
        star_id_str = str(star_id)
        for constellation in self.constellations:
            for star in constellation.stars:
                if str(star.id) == star_id_str:
                    return constellation
        return None
    
    def get_stars_by_galaxy(self, galaxy):
        return [star for star in self.all_stars.values() if getattr(star, 'galaxy', 'Vía Láctea') == galaxy]
    
    def get_hypergiant_stars(self, galaxy=None):
        hypergiants = [star for star in self.all_stars.values() if star.hypergiant]
        if galaxy:
            hypergiants = [star for star in hypergiants if getattr(star, 'galaxy', 'Vía Láctea') == galaxy]
        return hypergiants
    
    def get_stars_at_coordinates(self, x, y, tolerance=5):
        stars_at_point = []
        for star in self.all_stars.values():
            if (abs(star.coordinates['x'] - x) <= tolerance and 
                abs(star.coordinates['y'] - y) <= tolerance):
                stars_at_point.append(star)
        return stars_at_point
    
    def block_edge(self, star1_id, star2_id):
        edge = tuple(sorted([str(star1_id), str(star2_id)]))
        self.blocked_edges.add(edge)
    
    def unblock_edge(self, star1_id, star2_id):
        edge = tuple(sorted([str(star1_id), str(star2_id)]))
        if edge in self.blocked_edges:
            self.blocked_edges.remove(edge)
    
    def is_edge_blocked(self, star1_id, star2_id):
        edge = tuple(sorted([str(star1_id), str(star2_id)]))
        return edge in self.blocked_edges
    
    def get_adjacent_stars(self, star_id):
        star = self.get_star_by_id(star_id)
        if not star:
            return []
        
        adjacent = []
        for connection in star.linked_to:
            connected_star_id = str(connection['starId'])
            if not self.is_edge_blocked(star_id, connected_star_id):
                adjacent.append((connected_star_id, connection['distance']))
        
        return adjacent
    
    def find_path_bfs(self, start_star_id, end_star_id=None):
        start_star_id = str(start_star_id)
        if end_star_id:
            end_star_id = str(end_star_id)
        
        visited = set()
        queue = [(start_star_id, [start_star_id])]
        
        while queue:
            current_star_id, path = queue.pop(0)
            
            if end_star_id and current_star_id == end_star_id:
                return path
            
            if current_star_id not in visited:
                visited.add(current_star_id)
                
                adjacent_stars = self.get_adjacent_stars(current_star_id)
                for neighbor_id, distance in adjacent_stars:
                    if neighbor_id not in visited:
                        new_path = path + [neighbor_id]
                        queue.append((neighbor_id, new_path))
            
            if not end_star_id and len(visited) == len(self.all_stars):
                break
        
        return path if not end_star_id else []