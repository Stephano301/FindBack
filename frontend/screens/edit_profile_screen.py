from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import theme
from services import validators
from services.sample_data import SAMPLE_USER
from widgets.card import paint_background
from widgets.icon_text_input import IconTextInput
from widgets.labels import make_label
from widgets.photo_picker import PhotoPicker
from widgets.rounded_button import RoundedButton
from widgets.separator import Separator
from widgets.toast import show_toast
from widgets.top_bar import TopBar


def check_fields(checks):
    """Efface les erreurs, colore le premier champ fautif et retourne son message."""
    for field, _ in checks:
        field.set_error(False)
    for field, error in checks:
        if error:
            field.set_error(True)
            return error
    return None


class EditProfileScreen(Screen):
    """Modification du profil et du mot de passe."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white = theme.WHITE
        root = BoxLayout(orientation="vertical")
        paint_background(root, theme.BACKGROUND)
        root.add_widget(
            TopBar(
                "Modifier mon profil",
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

        # --- Informations personnelles ---
        content.add_widget(
            make_label(
                "Informations personnelles",
                sp(16),
                theme.rgba(theme.TEXT_DARK),
                bold=True,
                halign="left",
            )
        )
        self.photo_picker = PhotoPicker()
        content.add_widget(self.photo_picker)
        self.first_name_input = IconTextInput("person", "Prénom", fill=white)
        self.last_name_input = IconTextInput("person", "Nom", fill=white)
        self.email_input = IconTextInput("email", "Adresse e-mail", fill=white)
        self.occupation_input = IconTextInput("label", "Statut", fill=white)
        for widget in (
            self.first_name_input,
            self.last_name_input,
            self.email_input,
            self.occupation_input,
        ):
            content.add_widget(widget)
        self.profile_message = make_label("", sp(13), theme.rgba(theme.DANGER))
        content.add_widget(self.profile_message)
        save_button = RoundedButton(text="Enregistrer")
        save_button.bind(on_release=self.save_profile)
        content.add_widget(save_button)

        content.add_widget(Separator())

        # --- Mot de passe ---
        content.add_widget(
            make_label(
                "Changer le mot de passe",
                sp(16),
                theme.rgba(theme.TEXT_DARK),
                bold=True,
                halign="left",
            )
        )
        self.current_password = IconTextInput(
            "lock", "Mot de passe actuel", password=True, fill=white
        )
        self.new_password = IconTextInput(
            "lock", "Nouveau mot de passe", password=True, fill=white
        )
        self.confirm_password = IconTextInput(
            "lock", "Confirmer le nouveau mot de passe", password=True, fill=white
        )
        for widget in (
            self.current_password,
            self.new_password,
            self.confirm_password,
        ):
            content.add_widget(widget)
        self.password_message = make_label("", sp(13), theme.rgba(theme.DANGER))
        content.add_widget(self.password_message)
        password_button = RoundedButton(text="Modifier le mot de passe")
        password_button.bind(on_release=self.change_password)
        content.add_widget(password_button)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        """Remplit les champs avec les informations actuelles."""
        self.first_name_input.text = SAMPLE_USER["first_name"]
        self.last_name_input.text = SAMPLE_USER["last_name"]
        self.email_input.text = SAMPLE_USER["email"]
        self.occupation_input.text = SAMPLE_USER["occupation"]
        self.photo_picker.clear()
        for field in (
            self.current_password,
            self.new_password,
            self.confirm_password,
        ):
            field.clear()
        self.profile_message.text = ""
        self.password_message.text = ""

    def go(self, screen_name):
        self.manager.transition.direction = "right"
        self.manager.current = screen_name

    # ---------- Enregistrer le profil ----------

    def save_profile(self, *args):
        first_name = self.first_name_input.text.strip()
        last_name = self.last_name_input.text.strip()
        email = self.email_input.text.strip().lower()
        occupation = self.occupation_input.text.strip()

        error = check_fields(
            [
                (self.first_name_input, validators.validate_name(first_name, "Prénom")),
                (self.last_name_input, validators.validate_name(last_name, "Nom")),
                (self.email_input, validators.validate_email(email)),
                (
                    self.occupation_input,
                    validators.validate_name(occupation, "Statut"),
                ),
            ]
        )
        if error:
            self.profile_message.text = error
            return

        changes = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "occupation": occupation,
        }
        # L'envoi à l'API sera ajouté à l'étape 4 : ici on modifie l'exemple en mémoire
        print("Profil prêt à être envoyé à l'API :", changes, "| photo :", self.photo_picker.path)
        SAMPLE_USER.update(changes)
        show_toast("Profil modifié (simulation). L'API viendra à l'étape 4.")
        self.go("profile")

    # ---------- Changer le mot de passe ----------

    def change_password(self, *args):
        current = self.current_password.text
        new = self.new_password.text
        confirm = self.confirm_password.text

        confirm_error = None if new == confirm else "Les mots de passe ne correspondent pas."
        error = check_fields(
            [
                (
                    self.current_password,
                    None if current else "Veuillez saisir votre mot de passe actuel.",
                ),
                (self.new_password, validators.validate_password(new)),
                (self.confirm_password, confirm_error),
            ]
        )
        if error:
            self.password_message.text = error
            return

        self.password_message.text = ""
        for field in (
            self.current_password,
            self.new_password,
            self.confirm_password,
        ):
            field.clear()
        show_toast("Mot de passe valide (simulation). L'API viendra à l'étape 4.")