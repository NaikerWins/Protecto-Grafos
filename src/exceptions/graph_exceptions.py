class GraphError(Exception):
    """Excepción base para errores del grafo"""
    pass

class StarNotFoundError(GraphError):
    """Excepción cuando no se encuentra una estrella"""
    pass

class InvalidRouteError(GraphError):
    """Excepción para rutas inválidas"""
    pass

class InsufficientResourcesError(GraphError):
    """Excepción cuando no hay suficientes recursos"""
    pass