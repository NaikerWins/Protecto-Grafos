class Constants:
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    CANVAS_MARGIN = 50
    
    HEALTH_EXCELLENT = "Excelente"
    HEALTH_GOOD = "Buena"
    HEALTH_POOR = "Mala"
    HEALTH_DYING = "Moribundo"
    HEALTH_DEAD = "Muerto"
    
    CONSTELLATION_COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
    ]
    
    ENERGY_FACTORS = {
        HEALTH_EXCELLENT: 5,
        HEALTH_GOOD: 3,
        HEALTH_POOR: 2,
        HEALTH_DYING: 1,
        HEALTH_DEAD: 0
    }
    
    MAX_EATING_TIME_RATIO = 0.5
    

    HEALTH_ENERGY_RATIOS = {
        HEALTH_EXCELLENT: 1.0,
        HEALTH_GOOD: 0.75,
        HEALTH_POOR: 0.5,
        HEALTH_DYING: 0.25,
        HEALTH_DEAD: 0.0
    }
    
    DEATH_SOUND = "💀 ¡El burro ha muerto! 💀"