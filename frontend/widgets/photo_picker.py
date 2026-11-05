import os

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.popup import Popup

import theme
from widgets.icons import Icon
from widgets.labels import make_label
from widgets.rounded_button import RoundedButton
from widgets.toast import show_toast

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
MAX_SIZE = 5 * 1024 * 1024  # 5 Mo, comme sur le backend


class PhotoPicker(ButtonBehavior, BoxLayout):
    """Zone cliquable pour choisir une photo. `path` contient le fichier choisi."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(130))
        kwargs.setdefault("padding", dp(10))
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)
        self.path = None

        with self.canvas.before:
            Color(*theme.rgba(theme.WHITE))
            self._fill = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
            Color(*theme.rgba(theme.PRIMARY_LIGHT))
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                width=dp(1.2),
                dash_length=dp(6),
                dash_offset=dp(4),
            )
        self.bind(pos=self._update_shape, size=self._update_shape)
        self.bind(on_release=self.open_chooser)
        self._render()

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

    def _render(self):
        """Affiche soit l'invitation à choisir une photo, soit l'aperçu."""
        self.clear_widgets()
        if self.path:
            self.add_widget(Image(source=self.path, fit_mode="contain"))
            self.add_widget(
                make_label(
                    "Appuyer pour changer la photo",
                    sp(12),
                    theme.rgba(theme.TEXT_MUTED),
                )
            )
        else:
            self.add_widget(
                Icon("camera", icon_size=sp(34), color=theme.rgba(theme.PRIMARY))
            )
            self.add_widget(
                make_label(
                    "Ajouter une photo",
                    sp(15),
                    theme.rgba(theme.TEXT_DARK),
                    bold=True,
                )
            )
            self.add_widget(
                make_label(
                    "(Cliquer pour choisir une image)",
                    sp(12),
                    theme.rgba(theme.TEXT_MUTED),
                )
            )

    def clear(self):
        self.path = None
        self._render()

    def open_chooser(self, *args):
        chooser = FileChooserIconView(
            path=os.path.expanduser("~"),
            filters=["*.png", "*.jpg", "*.jpeg", "*.webp"],
        )
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        layout.add_widget(chooser)

        buttons = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel_button = RoundedButton(
            text="Annuler",
            bg_color=theme.rgba(theme.LAVENDER),
            color=theme.rgba(theme.TEXT_DARK),
        )
        choose_button = RoundedButton(text="Choisir")
        buttons.add_widget(cancel_button)
        buttons.add_widget(choose_button)
        layout.add_widget(buttons)

        popup = Popup(title="Choisir une photo", content=layout, size_hint=(0.96, 0.9))
        cancel_button.bind(on_release=popup.dismiss)
        choose_button.bind(on_release=lambda *args: self._choose(chooser, popup))
        popup.open()

    def _choose(self, chooser, popup):
        if not chooser.selection:
            show_toast("Sélectionnez d'abord une image.")
            return
        path = chooser.selection[0]
        if not path.lower().endswith(ALLOWED_EXTENSIONS):
            show_toast("Format accepté : JPG, PNG ou WEBP.")
            return
        if os.path.getsize(path) > MAX_SIZE:
            show_toast("Image trop lourde (5 Mo maximum).")
            return
        self.path = path
        self._render()
        popup.dismiss()