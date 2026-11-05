from kivy.metrics import dp
from kivy.uix.label import Label


def make_label(text, font_size, color, bold=False, markup=False, halign="center"):
    """Crée un texte qui passe à la ligne et dont la hauteur s'adapte au contenu."""
    label = Label(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold,
        markup=markup,
        halign=halign,
        valign="middle",
        size_hint_y=None,
    )
    label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
    label.bind(
        texture_size=lambda inst, size: setattr(inst, "height", size[1] + dp(6))
    )
    return label
