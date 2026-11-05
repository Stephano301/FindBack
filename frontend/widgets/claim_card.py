from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout

import theme
from services.formatters import format_date
from widgets.card import Card
from widgets.icons import Icon
from widgets.labels import make_label
from widgets.rounded_button import RoundedButton
from widgets.status_badge import StatusBadge
from widgets.text_lines import single_line_label

# état de la demande -> (style de la pastille, texte)
CLAIM_BADGES = {
    "pending": ("pending", "En attente"),
    "accepted": ("recovered", "Acceptée"),
    "rejected": ("lost", "Refusée"),
}


def _icon_row(icon_name, text, color, bold=False):
    row = BoxLayout(
        orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(6)
    )
    row.add_widget(
        Icon(
            icon_name,
            icon_size=sp(16),
            color=theme.rgba(color),
            size_hint_x=None,
            width=dp(20),
        )
    )
    row.add_widget(single_line_label(text, sp(13), theme.rgba(color), bold=bold))
    return row


class ClaimCard(Card):
    """Carte d'une demande. direction : « received » (reçue) ou « sent » (envoyée)."""

    def __init__(
        self,
        claim,
        direction,
        on_accept=None,
        on_reject=None,
        on_cancel=None,
        **kwargs
    ):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", dp(14))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter("height"))

        item = claim["item"]

        # Titre de l'annonce et état de la demande
        title_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(26), spacing=dp(8)
        )
        title_row.add_widget(
            single_line_label(
                item["title"], sp(16), theme.rgba(theme.TEXT_DARK), bold=True
            )
        )
        badge_kind, badge_text = CLAIM_BADGES[claim["status"]]
        badge = StatusBadge(badge_kind, text=badge_text)
        badge.pos_hint = {"center_y": 0.5}
        title_row.add_widget(badge)
        self.add_widget(title_row)

        # Qui est concerné
        if direction == "received":
            person = claim["claimant"]
            who = f"Demande de {person['first_name']} {person['last_name']}"
        else:
            owner = item["owner"]
            who = f"Annonce de {owner['first_name']} {owner['last_name']}"
        self.add_widget(_icon_row("person", who, theme.TEXT_MUTED))

        # Description donnée pour prouver la propriété, puis la date
        self.add_widget(
            make_label(
                f"« {claim['message']} »",
                sp(13),
                theme.rgba(theme.TEXT_DARK),
                halign="left",
            )
        )
        self.add_widget(
            make_label(
                format_date(claim["created_at"]),
                sp(12),
                theme.rgba(theme.TEXT_MUTED),
                halign="left",
            )
        )

        # E-mail de contact, visible seulement après acceptation
        if claim["status"] == "accepted" and claim.get("contact_email"):
            self.add_widget(
                _icon_row(
                    "email", f"Contact : {claim['contact_email']}", theme.SUCCESS, True
                )
            )

        # Boutons d'action (seulement si la demande est en attente)
        if claim["status"] == "pending":
            if direction == "received":
                buttons = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(44),
                    spacing=dp(10),
                )
                reject_button = RoundedButton(
                    text="Refuser",
                    bg_color=theme.rgba(theme.LAVENDER),
                    color=theme.rgba(theme.TEXT_DARK),
                    height=dp(44),
                    font_size=sp(14),
                )
                accept_button = RoundedButton(
                    text="Accepter", height=dp(44), font_size=sp(14)
                )
                reject_button.bind(
                    on_release=lambda *args: on_reject and on_reject(claim)
                )
                accept_button.bind(
                    on_release=lambda *args: on_accept and on_accept(claim)
                )
                buttons.add_widget(reject_button)
                buttons.add_widget(accept_button)
                self.add_widget(buttons)
            else:
                cancel_button = RoundedButton(
                    text="Annuler la demande",
                    bg_color=theme.rgba(theme.LAVENDER),
                    color=theme.rgba(theme.TEXT_DARK),
                    height=dp(44),
                    font_size=sp(14),
                )
                cancel_button.bind(
                    on_release=lambda *args: on_cancel and on_cancel(claim)
                )
                self.add_widget(cancel_button)