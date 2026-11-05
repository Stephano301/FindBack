from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import theme
from services import category_service, item_service
from services.tasks import run_async
from widgets.card import paint_background
from widgets.dropdown_field import DropdownField
from widgets.icon_text_input import IconTextInput
from widgets.item_card import ItemCard
from widgets.labels import make_label
from widgets.segmented_tabs import SegmentedTabs
from widgets.top_bar import TopBar


class BaseListScreen(Screen):
    """Base commune : barre du haut, zone de contrôles, liste d'annonces."""

    title = "Annonces"
    empty_text = "Aucune annonce."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._request_id = 0  # sert à ignorer les réponses devenues périmées
        self._refresh_event = None

        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        root.add_widget(
            TopBar(
                self.title,
                left_icon="arrow_back",
                right_icon="home",
                on_left=self.go_home,
                on_right=self.go_home,
            )
        )

        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        self.content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(12),
        )
        self.content.bind(minimum_height=self.content.setter("height"))

        self.build_controls(self.content)

        self.items_box = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(10)
        )
        self.items_box.bind(minimum_height=self.items_box.setter("height"))
        self.content.add_widget(self.items_box)
        self.empty_label = make_label("", sp(14), theme.rgba(theme.TEXT_MUTED))
        self.content.add_widget(self.empty_label)

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ---------- À redéfinir dans les écrans enfants ----------

    def build_controls(self, content):
        """Ajoute des champs de recherche ou de filtre (facultatif)."""

    def get_params(self):
        """Lit les critères (dans le fil principal) avant l'appel à l'API."""
        return {}

    def fetch(self, params):
        """Appelle l'API (dans un fil d'arrière-plan) et retourne la liste."""
        return []

    # ---------- Chargement ----------

    def on_pre_enter(self, *args):
        self.refresh()

    def schedule_refresh(self, *args):
        """Attend une courte pause dans la saisie avant de relancer la recherche."""
        if self._refresh_event is not None:
            self._refresh_event.cancel()
        self._refresh_event = Clock.schedule_once(lambda dt: self.refresh(), 0.35)

    def refresh(self, *args):
        params = self.get_params()
        self._request_id += 1
        request_id = self._request_id
        run_async(
            lambda: self.fetch(params),
            on_success=lambda items: self._on_loaded(request_id, items),
        )

    def _on_loaded(self, request_id, items):
        if request_id != self._request_id:
            return  # une recherche plus récente est déjà en cours
        self.show_items(items)

    def show_items(self, items):
        self.items_box.clear_widgets()
        for item in items:
            card = ItemCard(item)
            card.bind(on_release=lambda inst, i=item: self.open_item(i))
            self.items_box.add_widget(card)
        self.empty_label.text = "" if items else self.empty_text

    def open_item(self, item):
        detail = self.manager.get_screen("item_detail")
        detail.show_item(item, back_to=self.name)
        self.manager.transition.direction = "left"
        self.manager.current = "item_detail"

    def go_home(self, *args):
        self.manager.transition.direction = "right"
        self.manager.current = "home"


class ItemsScreen(BaseListScreen):
    """Toutes les annonces, avec recherche par nom et filtres."""

    title = "Toutes les annonces"
    empty_text = "Aucune annonce ne correspond à votre recherche."

    def build_controls(self, content):
        self.categories = []

        self.search_input = IconTextInput(
            "search", "Rechercher un objet", fill=theme.WHITE
        )
        content.add_widget(self.search_input)

        self.tabs = SegmentedTabs(
            options=[("all", "Tous"), ("lost", "Perdus"), ("found", "Trouvés")],
            selected="all",
        )
        content.add_widget(self.tabs)

        row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10)
        )
        self.category_field = DropdownField("list", "Catégorie", values=["Toutes"])
        self.location_input = IconTextInput("place", "Lieu", fill=theme.WHITE)
        row.add_widget(self.category_field)
        row.add_widget(self.location_input)
        content.add_widget(row)

        # La liste se met à jour quand on change un critère
        self.search_input.input.bind(text=self.schedule_refresh)
        self.location_input.input.bind(text=self.schedule_refresh)
        self.category_field.spinner.bind(text=self.refresh)
        self.tabs.bind(on_select=self.refresh)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        run_async(category_service.list_categories, on_success=self._on_categories)

    def _on_categories(self, categories):
        self.categories = categories
        self.category_field.set_values(
            ["Toutes"] + [category["name"] for category in categories]
        )

    def get_params(self):
        kind = None if self.tabs.selected == "all" else self.tabs.selected

        category_id = None
        name = self.category_field.selected_value
        if name and name != "Toutes":
            category_id = next(
                (c["id"] for c in self.categories if c["name"] == name), None
            )

        return {
            "kind": kind,
            "query": self.search_input.text.strip() or None,
            "category_id": category_id,
            "location": self.location_input.text.strip() or None,
        }

    def fetch(self, params):
        return item_service.list_items(**params)


class MyItemsScreen(BaseListScreen):
    """Les annonces publiées par l'utilisateur connecté."""

    title = "Mes annonces"
    empty_text = "Vous n'avez publié aucune annonce."

    def fetch(self, params):
        return item_service.my_items()