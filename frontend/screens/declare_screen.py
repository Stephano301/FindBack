from datetime import date

from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import theme
from services import category_service, item_service
from services.api_client import ApiError
from services.formatters import format_date
from services.item_validators import (
    parse_date_input,
    validate_item_date,
    validate_length,
)
from services.tasks import run_async
from widgets.card import paint_background
from widgets.dropdown_field import DropdownField
from widgets.icon_text_input import IconTextInput
from widgets.labels import make_label
from widgets.photo_picker import PhotoPicker
from widgets.rounded_button import RoundedButton
from widgets.segmented_tabs import SegmentedTabs
from widgets.text_area import TextArea
from widgets.toast import show_toast
from widgets.top_bar import TopBar

# Textes qui changent selon que l'objet est perdu ou trouvé
KIND_TEXTS = {
    "lost": {
        "location_hint": "Lieu de perte",
        "section": "Où et quand l'avez-vous perdu ?",
    },
    "found": {
        "location_hint": "Lieu de découverte",
        "section": "Où et quand l'avez-vous trouvé ?",
    },
}


def today_text():
    return date.today().strftime("%d/%m/%Y")


class DeclareScreen(Screen):
    """Formulaire pour déclarer un objet, ou pour modifier une annonce existante."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kind = "lost"
        self.categories = []  # chargées depuis l'API
        self.editing_item = None  # None = création, sinon l'annonce modifiée
        self._prepared = False  # True quand start_edit() vient de préparer le formulaire

        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        self.top_bar = TopBar(
            "Déclarer un objet",
            left_icon="arrow_back",
            right_icon="home",
            on_left=self.go_back,
            on_right=self.go_home,
        )
        root.add_widget(self.top_bar)

        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        # Onglets Objet perdu / Objet trouvé
        self.tabs = SegmentedTabs(
            options=[("lost", "Objet perdu"), ("found", "Objet trouvé")],
            selected="lost",
        )
        self.tabs.bind(on_select=lambda instance, key: self.set_kind(key))
        content.add_widget(self.tabs)

        # Photo
        self.photo_picker = PhotoPicker()
        content.add_widget(self.photo_picker)

        # Nom, description, catégorie
        self.title_input = IconTextInput("label", "Nom de l'objet", fill=theme.WHITE)
        content.add_widget(self.title_input)
        self.description_input = TextArea("Description")
        content.add_widget(self.description_input)
        self.category_field = DropdownField("list", "Choisir une catégorie", values=[])
        content.add_widget(self.category_field)

        # Lieu et date
        self.section_label = make_label(
            "", sp(13), theme.rgba(theme.TEXT_MUTED), halign="left"
        )
        content.add_widget(self.section_label)
        row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10)
        )
        self.location_input = IconTextInput("place", "Lieu de perte", fill=theme.WHITE)
        self.date_input = IconTextInput(
            "event", "JJ/MM/AAAA", text=today_text(), fill=theme.WHITE
        )
        row.add_widget(self.location_input)
        row.add_widget(self.date_input)
        content.add_widget(row)

        # Message et bouton de publication
        self.message = make_label("", sp(13), theme.rgba(theme.DANGER))
        content.add_widget(self.message)
        self.publish_button = RoundedButton(text="Publier l'annonce")
        self.publish_button.bind(on_release=self.publish)
        content.add_widget(self.publish_button)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)
        self.set_kind("lost")

    # ---------- Arrivée sur l'écran ----------

    def on_pre_enter(self, *args):
        if self._prepared:
            # Le formulaire vient d'être rempli par start_edit()
            self._prepared = False
        else:
            self.start_create()
        self.load_categories()

    def load_categories(self):
        run_async(category_service.list_categories, on_success=self._on_categories)

    def _on_categories(self, categories):
        self.categories = categories
        self.category_field.set_values([category["name"] for category in categories])

    def start_create(self):
        """Prépare un formulaire vide pour une nouvelle annonce."""
        self.editing_item = None
        self.top_bar.set_title("Déclarer un objet")
        self.publish_button.text = "Publier l'annonce"
        self.tabs.disabled = False
        self.reset_form()
        self.set_kind("lost")

    def start_edit(self, item):
        """Prépare le formulaire pour modifier une annonce existante."""
        self._prepared = True
        self.editing_item = item
        self.top_bar.set_title("Modifier l'annonce")
        self.publish_button.text = "Enregistrer les modifications"
        self.reset_form()
        self.set_kind(item["kind"])
        self.tabs.disabled = True  # le type (perdu / trouvé) ne peut pas changer
        self.title_input.text = item["title"]
        self.description_input.text = item["description"]
        self.location_input.text = item["location"]
        self.date_input.text = format_date(item["event_date"])
        self.category_field.spinner.text = item["category"]["name"]

    # ---------- Navigation ----------

    def go_back(self, *args):
        target = "item_detail" if self.editing_item else "home"
        self.manager.transition.direction = "right"
        self.manager.current = target

    def go_home(self, *args):
        self.manager.transition.direction = "right"
        self.manager.current = "home"

    # ---------- Perdu / trouvé ----------

    def set_kind(self, kind):
        self.kind = kind
        self.tabs.select(kind, notify=False)
        texts = KIND_TEXTS[kind]
        self.location_input.input.hint_text = texts["location_hint"]
        self.section_label.text = texts["section"]

    def show_error(self, text):
        self.message.color = theme.rgba(theme.DANGER)
        self.message.text = text

    # ---------- Validation et envoi ----------

    def _category_id(self, name):
        for category in self.categories:
            if category["name"] == name:
                return category["id"]
        return None

    def publish(self, *args):
        title = self.title_input.text.strip()
        description = self.description_input.text.strip()
        location = self.location_input.text.strip()
        date_text = self.date_input.text.strip()
        category_name = self.category_field.selected_value

        checks = [
            (self.title_input, validate_length(title, "Nom de l'objet", 2, 100)),
            (
                self.description_input,
                validate_length(description, "Description", 3, 2000),
            ),
            (
                self.category_field,
                None if category_name else "Veuillez choisir une catégorie.",
            ),
            (self.location_input, validate_length(location, "Lieu", 2, 150)),
            (self.date_input, validate_item_date(date_text)),
        ]

        # On efface les anciennes erreurs, puis on signale la première trouvée
        for field, _ in checks:
            field.set_error(False)
        for field, error in checks:
            if error:
                field.set_error(True)
                self.show_error(error)
                return

        category_id = self._category_id(category_name)
        if category_id is None:
            self.show_error("Les catégories n'ont pas pu être chargées. Réessayez.")
            return

        values = {
            "title": title,
            "description": description,
            "location": location,
            "event_date": parse_date_input(date_text).isoformat(),
            "category_id": category_id,
        }
        photo = self.photo_picker.path
        self.message.text = ""

        if self.editing_item:
            item_id = self.editing_item["id"]
            task = lambda: self._upload_after(
                item_service.update_item(item_id, values), photo
            )
        else:
            payload = dict(values, kind=self.kind)
            task = lambda: self._upload_after(item_service.create_item(payload), photo)

        run_async(task, on_success=self._on_saved, busy_widget=self.publish_button)

    @staticmethod
    def _upload_after(item, photo):
        """Envoie la photo (si choisie) après la création ou la modification."""
        photo_error = None
        if photo:
            try:
                item = item_service.upload_photo(item["id"], photo)
            except ApiError as error:
                photo_error = error.message
        return item, photo_error

    def _on_saved(self, result):
        item, photo_error = result
        was_editing = self.editing_item is not None

        if photo_error:
            show_toast(f"Annonce enregistrée, mais la photo a échoué : {photo_error}")
        else:
            show_toast("Annonce modifiée." if was_editing else "Annonce publiée !")

        self.manager.transition.direction = "right"
        if was_editing:
            detail = self.manager.get_screen("item_detail")
            detail.show_item(item, back_to=detail.back_target)
            self.manager.current = "item_detail"
        else:
            # L'accueil se recharge tout seul en s'affichant
            self.manager.current = "home"

    def reset_form(self):
        for field in (
            self.title_input,
            self.description_input,
            self.location_input,
            self.category_field,
            self.date_input,
        ):
            field.set_error(False)
        self.title_input.clear()
        self.description_input.clear()
        self.location_input.clear()
        self.date_input.text = today_text()
        self.category_field.reset()
        self.photo_picker.clear()
        self.message.text = ""