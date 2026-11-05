from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import theme
from services.sample_data import SAMPLE_CLAIMS, SAMPLE_USER, SAMPLE_USERS
from widgets.card import paint_background
from widgets.claim_card import ClaimCard
from widgets.labels import make_label
from widgets.popups import ConfirmPopup
from widgets.segmented_tabs import SegmentedTabs
from widgets.toast import show_toast
from widgets.top_bar import TopBar


class ClaimsScreen(Screen):
    """Demandes de récupération reçues et envoyées."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        root.add_widget(
            TopBar(
                "Mes demandes",
                left_icon="arrow_back",
                right_icon="home",
                on_left=self.go_home,
                on_right=self.go_home,
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

        self.tabs = SegmentedTabs(
            options=[("received", "Reçues"), ("sent", "Envoyées")],
            selected="received",
        )
        self.tabs.bind(on_select=lambda instance, key: self.refresh())
        content.add_widget(self.tabs)

        self.list_box = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(12)
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        content.add_widget(self.list_box)
        self.empty_label = make_label("", sp(14), theme.rgba(theme.TEXT_MUTED))
        content.add_widget(self.empty_label)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh()

    def go_home(self, *args):
        self.manager.transition.direction = "right"
        self.manager.current = "home"

    # ---------- Affichage ----------

    def _claims_for(self, direction):
        me = SAMPLE_USER["id"]
        if direction == "received":
            claims = [c for c in SAMPLE_CLAIMS if c["item"]["owner"]["id"] == me]
        else:
            claims = [c for c in SAMPLE_CLAIMS if c["claimant"]["id"] == me]
        return sorted(claims, key=lambda claim: claim["id"], reverse=True)

    def refresh(self):
        direction = self.tabs.selected
        claims = self._claims_for(direction)
        self.list_box.clear_widgets()
        for claim in claims:
            self.list_box.add_widget(
                ClaimCard(
                    claim,
                    direction,
                    on_accept=self.ask_accept,
                    on_reject=self.ask_reject,
                    on_cancel=self.ask_cancel,
                )
            )
        if claims:
            self.empty_label.text = ""
        elif direction == "received":
            self.empty_label.text = "Vous n'avez reçu aucune demande."
        else:
            self.empty_label.text = "Vous n'avez envoyé aucune demande."

    # ---------- Actions (simulées : l'API viendra à l'étape 4) ----------

    def ask_accept(self, claim):
        ConfirmPopup(
            title="Accepter cette demande ?",
            message="L'objet sera marqué comme récupéré et les autres demandes "
            "en attente seront refusées.",
            confirm_text="Accepter",
            on_confirm=lambda: self.accept(claim),
        ).open()

    def accept(self, claim):
        claim["status"] = "accepted"
        claim["item"]["status"] = "recovered"
        claim["contact_email"] = next(
            (
                user["email"]
                for user in SAMPLE_USERS
                if user["id"] == claim["claimant"]["id"]
            ),
            None,
        )
        # Les autres demandes en attente sur le même objet sont refusées
        for other in SAMPLE_CLAIMS:
            if (
                other is not claim
                and other["item"] is claim["item"]
                and other["status"] == "pending"
            ):
                other["status"] = "rejected"
        self.refresh()
        show_toast("Demande acceptée (simulation).")

    def ask_reject(self, claim):
        ConfirmPopup(
            title="Refuser cette demande ?",
            message="La personne sera informée du refus.",
            confirm_text="Refuser",
            on_confirm=lambda: self.reject(claim),
            danger=True,
        ).open()

    def reject(self, claim):
        claim["status"] = "rejected"
        self.refresh()
        show_toast("Demande refusée (simulation).")

    def ask_cancel(self, claim):
        ConfirmPopup(
            title="Annuler la demande ?",
            message="Cette action est définitive.",
            confirm_text="Annuler la demande",
            on_confirm=lambda: self.cancel(claim),
            danger=True,
        ).open()

    def cancel(self, claim):
        SAMPLE_CLAIMS.remove(claim)
        self.refresh()
        show_toast("Demande annulée (simulation).")