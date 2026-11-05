from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

import theme
from widgets.icons import Icon, IconButton


class IconTextInput(BoxLayout):
    """Champ de saisie arrondi avec icône ; bouton œil si c'est un mot de passe."""

    def __init__(
        self,
        icon_name,
        hint_text,
        password=False,
        text="",
        fill=theme.BACKGROUND,
        **kwargs
    ):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("padding", [dp(14), 0, dp(6), 0])
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)

        self._has_error = False

        # Fond arrondi et bordure
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

        # Icône de gauche
        self.add_widget(
            Icon(
                icon_name,
                icon_size=sp(22),
                color=theme.rgba(theme.PRIMARY),
                size_hint_x=None,
                width=dp(28),
            )
        )

        # Zone de saisie
        self.input = TextInput(
            text=text,
            hint_text=hint_text,
            password=password,
            multiline=False,
            write_tab=False,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=theme.rgba(theme.TEXT_DARK),
            hint_text_color=theme.rgba(theme.TEXT_MUTED, 0.9),
            cursor_color=theme.rgba(theme.PRIMARY),
            font_size=sp(15),
        )
        self.input.bind(
            height=self._center_text,
            line_height=self._center_text,
            focus=self._refresh_border,
            text=lambda *args: self.set_error(False),
        )
        self.add_widget(self.input)

        # Œil pour afficher / masquer le mot de passe
        if password:
            self.eye = IconButton(
                "visibility_off", size_hint_x=None, width=dp(40)
            )
            self.eye.bind(on_release=self._toggle_password)
            self.add_widget(self.eye)

        self._center_text()

    # ----- Valeur du champ -----
    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, value):
        self.input.text = value

    def clear(self):
        self.input.text = ""

    def set_error(self, has_error):
        """Met la bordure en rouge (ou la remet normale)."""
        self._has_error = has_error
        self._refresh_border()

    # ----- Fonctions internes -----
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

    def _center_text(self, *args):
        """Centre le texte verticalement dans le champ."""
        padding = max(0, (self.input.height - self.input.line_height) / 2)
        self.input.padding = [0, padding, 0, padding]

    def _refresh_border(self, *args):
        if self._has_error:
            color = theme.DANGER
        elif self.input.focus:
            color = theme.PRIMARY
        else:
            color = theme.LAVENDER_DARK
        self._border_color.rgba = theme.rgba(color)

    def _toggle_password(self, *args):
        self.input.password = not self.input.password
        self.eye.set_icon("visibility_off" if self.input.password else "visibility")