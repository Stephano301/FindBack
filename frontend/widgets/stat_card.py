from kivy.graphics import Color, Ellipse
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label

import theme
from widgets.card import Card
from widgets.icons import Icon


class IconCircle(AnchorLayout):
    """Un disque coloré avec une icône blanche au centre."""

    def __init__(self, icon_name, color, diameter=dp(40), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (diameter, diameter))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*theme.rgba(color))
            self._circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update_shape, size=self._update_shape)
        self.add_widget(
            Icon(icon_name, icon_size=sp(22), color=theme.rgba(theme.WHITE))
        )

    def _update_shape(self, *args):
        self._circle.pos = self.pos
        self._circle.size = self.size


class StatCard(Card):
    """Carte avec une icône, un nombre et une légende."""

    def __init__(self, icon_name, color, label, value=0, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", [dp(4), dp(10), dp(4), dp(6)])
        kwargs.setdefault("spacing", dp(2))
        super().__init__(**kwargs)

        self.add_widget(IconCircle(icon_name, color, pos_hint={"center_x": 0.5}))

        self.value_label = Label(
            text=str(value),
            bold=True,
            font_size=sp(22),
            color=theme.rgba(color),
            size_hint_y=None,
            height=dp(30),
        )
        self.add_widget(self.value_label)

        caption = Label(
            text=label,
            font_size=sp(11),
            color=theme.rgba(theme.TEXT_MUTED),
            halign="center",
            valign="top",
            size_hint_y=None,
            height=dp(30),
        )
        caption.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        self.add_widget(caption)

    def set_value(self, value):
        self.value_label.text = str(value)