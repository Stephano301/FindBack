from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget

import theme


class PageDots(Widget):
    """Points indiquant la page courante d'un carrousel."""

    count = NumericProperty(3)
    index = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            pos=self._draw, size=self._draw, count=self._draw, index=self._draw
        )
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        dot = dp(9)
        gap = dp(10)
        total_width = self.count * dot + (self.count - 1) * gap
        x = self.center_x - total_width / 2
        y = self.center_y - dot / 2

        with self.canvas:
            for i in range(int(self.count)):
                active = i == int(round(self.index))
                color = theme.PRIMARY if active else theme.LAVENDER_DARK
                Color(*theme.rgba(color))
                Ellipse(pos=(x + i * (dot + gap), y), size=(dot, dot))