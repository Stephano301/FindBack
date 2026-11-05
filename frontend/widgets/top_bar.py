from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

import theme
from widgets.card import paint_background
from widgets.icons import IconButton


class TopBar(BoxLayout):
    """Barre violette en haut d'un écran : icône à gauche, titre, icône à droite."""

    def __init__(
        self,
        title,
        left_icon=None,
        right_icon=None,
        on_left=None,
        on_right=None,
        **kwargs
    ):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(58))
        kwargs.setdefault("padding", [dp(6), 0, dp(6), 0])
        kwargs.setdefault("spacing", dp(6))
        super().__init__(**kwargs)
        paint_background(self, theme.PRIMARY)

        self.add_widget(self._make_button(left_icon, on_left))
        self.title_label = Label(
            text=title,
            bold=True,
            font_size=sp(19),
            color=theme.rgba(theme.WHITE),
            halign="left",
            valign="middle",
        )
        self.title_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.add_widget(self.title_label)
        self.add_widget(self._make_button(right_icon, on_right))

    def _make_button(self, icon_name, callback):
        # Sans icône : un espace vide garde le titre bien placé
        if not icon_name:
            return Widget(size_hint_x=None, width=dp(48))
        button = IconButton(
            icon_name,
            icon_size=sp(26),
            color=theme.rgba(theme.WHITE),
            size_hint_x=None,
            width=dp(48),
        )
        if callback:
            button.bind(on_release=lambda *args: callback())
        return button

    def set_title(self, title):
        self.title_label.text = title