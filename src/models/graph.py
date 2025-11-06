from models.star import Star
from models.constellation import Constellation

class StarGraph:
    def __init__(self):
        self.constellations = []
        self.all_stars = {}  # Diccionario para acceso rápido por ID
        self.blocked_edges = set()  # Aristas bloqueadas
    
    def add_constellation(self, constellation):
        """Añade una constelación al grafo"""
        self.constellations.append(constellation)
        
        # Actualizar diccionario de estrellas (manejar IDs duplicados)
        for star in constellation.stars:
            if star.id in self.all_stars:
                # Si ya existe una estrella con este ID, crear una versión única
                original_id = star.id
                counter = 1
                while star.id in self.all_stars:
                    star.id = f"{original_id}_{counter}"
                    counter += 1
            self.all_stars[star.id] = star
    
    def get_star_by_id(self, star_id):
        """Obtiene una estrella por su ID"""
        return self.all_stars.get(star_id)
    
    def get_all_stars(self):
        """Retorna todas las estrellas del grafo"""
        return list(self.all_stars.values())
    
    def get_constellation_for_star(self, star_id):
        """Encuentra la constelación a la que pertenece una estrella"""
        for constellation in self.constellations:
            for star in constellation.stars:
                if star.id == star_id:
                    return constellation
        return None
    
    def get_stars_at_coordinates(self, x, y, tolerance=5):
        """Encuentra estrellas en coordenadas específicas"""
        stars_at_point = []
        for star in self.all_stars.values():
            if (abs(star.coordinates['x'] - x) <= tolerance and 
                abs(star.coordinates['y'] - y) <= tolerance):
                stars_at_point.append(star)
        return stars_at_point
    
    def block_edge(self, star1_id, star2_id):
        """Bloquea una arista entre dos estrellas"""
        edge = tuple(sorted([star1_id, star2_id]))
        self.blocked_edges.add(edge)
    
    def unblock_edge(self, star1_id, star2_id):
        """Desbloquea una arista entre dos estrellas"""
        edge = tuple(sorted([star1_id, star2_id]))
        if edge in self.blocked_edges:
            self.blocked_edges.remove(edge)
    
    def is_edge_blocked(self, star1_id, star2_id):
        """Verifica si una arista está bloqueada"""
        edge = tuple(sorted([star1_id, star2_id]))
        return edge in self.blocked_edges
    
    def get_adjacent_stars(self, star_id):
        """Obtiene estrellas adyacentes no bloqueadas"""
        star = self.get_star_by_id(star_id)
        if not star:
            return []
        
        adjacent = []
        for connection in star.linked_to:
            if not self.is_edge_blocked(star_id, connection['starId']):
                adjacent.append((connection['starId'], connection['distance']))
        
        return adjacent