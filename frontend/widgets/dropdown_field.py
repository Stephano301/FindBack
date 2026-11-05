from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner, SpinnerOption

import theme
from widgets.icons import Icon


class DropdownOption(SpinnerOption):
    """Une ligne de la liste déroulante."""

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", theme.rgba(theme.WHITE))
        kwargs.setdefault("color", theme.rgba(theme.TEXT_DARK))
        kwargs.setdefault("font_size", sp(15))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(44))
        super().__init__(**kwargs)


class DropdownField(BoxLayout):
    """Champ à liste déroulante, avec une icône à gauche."""

    def __init__(self, icon_name, hint_text, values=None, fill=theme.WHITE, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("padding", [dp(14), 0, dp(6), 0])
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        self._hint = hint_text
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

        self.add_widget(
            Icon(
                icon_name,
                icon_size=sp(22),
                color=theme.rgba(theme.PRIMARY),
                size_hint_x=None,
                width=dp(28),
            )
        )

        self.spinner = Spinner(
            text=hint_text,
            values=values or [],
            option_cls=DropdownOption,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=theme.rgba(theme.TEXT_MUTED),
            font_size=sp(15),
            halign="left",
            valign="middle",
        )
        self.spinner.bind(
            size=lambda inst, size: setattr(inst, "text_size", size),
            text=self._on_text_changed,
        )
        self.add_widget(self.spinner)

    @property
    def selected_value(self):
        """Le choix fait, ou None si rien n'est choisi."""
        return None if self.spinner.text == self._hint else self.spinner.text

    def set_values(self, values):
        self.spinner.values = values

    def reset(self):
        self.spinner.text = self._hint

    def set_error(self, has_error):
        self._has_error = has_error
        self._border_color.rgba = theme.rgba(
            theme.DANGER if has_error else theme.LAVENDER_DARK
        )

    def _on_text_changed(self, instance, text):
        chosen = text != self._hint
        instance.color = theme.rgba(theme.TEXT_DARK if chosen else theme.TEXT_MUTED)
        if chosen:
            self.set_error(False)

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