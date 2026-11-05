from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.widget import Widget

import theme


class Separator(Widget):
    """Un trait horizontal fin."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(1))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*theme.rgba(theme.LAVENDER_DARK))
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size