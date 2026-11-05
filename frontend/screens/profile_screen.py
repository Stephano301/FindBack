from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import theme
from services.sample_data import SAMPLE_USER
from widgets.card import Card, paint_background
from widgets.icons import Icon
from widgets.labels import make_label
from widgets.nav_drawer import MenuRow
from widgets.separator import Separator
from widgets.toast import show_toast
from widgets.top_bar import TopBar


class Pill(Label):
    """Petite pastille lavande, par exemple « Étudiant »."""

    def __init__(self, text, **kwargs):
        super().__init__(
            text=text,
            color=theme.rgba(theme.PRIMARY),
            font_size=sp(13),
            bold=True,
            size_hint=(None, None),
            **kwargs
        )
        with self.canvas.before:
            Color(*theme.rgba(theme.LAVENDER_DARK, 0.6))
            self._shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )
        self.bind(
            texture_size=self._resize, pos=self._update_shape, size=self._update_shape
        )
        self.texture_update()
        self._resize()

    def _resize(self, *args):
        self.size = (self.texture_size[0] + dp(26), self.texture_size[1] + dp(12))

    def _update_shape(self, *args):
        self._shape.pos = self.pos
        self._shape.size = self.size


class ChevronRow(MenuRow):
    """Ligne de menu avec une flèche à droite."""

    def __init__(
        self,
        icon_name,
        text,
        text_color=theme.TEXT_DARK,
        icon_color=theme.PRIMARY,
        **kwargs
    ):
        super().__init__(icon_name, text, text_color, icon_color, **kwargs)
        self.add_widget(
            Icon(
                "arrow_forward",
                icon_size=sp(20),
                color=theme.rgba(theme.TEXT_MUTED),
                size_hint_x=None,
                width=dp(24),
            )
        )


class ProfileScreen(Screen):
    """Profil de l'utilisateur connecté."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        root.add_widget(
            TopBar(
                "Mon profil",
                left_icon="arrow_back",
                right_icon="settings",
                on_left=lambda: self.go("home", "right"),
                on_right=lambda: show_toast("Les paramètres arriveront plus tard."),
            )
        )
        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        self.content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(16),
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        """Reconstruit l'écran avec les informations actuelles de l'utilisateur."""
        self.content.clear_widgets()
        self.content.add_widget(self._build_header())
        self.content.add_widget(self._build_menu())
        self.content.add_widget(self._build_logout())

    # ---------- Construction ----------

    def _build_header(self):
        user = SAMPLE_USER
        header = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(112), spacing=dp(14)
        )
        header.add_widget(
            Icon(
                "account_circle",
                icon_size=sp(84),
                color=theme.rgba(theme.PRIMARY_LIGHT),
                size_hint_x=None,
                width=dp(96),
            )
        )

        info = BoxLayout(orientation="vertical", spacing=dp(4))
        info.add_widget(Widget())
        info.add_widget(
            make_label(
                f"{user['first_name']} {user['last_name']}",
                sp(19),
                theme.rgba(theme.TEXT_DARK),
                bold=True,
                halign="left",
            )
        )
        info.add_widget(
            make_label(
                user["email"], sp(13), theme.rgba(theme.TEXT_MUTED), halign="left"
            )
        )
        pill_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(30)
        )
        pill = Pill(user["occupation"])
        pill.pos_hint = {"center_y": 0.5}
        pill_row.add_widget(pill)
        pill_row.add_widget(Widget())
        info.add_widget(pill_row)
        info.add_widget(Widget())
        header.add_widget(info)
        return header

    def _build_menu(self):
        entries = [
            ("list", "Mes annonces", "my_items"),
            ("send", "Mes demandes", "claims"),
            ("edit", "Modifier mon profil", "edit_profile"),
        ]
        if SAMPLE_USER.get("is_admin"):
            entries.append(("settings", "Administration", "admin"))

        card = Card(orientation="vertical", size_hint_y=None, padding=dp(4))
        card.bind(minimum_height=card.setter("height"))
        for index, (icon_name, label, screen_name) in enumerate(entries):
            if index > 0:
                card.add_widget(Separator())
            row = ChevronRow(icon_name, label)
            row.bind(on_release=lambda inst, name=screen_name: self.go(name))
            card.add_widget(row)
        return card

    def _build_logout(self):
        card = Card(orientation="vertical", size_hint_y=None, padding=dp(4))
        card.bind(minimum_height=card.setter("height"))
        row = ChevronRow(
            "logout",
            "Se déconnecter",
            text_color=theme.DANGER,
            icon_color=theme.DANGER,
        )
        row.bind(on_release=lambda *args: self.go("auth", "right"))
        card.add_widget(row)
        return card

    # ---------- Navigation ----------

    def go(self, screen_name, direction="left"):
        if self.manager.has_screen(screen_name):
            self.manager.transition.direction = direction
            self.manager.current = screen_name
        else:
            show_toast("Cet écran n'est pas encore disponible.")