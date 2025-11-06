class Constants:
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    CANVAS_MARGIN = 50
    
    # Estados de salud del burro
    HEALTH_EXCELLENT = "Excelente"
    HEALTH_GOOD = "Buena"
    HEALTH_POOR = "Mala"
    HEALTH_DYING = "Moribundo"
    HEALTH_DEAD = "Muerto"
    
    # Colores para las constelaciones
    CONSTELLATION_COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
    ]
    
    # Factores de energía por estado de salud
    ENERGY_FACTORS = {
        HEALTH_EXCELLENT: 5,
        HEALTH_GOOD: 3,
        HEALTH_POOR: 2
    }
    
    # Tiempo máximo de estadía para comer (50%)
    MAX_EATING_TIME_RATIO = 0.5