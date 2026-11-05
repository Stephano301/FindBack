from pathlib import Path

from kivy.metrics import sp
from kivy.uix.button import Button
from kivy.uix.label import Label

import theme

# Chemin de la police d'icônes (frontend/assets/fonts/)
FONT_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "fonts"
    / "MaterialIcons-Regular.ttf"
)
FONT_AVAILABLE = FONT_PATH.exists()

# Nom de l'icône -> caractère correspondant dans la police Material Icons
ICONS = {
    "email": "\ue0be",
    "lock": "\ue897",
    "visibility": "\ue8f4",
    "visibility_off": "\ue8f5",
    "person": "\ue7fd",
    "account_circle": "\ue853",
    "home": "\ue88a",
    "search": "\ue8b6",
    "settings": "\ue8b8",
    "arrow_back": "\ue5c4",
    "arrow_forward": "\ue5c8",
    "menu": "\ue5d2",
    "place": "\ue55f",
    "event": "\ue878",
    "camera": "\ue412",
    "send": "\ue163",
    "check": "\ue86c",
    "warning": "\ue002",
    "hourglass": "\ue88b",
    "star": "\ue838",
    "logout": "\ue879",
    "edit": "\ue3c9",
    "share": "\ue80d",
    "add": "\ue145",
    "label": "\ue892",
    "list": "\ue896",
    "campaign": "\ue7f1",
}


def icon_text(name):
    """Retourne le caractère de l'icône (ou rien si la police est absente)."""
    return ICONS.get(name, "") if FONT_AVAILABLE else ""


def icon_font_kwargs():
    """À passer à un widget pour qu'il affiche du texte avec la police d'icônes."""
    return {"font_name": str(FONT_PATH)} if FONT_AVAILABLE else {}


class Icon(Label):
    """Une icône affichée comme un texte."""

    def __init__(self, name, icon_size=sp(22), color=None, **kwargs):
        kwargs.setdefault("font_size", icon_size)
        kwargs.setdefault("color", color or theme.rgba(theme.PRIMARY))
        if FONT_AVAILABLE:
            kwargs["font_name"] = str(FONT_PATH)
        super().__init__(text=icon_text(name), **kwargs)


class IconButton(Button):
    """Un bouton transparent qui affiche une icône."""

    def __init__(self, name, icon_size=sp(22), color=None, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("font_size", icon_size)
        kwargs.setdefault("color", color or theme.rgba(theme.TEXT_MUTED))
        if FONT_AVAILABLE:
            kwargs["font_name"] = str(FONT_PATH)
        super().__init__(text=icon_text(name), **kwargs)

    def set_icon(self, name):
        self.text = icon_text(name)