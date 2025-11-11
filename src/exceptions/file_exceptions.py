class FileLoadError(Exception):
    # Exception for file upload errors
    pass

class InvalidJSONError(Exception):
    # Exception for invalid JSON
    pass

class ConstellationNotFoundError(Exception):
    # Exception when a constellation is not found
    pass