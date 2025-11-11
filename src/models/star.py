class Star:
    def __init__(self, star_id, label, coordinates, radius, time_to_eat, 
                 amount_of_energy, hypergiant=False, linked_to=None, research_effect=0, galaxy="Vía Láctea"):
        self.id = str(star_id)
        self.label = label
        self.coordinates = coordinates
        self.radius = radius
        self.time_to_eat = time_to_eat
        self.amount_of_energy = amount_of_energy
        self.research_effect = research_effect 
        self.hypergiant = hypergiant
        self.linked_to = linked_to if linked_to else []
        self.galaxy = galaxy
        self.visited = False
        self.blocked = False
    
    def add_connection(self, star_id, distance):
        self.linked_to.append({'starId': str(star_id), 'distance': distance})
    
    def remove_connection(self, star_id):
        star_id_str = str(star_id)
        self.linked_to = [conn for conn in self.linked_to if str(conn['starId']) != star_id_str]
    
    def get_connections(self):
        return self.linked_to
    
    def __str__(self):
        return f"Star {self.id} ({self.label}) at ({self.coordinates['x']}, {self.coordinates['y']}) - Galaxy: {self.galaxy}"
    
    def __repr__(self):
        return self.__str__()