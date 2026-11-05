from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout

import theme
from widgets.rounded_button import RoundedButton


class SegmentedTabs(BoxLayout):
    """Boutons côte à côte dont un seul est actif. Envoie l'événement on_select."""

    __events__ = ("on_select",)

    def __init__(self, options, selected=None, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        kwargs.setdefault("padding", dp(4))
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)

        self.selected = None
        self._buttons = {}

        with self.canvas.before:
            Color(*theme.rgba(theme.LAVENDER))
            self._background = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )
        self.bind(pos=self._update_background, size=self._update_background)

        # options = [("login", "Connexion"), ("register", "Inscription")]
        for key, label in options:
            button = RoundedButton(
                text=label, radius=dp(11), size_hint_y=1, font_size=sp(14)
            )
            button.bind(on_release=lambda inst, k=key: self.select(k))
            self._buttons[key] = button
            self.add_widget(button)

        self.select(selected or options[0][0], notify=False)

    def _update_background(self, *args):
        self._background.pos = self.pos
        self._background.size = self.size

    def select(self, key, notify=True):
        """Active un onglet. notify=False évite d'envoyer l'événement."""
        self.selected = key
        for k, button in self._buttons.items():
            if k == key:
                button.bg_color = theme.rgba(theme.PRIMARY)
                button.color = theme.rgba(theme.WHITE)
            else:
                button.bg_color = (0, 0, 0, 0)
                button.color = theme.rgba(theme.TEXT_DARK)
        if notify:
            self.dispatch("on_select", key)

    def on_select(self, key):
        pass
