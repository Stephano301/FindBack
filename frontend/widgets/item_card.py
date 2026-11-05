from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label

import theme
from services.formatters import format_date
from widgets.card import Card
from widgets.icons import Icon
from widgets.status_badge import StatusBadge


def _single_line_label(text, font_size, color, bold=False):
    """Texte sur une seule ligne, coupé avec « … » s'il est trop long."""
    label = Label(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold,
        halign="left",
        valign="middle",
        shorten=True,
        shorten_from="right",
    )
    label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    return label


class ItemCard(ButtonBehavior, Card):
    """Carte d'annonce cliquable. `item` est un dictionnaire au format de l'API."""

    def __init__(self, item, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(88))
        kwargs.setdefault("padding", dp(8))
        kwargs.setdefault("spacing", dp(12))
        super().__init__(**kwargs)
        self.item = item
        self.add_widget(self._build_photo(item.get("photo_url")))
        self.add_widget(self._build_info(item))

    def _build_photo(self, photo_url):
        if photo_url:
            return AsyncImage(
                source=photo_url, fit_mode="cover", size_hint=(None, 1), width=dp(72)
            )
        # Sans photo : un carré lavande avec une icône d'appareil photo
        placeholder = Card(
            fill=theme.LAVENDER,
            border=None,
            radius=dp(12),
            size_hint=(None, 1),
            width=dp(72),
        )
        placeholder.add_widget(
            Icon("camera", icon_size=sp(28), color=theme.rgba(theme.PRIMARY_LIGHT))
        )
        return placeholder

    def _build_info(self, item):
        muted = theme.rgba(theme.TEXT_MUTED)

        info = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        info.bind(minimum_height=info.setter("height"))

        # Ligne 1 : titre et pastille Perdu / Trouvé
        title_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(8)
        )
        title_row.add_widget(
            _single_line_label(
                item["title"], sp(15), theme.rgba(theme.TEXT_DARK), bold=True
            )
        )
        badge = StatusBadge(item["kind"])
        badge.pos_hint = {"center_y": 0.5}
        title_row.add_widget(badge)
        info.add_widget(title_row)

        # Ligne 2 : lieu et date
        place_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(4)
        )
        place_row.add_widget(
            Icon("place", icon_size=sp(16), color=muted, size_hint_x=None, width=dp(18))
        )
        place_row.add_widget(
            _single_line_label(
                f"{item['location']}  •  {format_date(item['event_date'])}",
                sp(12),
                muted,
            )
        )
        info.add_widget(place_row)

        # On centre le bloc verticalement dans la carte
        wrapper = AnchorLayout(anchor_y="center")
        wrapper.add_widget(info)
        return wrapper