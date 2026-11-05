from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

import theme
from widgets.icons import Icon


class TextArea(BoxLayout):
    """Champ de saisie multiligne arrondi, avec une icône en haut à gauche."""

    def __init__(
        self, hint_text, icon_name="list", height=dp(110), fill=theme.WHITE, **kwargs
    ):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", [dp(14), dp(8), dp(10), dp(8)])
        kwargs.setdefault("spacing", dp(8))
        super().__init__(height=height, **kwargs)
        self._has_error = False

        with self.canvas.before:
            Color(*theme.rgba(fill))
            self._fill = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
            self._border_color = Color(*theme.rgba(theme.LAVENDER_DARK))
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=dp(1.1),
            )
        self.bind(pos=self._update_shape, size=self._update_shape)

        # Icône alignée en haut
        icon_holder = AnchorLayout(anchor_y="top", size_hint_x=None, width=dp(28))
        icon_holder.add_widget(
            Icon(
                icon_name,
                icon_size=sp(22),
                color=theme.rgba(theme.PRIMARY),
                size_hint=(None, None),
                size=(dp(28), dp(34)),
            )
        )
        self.add_widget(icon_holder)

        self.input = TextInput(
            hint_text=hint_text,
            multiline=True,
            write_tab=False,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=theme.rgba(theme.TEXT_DARK),
            hint_text_color=theme.rgba(theme.TEXT_MUTED, 0.9),
            cursor_color=theme.rgba(theme.PRIMARY),
            font_size=sp(15),
            padding=[0, dp(8), 0, dp(8)],
        )
        self.input.bind(
            focus=self._refresh_border, text=lambda *args: self.set_error(False)
        )
        self.add_widget(self.input)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, value):
        self.input.text = value

    def clear(self):
        self.input.text = ""

    def set_error(self, has_error):
        self._has_error = has_error
        self._refresh_border()

    def _update_shape(self, *args):
        self._fill.pos = self.pos
        self._fill.size = self.size
        self._border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(12),
        )

    def _refresh_border(self, *args):
        if self._has_error:
            color = theme.DANGER
        elif self.input.focus:
            color = theme.PRIMARY
        else:
            color = theme.LAVENDER_DARK
        self._border_color.rgba = theme.rgba(color)