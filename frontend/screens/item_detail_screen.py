from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import theme
from services import claim_service, item_service
from services.formatters import format_date
from services.session import session
from services.tasks import run_async
from widgets.card import Card, paint_background
from widgets.icons import Icon
from widgets.labels import make_label
from widgets.popups import ClaimPopup, ConfirmPopup
from widgets.rounded_button import RoundedButton
from widgets.separator import Separator
from widgets.status_badge import StatusBadge
from widgets.toast import show_toast
from widgets.top_bar import TopBar


def info_chip(icon_name, text):
    """Une icône suivie d'un texte sur une ligne."""
    row = BoxLayout(
        orientation="horizontal", size_hint_y=None, height=dp(26), spacing=dp(6)
    )
    row.add_widget(
        Icon(
            icon_name,
            icon_size=sp(18),
            color=theme.rgba(theme.PRIMARY),
            size_hint_x=None,
            width=dp(22),
        )
    )
    label = Label(
        text=text,
        font_size=sp(14),
        color=theme.rgba(theme.TEXT_DARK),
        halign="left",
        valign="middle",
        shorten=True,
        shorten_from="right",
    )
    label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    row.add_widget(label)
    return row


class ItemDetailScreen(Screen):
    """Détail d'une annonce. Appeler show_item(item) avant d'afficher l'écran."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item = None
        self.back_target = "home"

        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        root.add_widget(
            TopBar(
                "Détails de l'annonce",
                left_icon="arrow_back",
                right_icon="share",
                on_left=self.go_back,
                on_right=lambda: show_toast("Le partage sera ajouté plus tard."),
            )
        )

        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        self.content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(14),
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ---------- Navigation ----------

    def go_back(self, *args):
        self.manager.transition.direction = "right"
        self.manager.current = self.back_target

    # ---------- Affichage d'une annonce ----------

    def show_item(self, item, back_to="home"):
        self.item = item
        self.back_target = back_to
        is_owner = item["owner"]["id"] == session.user["id"]

        content = self.content
        content.clear_widgets()

        content.add_widget(self._build_photo(item))
        content.add_widget(
            make_label(
                item["title"],
                sp(24),
                theme.rgba(theme.TEXT_DARK),
                bold=True,
                halign="left",
            )
        )
        content.add_widget(
            make_label(
                item["description"], sp(14), theme.rgba(theme.TEXT_MUTED), halign="left"
            )
        )

        # Lieu et date
        pair = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(26), spacing=dp(12)
        )
        pair.add_widget(info_chip("place", item["location"]))
        pair.add_widget(info_chip("event", format_date(item["event_date"])))
        content.add_widget(pair)

        content.add_widget(Separator())
        content.add_widget(self._build_status_row(item))
        content.add_widget(info_chip("label", f"Catégorie : {item['category']['name']}"))
        owner = item["owner"]
        content.add_widget(
            info_chip("person", f"Publié par {owner['first_name']} {owner['last_name']}")
        )

        content.add_widget(Widget(size_hint_y=None, height=dp(4)))
        content.add_widget(self._build_actions(item, is_owner))
        content.add_widget(Widget(size_hint_y=None, height=dp(16)))

    def _build_photo(self, item):
        """Grande photo avec la pastille Perdu / Trouvé en haut à droite."""
        box = FloatLayout(size_hint_y=None, height=dp(210))
        if item.get("photo_url"):
            box.add_widget(AsyncImage(source=item["photo_url"], fit_mode="cover"))
        else:
            placeholder = Card(fill=theme.LAVENDER, border=None, radius=dp(16))
            placeholder.add_widget(
                Icon("camera", icon_size=sp(54), color=theme.rgba(theme.PRIMARY_LIGHT))
            )
            box.add_widget(placeholder)
        badge = StatusBadge(item["kind"])
        badge.pos_hint = {"right": 0.97, "top": 0.95}
        box.add_widget(badge)
        return box

    def _build_status_row(self, item):
        """Ligne « Statut : [pastille] »."""
        recovered = item["status"] == "recovered"
        row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(32), spacing=dp(8)
        )
        row.add_widget(
            Icon(
                "check" if recovered else "hourglass",
                icon_size=sp(20),
                color=theme.rgba(theme.SUCCESS if recovered else theme.ACCENT),
                size_hint_x=None,
                width=dp(24),
            )
        )
        status_label = Label(
            text="Statut",
            bold=True,
            font_size=sp(15),
            color=theme.rgba(theme.TEXT_DARK),
            halign="left",
            valign="middle",
            size_hint_x=None,
            width=dp(56),
        )
        status_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        row.add_widget(status_label)
        badge = StatusBadge(item["status"])
        badge.pos_hint = {"center_y": 0.5}
        row.add_widget(badge)
        row.add_widget(Widget())
        return row

    def _build_actions(self, item, is_owner):
        """Boutons du bas : dépendent de qui regarde l'annonce."""
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        box.bind(minimum_height=box.setter("height"))

        if is_owner:
            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10),
            )
            edit_button = RoundedButton(
                text="Modifier",
                bg_color=theme.rgba(theme.LAVENDER),
                color=theme.rgba(theme.TEXT_DARK),
            )
            edit_button.bind(on_release=self.edit_item)
            delete_button = RoundedButton(
                text="Supprimer", bg_color=theme.rgba(theme.DANGER)
            )
            delete_button.bind(on_release=self.ask_delete)
            row.add_widget(edit_button)
            row.add_widget(delete_button)
            box.add_widget(row)
            return box

        if item["status"] == "recovered":
            box.add_widget(
                make_label(
                    "Cet objet a déjà été récupéré.",
                    sp(14),
                    theme.rgba(theme.TEXT_MUTED),
                )
            )
        else:
            claim_button = RoundedButton(text="Faire une demande")
            claim_button.bind(on_release=self.open_claim_form)
            box.add_widget(claim_button)

        # Un administrateur peut supprimer une annonce inappropriée
        if session.user.get("is_admin"):
            admin_button = RoundedButton(
                text="Supprimer l'annonce (administrateur)",
                bg_color=theme.rgba(theme.DANGER),
                font_size=sp(14),
            )
            admin_button.bind(on_release=self.ask_delete)
            box.add_widget(admin_button)
        return box

    # ---------- Actions ----------

    def edit_item(self, *args):
        declare = self.manager.get_screen("declare")
        declare.start_edit(self.item)
        self.manager.transition.direction = "left"
        self.manager.current = "declare"

    def open_claim_form(self, *args):
        ClaimPopup(item_title=self.item["title"], on_send=self.send_claim).open()

    def send_claim(self, message):
        item_id = self.item["id"]
        run_async(
            lambda: claim_service.create_claim(item_id, message),
            on_success=lambda claim: show_toast(
                "Demande envoyée au propriétaire de l'annonce."
            ),
        )

    def ask_delete(self, *args):
        ConfirmPopup(
            title="Supprimer l'annonce ?",
            message="Cette action est définitive.",
            confirm_text="Supprimer",
            on_confirm=self.delete_item,
            danger=True,
        ).open()

    def delete_item(self):
        item_id = self.item["id"]
        run_async(
            lambda: item_service.delete_item(item_id), on_success=self._on_deleted
        )

    def _on_deleted(self, result):
        show_toast("Annonce supprimée.")
        self.go_back()