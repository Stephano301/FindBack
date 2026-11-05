from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import theme
from services.formatters import format_date
from services.sample_data import SAMPLE_CLAIMS, SAMPLE_ITEMS, SAMPLE_USER, SAMPLE_USERS
from widgets.admin_row import AdminRow
from widgets.card import paint_background
from widgets.labels import make_label
from widgets.popups import ConfirmPopup
from widgets.segmented_tabs import SegmentedTabs
from widgets.stat_card import StatCard
from widgets.toast import show_toast
from widgets.top_bar import TopBar

KIND_LABELS = {"lost": "Perdu", "found": "Trouvé"}
CLAIM_LABELS = {"pending": "En attente", "accepted": "Acceptée", "rejected": "Refusée"}

# Deux rangées de quatre statistiques : (clé, icône, couleur, légende)
STAT_ROWS = [
    [
        ("total_users", "person", theme.PRIMARY, "Utilisateurs"),
        ("total_items", "list", theme.PRIMARY_LIGHT, "Annonces"),
        ("total_lost", "warning", theme.DANGER, "Perdus"),
        ("total_found", "check", theme.SUCCESS, "Trouvés"),
    ],
    [
        ("total_recovered", "star", theme.PRIMARY, "Récupérés"),
        ("claims_pending", "hourglass", theme.ACCENT, "En attente"),
        ("claims_accepted", "check", theme.SUCCESS, "Acceptées"),
        ("claims_rejected", "warning", theme.DANGER, "Refusées"),
    ],
]


def compute_stats():
    """Calcule les statistiques à partir des données d'exemple (l'API le fera à l'étape 4)."""
    return {
        "total_users": len(SAMPLE_USERS),
        "total_items": len(SAMPLE_ITEMS),
        "total_lost": sum(1 for i in SAMPLE_ITEMS if i["kind"] == "lost"),
        "total_found": sum(1 for i in SAMPLE_ITEMS if i["kind"] == "found"),
        "total_recovered": sum(1 for i in SAMPLE_ITEMS if i["status"] == "recovered"),
        "claims_pending": sum(1 for c in SAMPLE_CLAIMS if c["status"] == "pending"),
        "claims_accepted": sum(1 for c in SAMPLE_CLAIMS if c["status"] == "accepted"),
        "claims_rejected": sum(1 for c in SAMPLE_CLAIMS if c["status"] == "rejected"),
    }


class AdminScreen(Screen):
    """Statistiques, utilisateurs, annonces et demandes de toute l'application."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stat_cards = {}

        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        root.add_widget(
            TopBar(
                "Administration",
                left_icon="arrow_back",
                right_icon="home",
                on_left=lambda: self.go("profile"),
                on_right=lambda: self.go("home"),
            )
        )

        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(12),
        )
        content.bind(minimum_height=content.setter("height"))

        for row_definition in STAT_ROWS:
            grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(122))
            for key, icon_name, color, label in row_definition:
                card = StatCard(icon_name, color, label)
                self.stat_cards[key] = card
                grid.add_widget(card)
            content.add_widget(grid)

        self.tabs = SegmentedTabs(
            options=[
                ("users", "Utilisateurs"),
                ("items", "Annonces"),
                ("claims", "Demandes"),
            ],
            selected="users",
        )
        self.tabs.bind(on_select=lambda instance, key: self.refresh())
        content.add_widget(self.tabs)

        self.list_box = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(10)
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        content.add_widget(self.list_box)
        self.empty_label = make_label("", sp(14), theme.rgba(theme.TEXT_MUTED))
        content.add_widget(self.empty_label)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        # Écran réservé aux administrateurs
        if not SAMPLE_USER.get("is_admin"):
            show_toast("Accès réservé aux administrateurs.")
            Clock.schedule_once(lambda dt: self.go("home"), 0)
            return
        self.refresh()

    def go(self, screen_name):
        self.manager.transition.direction = "right"
        self.manager.current = screen_name

    # ---------- Affichage ----------

    def refresh(self):
        stats = compute_stats()
        for key, card in self.stat_cards.items():
            card.set_value(stats[key])

        self.list_box.clear_widgets()
        tab = self.tabs.selected
        if tab == "users":
            rows = self._user_rows()
        elif tab == "items":
            rows = self._item_rows()
        else:
            rows = self._claim_rows()
        for row in rows:
            self.list_box.add_widget(row)
        self.empty_label.text = "" if rows else "Rien à afficher."

    def _user_rows(self):
        return [
            AdminRow(
                title=f"{user['first_name']} {user['last_name']}",
                subtitle=f"{user['email']}  •  {user['occupation']}",
                badge=("found", "Admin") if user.get("is_admin") else None,
            )
            for user in SAMPLE_USERS
        ]

    def _item_rows(self):
        return [
            AdminRow(
                title=item["title"],
                subtitle=f"{KIND_LABELS[item['kind']]}  •  {item['location']}  •  "
                f"{format_date(item['event_date'])}",
                action_text="Supprimer",
                on_action=lambda i=item: self.ask_delete_item(i),
            )
            for item in SAMPLE_ITEMS
        ]

    def _claim_rows(self):
        return [
            AdminRow(
                title=claim["item"]["title"],
                subtitle=f"{claim['claimant']['first_name']} {claim['claimant']['last_name']}"
                f"  •  {CLAIM_LABELS[claim['status']]}",
                action_text="Supprimer",
                on_action=lambda c=claim: self.ask_delete_claim(c),
            )
            for claim in SAMPLE_CLAIMS
        ]

    # ---------- Suppressions (simulées : l'API viendra à l'étape 4) ----------

    def ask_delete_item(self, item):
        ConfirmPopup(
            title="Supprimer cette annonce ?",
            message=f"« {item['title']} » et ses demandes seront supprimées.",
            confirm_text="Supprimer",
            on_confirm=lambda: self.delete_item(item),
            danger=True,
        ).open()

    def delete_item(self, item):
        SAMPLE_ITEMS.remove(item)
        SAMPLE_CLAIMS[:] = [c for c in SAMPLE_CLAIMS if c["item"] is not item]
        self.refresh()
        show_toast("Annonce supprimée (simulation).")

    def ask_delete_claim(self, claim):
        ConfirmPopup(
            title="Supprimer cette demande ?",
            message="Cette action est définitive.",
            confirm_text="Supprimer",
            on_confirm=lambda: self.delete_claim(claim),
            danger=True,
        ).open()

    def delete_claim(self, claim):
        SAMPLE_CLAIMS.remove(claim)
        self.refresh()
        show_toast("Demande supprimée (simulation).")