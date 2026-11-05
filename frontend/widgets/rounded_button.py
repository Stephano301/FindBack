from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.button import Button

import theme


class RoundedButton(Button):
    """Bouton violet à coins arrondis."""

    bg_color = ColorProperty(theme.rgba(theme.PRIMARY))
    radius = NumericProperty(dp(14))

    def __init__(self, **kwargs):
        # On retire le fond par défaut de Kivy pour dessiner le nôtre
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", theme.rgba(theme.WHITE))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", sp(16))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )
        self.bind(
            pos=self._update_shape,
            size=self._update_shape,
            bg_color=self._update_shape,
            radius=self._update_shape,
        )

    def _update_shape(self, *args):
        self._color.rgba = self.bg_color
        self._shape.pos = self.pos
        self._shape.size = self.size
        self._shape.radius = [self.radius]

    # Petit effet : le bouton s'éclaircit quand on appuie dessus
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            self.opacity = 0.8
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.opacity = 1
        return super().on_touch_up(touch)