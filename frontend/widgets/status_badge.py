from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.label import Label

import theme

# type -> (texte, couleur du fond, couleur du texte)
BADGE_STYLES = {
    "lost": ("Perdu", "#FDE2E4", "#E5484D"),
    "found": ("Trouvé", "#DCF5E7", "#1F9D57"),
    "pending": ("En attente de récupération", "#FDF0D5", "#B7791F"),
    "recovered": ("Récupéré", "#DCF5E7", "#1F9D57"),
}


class StatusBadge(Label):
    """Petite pastille arrondie. kind : lost, found, pending ou recovered."""

    def __init__(self, kind, text=None, **kwargs):
        label, background, foreground = BADGE_STYLES[kind]
        super().__init__(
            text=text or label,
            color=theme.rgba(foreground),
            font_size=sp(11),
            bold=True,
            size_hint=(None, None),
            **kwargs
        )
        with self.canvas.before:
            Color(*theme.rgba(background))
            self._shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(10)]
            )
        self.bind(
            texture_size=self._resize, pos=self._update_shape, size=self._update_shape
        )
        self.texture_update()
        self._resize()

    def _resize(self, *args):
        self.size = (self.texture_size[0] + dp(18), self.texture_size[1] + dp(8))

    def _update_shape(self, *args):
        self._shape.pos = self.pos
        self._shape.size = self.size