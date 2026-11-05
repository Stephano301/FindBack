from kivy.utils import get_color_from_hex

# ---------- Couleurs (relevées sur la maquette) ----------
PRIMARY = "#4F3CC9"        # violet principal (barres, boutons)
PRIMARY_DARK = "#3B2BA6"   # violet foncé
PRIMARY_LIGHT = "#8B7CF6"  # violet clair
LAVENDER = "#EEEAFE"       # lavande très claire (cartes, champs)
LAVENDER_DARK = "#C9C1F7"  # lavande plus soutenue
BACKGROUND = "#F6F4FF"     # fond des écrans
ACCENT = "#F5A524"         # orange du logo ("Back")
WHITE = "#FFFFFF"
TEXT_DARK = "#1E1B4B"      # texte principal
TEXT_MUTED = "#6B6B8D"     # texte secondaire
DANGER = "#E5484D"         # rouge (perdu, déconnexion)
SUCCESS = "#2FB86B"        # vert (trouvé)

# ---------- Fenêtre (format téléphone) ----------
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 700


def rgba(hex_code, alpha=1.0):
    """Convertit '#4F3CC9' en couleur Kivy (rouge, vert, bleu, opacité)."""
    r, g, b, _ = get_color_from_hex(hex_code)
    return (r, g, b, alpha)