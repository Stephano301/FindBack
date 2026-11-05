from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget

import theme
from widgets.card import paint_background
from widgets.icons import Icon
from widgets.labels import make_label


class MenuRow(ButtonBehavior, BoxLayout):
    """Une ligne du menu : une icône et un texte."""

    def __init__(self, icon_name, text, text_color, icon_color, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(52))
        kwargs.setdefault("padding", [dp(20), 0, dp(12), 0])
        kwargs.setdefault("spacing", dp(16))
        super().__init__(**kwargs)
        self.add_widget(
            Icon(
                icon_name,
                icon_size=sp(22),
                color=theme.rgba(icon_color),
                size_hint_x=None,
                width=dp(28),
            )
        )
        label = Label(
            text=text,
            font_size=sp(15),
            color=theme.rgba(text_color),
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.add_widget(label)


class NavDrawer(ModalView):
    """Menu latéral. entries = [(icône, texte, clé), ...]. Appelle on_select(clé)."""

    def __init__(self, user, entries, on_select, **kwargs):
        super().__init__(
            size_hint=(0.78, 1),
            anchor_x="left",
            auto_dismiss=True,
            background="",
            background_color=(0, 0, 0, 0),
            overlay_color=(0, 0, 0, 0.45),
            **kwargs
        )
        self._on_select = on_select

        panel = BoxLayout(orientation="vertical")
        paint_background(panel, theme.WHITE)

        # En-tête violet : avatar, nom et e-mail
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(170),
            padding=dp(20),
            spacing=dp(4),
        )
        paint_background(header, theme.PRIMARY)
        header.add_widget(
            Icon(
                "account_circle",
                icon_size=sp(56),
                color=theme.rgba(theme.WHITE),
                size_hint=(None, None),
                size=(dp(64), dp(64)),
            )
        )
        header.add_widget(
            make_label(
                f"{user['first_name']} {user['last_name']}",
                sp(17),
                theme.rgba(theme.WHITE),
                bold=True,
                halign="left",
            )
        )
        header.add_widget(
            make_label(user["email"], sp(12), theme.rgba(theme.LAVENDER), halign="left")
        )
        panel.add_widget(header)

        # Les lignes du menu
        for icon_name, label, key in entries:
            is_logout = key == "logout"
            if is_logout:
                panel.add_widget(Widget())  # pousse « Se déconnecter » en bas
            row = MenuRow(
                icon_name,
                label,
                text_color=theme.DANGER if is_logout else theme.TEXT_DARK,
                icon_color=theme.DANGER if is_logout else theme.PRIMARY,
            )
            row.bind(on_release=lambda inst, k=key: self._choose(k))
            panel.add_widget(row)
        panel.add_widget(Widget(size_hint_y=None, height=dp(12)))

        self.add_widget(panel)

    def _choose(self, key):
        self.dismiss()
        self._on_select(key)