class FileLoadError(Exception):
    """Excepción para errores de carga de archivos"""
    pass

class InvalidJSONError(Exception):
    """Excepción para JSON inválido"""
    pass

class ConstellationNotFoundError(Exception):
    """Excepción cuando no se encuentra una constelación"""
    pass