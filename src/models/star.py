class Star:
    def __init__(self, star_id, label, coordinates, radius, time_to_eat, 
                 amount_of_energy, hypergiant=False, linked_to=None):
        self.id = star_id
        self.label = label
        self.coordinates = coordinates  # {'x': x, 'y': y}
        self.radius = radius
        self.time_to_eat = time_to_eat
        self.amount_of_energy = amount_of_energy
        self.hypergiant = hypergiant
        self.linked_to = linked_to if linked_to else []
        self.visited = False
        self.blocked = False
    
    def add_connection(self, star_id, distance):
        """Añade una conexión a otra estrella"""
        self.linked_to.append({'starId': star_id, 'distance': distance})
    
    def remove_connection(self, star_id):
        """Elimina una conexión a otra estrella"""
        self.linked_to = [conn for conn in self.linked_to if conn['starId'] != star_id]
    
    def get_connections(self):
        """Retorna todas las conexiones de la estrella"""
        return self.linked_to
    
    def __str__(self):
        return f"Star {self.id} ({self.label}) at ({self.coordinates['x']}, {self.coordinates['y']})"
    
    def __repr__(self):
        return self.__str__()