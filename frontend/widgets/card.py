from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

import theme


def paint_background(widget, hex_color):
    """Peint un fond uni derrière un widget (et le garde à la bonne taille)."""
    with widget.canvas.before:
        Color(*theme.rgba(hex_color))
        rectangle = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(
        pos=lambda inst, value: setattr(rectangle, "pos", value),
        size=lambda inst, value: setattr(rectangle, "size", value),
    )


class Card(BoxLayout):
    """Conteneur à coins arrondis, avec un fond et une bordure fine."""

    def __init__(
        self, fill=theme.WHITE, border=theme.LAVENDER_DARK, radius=dp(16), **kwargs
    ):
        super().__init__(**kwargs)
        self._radius = radius
        with self.canvas.before:
            Color(*theme.rgba(fill))
            self._fill = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[radius]
            )
            # Sans bordure : on dessine le trait de la même couleur que le fond
            Color(*theme.rgba(border or fill))
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, radius),
                width=dp(1),
            )
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *args):
        self._fill.pos = self.pos
        self._fill.size = self.size
        self._border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self._radius,
        )