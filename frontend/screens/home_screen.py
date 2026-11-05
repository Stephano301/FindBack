from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import theme
from services import dashboard_service
from services.session import session
from services.tasks import run_async
from widgets.card import Card, paint_background
from widgets.icons import Icon, IconButton, icon_font_kwargs, icon_text
from widgets.item_card import ItemCard
from widgets.labels import make_label
from widgets.logo import LogoWidget
from widgets.nav_drawer import NavDrawer
from widgets.rounded_button import RoundedButton
from widgets.stat_card import StatCard
from widgets.toast import show_toast
from widgets.top_bar import TopBar

# "all" = chiffres de toute l'application, "mine" = seulement mes annonces
DASHBOARD_SCOPE = "all"

# (clé de l'API, icône, couleur, légende)
STAT_DEFINITIONS = [
    ("total_lost", "warning", theme.DANGER, "Objets perdus"),
    ("total_found", "check", theme.SUCCESS, "Objets trouvés"),
    ("total_recovered", "star", theme.PRIMARY, "Récupéré"),
    ("pending_claims", "hourglass", theme.ACCENT, "En attente"),
]

# (icône, texte, nom de l'écran visé)
MENU_ENTRIES = [
    ("home", "Accueil", "home"),
    ("add", "Déclarer un objet", "declare"),
    ("list", "Toutes les annonces", "items"),
    ("label", "Mes annonces", "my_items"),
    ("send", "Mes demandes", "claims"),
    ("account_circle", "Mon profil", "profile"),
    ("logout", "Se déconnecter", "logout"),
]


class HomeScreen(Screen):
    """Accueil : salutation, statistiques et dernières annonces."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stat_cards = {}

        root = FloatLayout()
        main = BoxLayout(orientation="vertical")
        paint_background(main, theme.BACKGROUND)

        # Barre violette : menu à gauche, profil à droite
        main.add_widget(
            TopBar(
                "FindBack",
                left_icon="menu",
                right_icon="account_circle",
                on_left=self.open_menu,
                on_right=lambda: self.go("profile"),
            )
        )

        # Contenu défilant
        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(16), dp(16), dp(16), dp(90)],
            spacing=dp(16),
        )
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(self._build_banner())
        content.add_widget(self._build_stats())
        content.add_widget(self._build_section_header())

        self.items_box = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(10)
        )
        self.items_box.bind(minimum_height=self.items_box.setter("height"))
        content.add_widget(self.items_box)
        self.empty_label = make_label("", sp(14), theme.rgba(theme.TEXT_MUTED))
        content.add_widget(self.empty_label)

        scroll.add_widget(content)
        main.add_widget(scroll)
        root.add_widget(main)

        # Bouton rond « + » en bas à droite
        fab = RoundedButton(
            text=icon_text("add") or "+",
            font_size=sp(30),
            size_hint=(None, None),
            width=dp(58),
            height=dp(58),
            radius=dp(29),
            pos_hint={"right": 0.95, "y": 0.035},
            **icon_font_kwargs()
        )
        fab.bind(on_release=lambda *args: self.go("declare"))
        root.add_widget(fab)

        self.add_widget(root)

    # ---------- Construction ----------

    def _build_banner(self):
        """Carte lavande « Bonjour … ! » avec le logo."""
        banner = Card(
            fill=theme.LAVENDER,
            border=None,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(120),
            padding=dp(16),
            spacing=dp(8),
        )
        texts = BoxLayout(orientation="vertical", spacing=dp(2))
        texts.add_widget(Widget())
        self.greeting_label = make_label(
            "Bonjour !",
            sp(21),
            theme.rgba(theme.TEXT_DARK),
            bold=True,
            halign="left",
        )
        texts.add_widget(self.greeting_label)
        texts.add_widget(
            make_label(
                "Bienvenue sur FindBack.",
                sp(14),
                theme.rgba(theme.TEXT_DARK),
                halign="left",
            )
        )
        texts.add_widget(Widget())
        banner.add_widget(texts)
        banner.add_widget(LogoWidget(variant="dark", size_hint=(None, 1), width=dp(100)))
        return banner

    def _build_stats(self):
        """Les quatre cartes de statistiques."""
        grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(122))
        for key, icon_name, color, label in STAT_DEFINITIONS:
            card = StatCard(icon_name, color, label)
            self.stat_cards[key] = card
            grid.add_widget(card)
        return grid

    def _build_section_header(self):
        """Ligne « Dernières annonces ———— Voir tout → »."""
        row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(34), spacing=dp(6)
        )
        row.add_widget(
            Icon(
                "campaign",
                icon_size=sp(24),
                color=theme.rgba(theme.PRIMARY),
                size_hint_x=None,
                width=dp(28),
            )
        )
        title = make_label(
            "Dernières annonces",
            sp(17),
            theme.rgba(theme.TEXT_DARK),
            bold=True,
            halign="left",
        )
        title.pos_hint = {"center_y": 0.5}
        row.add_widget(title)

        see_all = Button(
            text="Voir tout",
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=theme.rgba(theme.PRIMARY),
            bold=True,
            font_size=sp(14),
            size_hint_x=None,
            width=dp(72),
        )
        see_all.bind(on_release=lambda *args: self.go("items"))
        row.add_widget(see_all)

        arrow = IconButton(
            "arrow_forward",
            icon_size=sp(20),
            color=theme.rgba(theme.PRIMARY),
            size_hint_x=None,
            width=dp(28),
        )
        arrow.bind(on_release=lambda *args: self.go("items"))
        row.add_widget(arrow)
        return row

    # ---------- Chargement des données depuis l'API ----------

    def on_pre_enter(self, *args):
        # Il faut être connecté pour voir l'accueil
        if not session.is_logged_in:
            Clock.schedule_once(lambda dt: self._go_to_auth(), 0)
            return
        self.greeting_label.text = f"Bonjour {session.user['first_name']} !"
        self.refresh()

    def _go_to_auth(self):
        self.manager.transition.direction = "right"
        self.manager.current = "auth"

    def refresh(self):
        run_async(
            lambda: dashboard_service.get_dashboard(DASHBOARD_SCOPE),
            on_success=self._on_dashboard_loaded,
        )

    def _on_dashboard_loaded(self, data):
        self.update_stats(data)
        self.show_items(data["latest_items"])

    def update_stats(self, stats):
        for key, card in self.stat_cards.items():
            card.set_value(stats.get(key, 0))

    def show_items(self, items):
        self.items_box.clear_widgets()
        for item in items:
            card = ItemCard(item)
            card.bind(on_release=lambda inst, i=item: self.open_item(i))
            self.items_box.add_widget(card)
        self.empty_label.text = "" if items else "Aucune annonce pour le moment."

    # ---------- Navigation ----------

    def go(self, screen_name):
        """Va vers un écran s'il existe, sinon affiche un petit message."""
        if self.manager and self.manager.has_screen(screen_name):
            self.manager.transition.direction = "left"
            self.manager.current = screen_name
        else:
            show_toast("Cet écran sera construit dans une prochaine sous-étape.")

    def open_item(self, item):
        detail = self.manager.get_screen("item_detail")
        detail.show_item(item, back_to="home")
        self.manager.transition.direction = "left"
        self.manager.current = "item_detail"

    def open_menu(self):
        NavDrawer(
            user=session.user, entries=MENU_ENTRIES, on_select=self.on_menu_select
        ).open()

    def on_menu_select(self, key):
        if key == "home":
            return
        if key == "logout":
            # L'écran de connexion efface la session en s'ouvrant
            self.manager.transition.direction = "right"
            self.manager.current = "auth"
            return
        self.go(key)