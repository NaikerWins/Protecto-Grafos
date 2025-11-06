class Constellation:
    def __init__(self, name):
        self.name = name
        self.stars = []
        self.color = None
    
    def add_star(self, star):
        """Añade una estrella a la constelación"""
        self.stars.append(star)
    
    def get_star_by_id(self, star_id):
        """Busca una estrella por su ID"""
        for star in self.stars:
            if star.id == star_id:
                return star
        return None
    
    def get_all_stars(self):
        """Retorna todas las estrellas de la constelación"""
        return self.stars
    
    def get_hypergiant_stars(self):
        """Retorna las estrellas hipergigantes de la constelación"""
        return [star for star in self.stars if star.hypergiant]
    
    def __str__(self):
        return f"Constellation {self.name} with {len(self.stars)} stars"
    
    def __repr__(self):
        return self.__str__()