"""
Configuration centralisée des couleurs pour le thème rouge bordeaux, noir et blanc
"""

# Couleurs principales du thème rouge bordeaux
THEME_COLORS = {
    # Rouge bordeaux (couleurs principales)
    "primary": "#800020",           # Rouge bordeaux principal
    "primary_light": "#A52A2A",     # Rouge bordeaux clair  
    "primary_dark": "#400010",      # Rouge bordeaux foncé
    "primary_accent": "#B22222",    # Rouge accent
    
    # Couleurs de fond
    "background": "#000000",        # Noir pur
    "surface": "#0a0a0a",          # Gris très foncé
    "surface_light": "#0d0d0d",    # Gris foncé
    "surface_variant": "#1a1a1a",   # Gris moyen foncé
    
    # Couleurs de texte
    "text_primary": "#ffffff",      # Blanc pur
    "text_secondary": "#cccccc",    # Gris clair
    "text_disabled": "#666666",     # Gris moyen
    "text_hint": "#999999",         # Gris
    
    # Couleurs de bordure
    "border": "#1a1a1a",           # Gris foncé
    "border_light": "#333333",      # Gris moyen
    "border_focus": "#800020",      # Rouge bordeaux (focus)
    
    # Couleurs sémantiques (conservées)
    "success": "#00cc44",          # Vert succès
    "success_light": "#00ff55",    # Vert clair
    "warning": "#ff9800",          # Orange avertissement  
    "warning_light": "#ffb84d",    # Orange clair
    "error": "#ff3333",            # Rouge erreur
    "error_light": "#ff5555",      # Rouge erreur clair
    "info": "#B22222",             # Rouge info (au lieu du bleu)
    
    # Couleurs spéciales
    "transparent": "transparent",
    "shadow": "rgba(0, 0, 0, 0.3)",
    "overlay": "rgba(0, 0, 0, 0.5)",
}

# Gradients pour les effets visuels
GRADIENTS = {
    "header": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #220000, stop:1 #000000)",
    "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #A52A2A, stop:1 #800020)",
    "progress": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #800020, stop:1 #B22222)",
    "success": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00ff55, stop:1 #00cc44)",
    "card": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05))",
}

# Couleurs par fonction dans l'application
FUNCTIONAL_COLORS = {
    # États des étapes de navigation
    "step_active": THEME_COLORS["primary"],
    "step_completed": THEME_COLORS["success"],
    "step_inactive": THEME_COLORS["surface_variant"],
    
    # Types d'anomalies
    "anomaly_profile": THEME_COLORS["primary_light"],      # Changement profil
    "anomaly_direction": THEME_COLORS["primary"],          # Changement direction  
    "anomaly_non_rh": THEME_COLORS["error"],              # Compte non RH
    "anomaly_inactive": THEME_COLORS["primary_accent"],    # Compte inactif
    "anomaly_harmonized": THEME_COLORS["success"],         # Harmonisation
    
    # Types de décisions
    "decision_modify": THEME_COLORS["primary"],           # Modifier
    "decision_keep": THEME_COLORS["success"],             # Conserver  
    "decision_disable": THEME_COLORS["error"],            # Désactiver
    
    # Statistiques
    "stat_total": THEME_COLORS["primary_accent"],
    "stat_anomalies": THEME_COLORS["warning"],
    "stat_to_verify": THEME_COLORS["primary"],
    "stat_auto": THEME_COLORS["primary_light"],
    "stat_valid": THEME_COLORS["success"],
}

# Mapping des anciennes couleurs bleues vers les nouvelles couleurs rouges
COLOR_MAPPING = {
    # Couleurs principales bleues -> rouges bordeaux
    "#0066cc": THEME_COLORS["primary"],
    "#0080ff": THEME_COLORS["primary_light"], 
    "#0099ff": THEME_COLORS["primary_accent"],
    "#2196F3": THEME_COLORS["primary_accent"],
    "#1976d2": THEME_COLORS["primary"],
    "#003366": THEME_COLORS["primary_dark"],
    
    # Couleurs spéciales préservées
    "#4CAF50": THEME_COLORS["success"],
    "#00cc44": THEME_COLORS["success"],
    "#00ff55": THEME_COLORS["success_light"],
    "#FF9800": THEME_COLORS["warning"],
    "#ff9900": THEME_COLORS["warning"],
    "#F44336": THEME_COLORS["error"],
    "#ff3333": THEME_COLORS["error"],
    "#9C27B0": "#9900cc",  # Violet conservé
}

# Couleurs pour les widgets de statistiques (format sans #)
STAT_COLORS_HEX = {
    "red": "800020",        # Rouge bordeaux principal
    "burgundy": "A52A2A",   # Rouge bordeaux clair
    "accent": "B22222",     # Rouge accent  
    "green": "00cc44",      # Vert succès
    "orange": "ff9900",     # Orange avertissement
    "purple": "9900cc",     # Violet
    "error": "ff3333",      # Rouge erreur
}

def get_color(color_key):
    """
    Récupérer une couleur par sa clé
    
    Args:
        color_key (str): Clé de la couleur dans THEME_COLORS ou FUNCTIONAL_COLORS
    
    Returns:
        str: Code couleur hexadécimal
    """
    if color_key in THEME_COLORS:
        return THEME_COLORS[color_key]
    elif color_key in FUNCTIONAL_COLORS:
        return FUNCTIONAL_COLORS[color_key]
    else:
        return THEME_COLORS["primary"]  # Couleur par défaut

def get_gradient(gradient_key):
    """
    Récupérer un gradient par sa clé
    
    Args:
        gradient_key (str): Clé du gradient dans GRADIENTS
    
    Returns:
        str: Définition CSS du gradient
    """
    return GRADIENTS.get(gradient_key, GRADIENTS["button_primary"])

def map_old_color(old_color):
    """
    Mapper une ancienne couleur bleue vers la nouvelle couleur rouge bordeaux
    
    Args:
        old_color (str): Ancienne couleur (format #rrggbb)
    
    Returns:
        str: Nouvelle couleur mappée
    """
    return COLOR_MAPPING.get(old_color, old_color)

# Export des couleurs les plus utilisées pour un accès facile
PRIMARY = THEME_COLORS["primary"]
PRIMARY_LIGHT = THEME_COLORS["primary_light"]
PRIMARY_DARK = THEME_COLORS["primary_dark"]
ACCENT = THEME_COLORS["primary_accent"]
BACKGROUND = THEME_COLORS["background"]
SURFACE = THEME_COLORS["surface"]
TEXT = THEME_COLORS["text_primary"]
SUCCESS = THEME_COLORS["success"]
WARNING = THEME_COLORS["warning"]
ERROR = THEME_COLORS["error"]