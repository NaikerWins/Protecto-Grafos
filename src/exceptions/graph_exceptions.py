class GraphError(Exception):
    # Base exception for graph errors
    pass

class StarNotFoundError(GraphError):
    # Exception when a star is not found
    pass

class InvalidRouteError(GraphError):
    # Exception for invalid routes
    pass

class InsufficientResourcesError(GraphError):
    # Exception when there are insufficient resources
    pass