from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout

import theme
from widgets.card import Card
from widgets.rounded_button import RoundedButton
from widgets.status_badge import StatusBadge
from widgets.text_lines import single_line_label


class AdminRow(Card):
    """Ligne d'administration : titre, sous-titre, pastille et bouton facultatifs."""

    def __init__(
        self,
        title,
        subtitle,
        badge=None,
        action_text=None,
        on_action=None,
        **kwargs
    ):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(70))
        kwargs.setdefault("padding", dp(12))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)

        texts = BoxLayout(orientation="vertical", spacing=dp(2))
        texts.add_widget(
            single_line_label(title, sp(15), theme.rgba(theme.TEXT_DARK), bold=True)
        )
        texts.add_widget(
            single_line_label(subtitle, sp(12), theme.rgba(theme.TEXT_MUTED))
        )
        self.add_widget(texts)

        # badge = (style, texte), par exemple ("found", "Admin")
        if badge:
            pill = StatusBadge(badge[0], text=badge[1])
            pill.pos_hint = {"center_y": 0.5}
            self.add_widget(pill)

        if action_text:
            button = RoundedButton(
                text=action_text,
                bg_color=theme.rgba(theme.DANGER),
                font_size=sp(12),
                size_hint=(None, None),
                width=dp(88),
                height=dp(36),
                pos_hint={"center_y": 0.5},
            )
            button.bind(on_release=lambda *args: on_action and on_action())
            self.add_widget(button)