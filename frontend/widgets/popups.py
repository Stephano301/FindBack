from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

import theme
from services.item_validators import validate_length
from widgets.labels import make_label
from widgets.rounded_button import RoundedButton
from widgets.text_area import TextArea


def _popup_style():
    """Réglages communs : fond blanc, pas de barre de titre."""
    return {
        "title": "",
        "title_size": 0,
        "separator_height": 0,
        "background": "",
        "background_color": theme.rgba(theme.WHITE),
        "auto_dismiss": True,
    }


class ConfirmPopup(Popup):
    """Fenêtre « Êtes-vous sûr ? » avec un bouton Annuler et un bouton de confirmation."""

    def __init__(self, title, message, confirm_text, on_confirm, danger=False, **kwargs):
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(14))
        content.add_widget(
            make_label(title, sp(18), theme.rgba(theme.TEXT_DARK), bold=True)
        )
        content.add_widget(make_label(message, sp(14), theme.rgba(theme.TEXT_MUTED)))

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        cancel_button = RoundedButton(
            text="Annuler",
            bg_color=theme.rgba(theme.LAVENDER),
            color=theme.rgba(theme.TEXT_DARK),
        )
        confirm_button = RoundedButton(
            text=confirm_text,
            bg_color=theme.rgba(theme.DANGER if danger else theme.PRIMARY),
        )
        buttons.add_widget(cancel_button)
        buttons.add_widget(confirm_button)
        content.add_widget(buttons)

        super().__init__(
            content=content,
            size_hint=(0.88, None),
            height=dp(230),
            **_popup_style(),
            **kwargs
        )
        self._on_confirm = on_confirm
        cancel_button.bind(on_release=self.dismiss)
        confirm_button.bind(on_release=self._confirm)

    def _confirm(self, *args):
        self.dismiss()
        self._on_confirm()


class ClaimPopup(Popup):
    """Fenêtre pour réclamer un objet, avec la description qui prouve la propriété."""

    def __init__(self, item_title, on_send, **kwargs):
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10))
        content.add_widget(
            make_label(
                "Faire une demande", sp(18), theme.rgba(theme.TEXT_DARK), bold=True
            )
        )
        content.add_widget(
            make_label(
                f"Objet : {item_title}", sp(14), theme.rgba(theme.PRIMARY), bold=True
            )
        )
        content.add_widget(
            make_label(
                "Décrivez l'objet pour prouver qu'il vous appartient "
                "(signes distinctifs, contenu, etc.).",
                sp(13),
                theme.rgba(theme.TEXT_MUTED),
            )
        )
        text_area = TextArea("Votre description…", icon_name="edit", height=dp(120))
        content.add_widget(text_area)
        error_label = make_label("", sp(12), theme.rgba(theme.DANGER))
        content.add_widget(error_label)

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        cancel_button = RoundedButton(
            text="Annuler",
            bg_color=theme.rgba(theme.LAVENDER),
            color=theme.rgba(theme.TEXT_DARK),
        )
        send_button = RoundedButton(text="Envoyer")
        buttons.add_widget(cancel_button)
        buttons.add_widget(send_button)
        content.add_widget(buttons)

        super().__init__(
            content=content,
            size_hint=(0.92, None),
            height=dp(480),
            **_popup_style(),
            **kwargs
        )
        self._on_send = on_send
        self.text_area = text_area
        self.error_label = error_label
        cancel_button.bind(on_release=self.dismiss)
        send_button.bind(on_release=self._send)

    def _send(self, *args):
        message = self.text_area.text.strip()
        error = validate_length(message, "Description", 10, 1000)
        if error:
            self.text_area.set_error(True)
            self.error_label.text = error
            return
        self.dismiss()
        self._on_send(message)