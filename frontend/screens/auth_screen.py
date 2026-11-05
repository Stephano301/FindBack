from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import theme
from services import auth_service, validators
from services.session import session
from services.tasks import error_text, run_async
from widgets.icon_text_input import IconTextInput
from widgets.labels import make_label
from widgets.logo import LogoWidget
from widgets.rounded_button import RoundedButton
from widgets.segmented_tabs import SegmentedTabs


class AuthBackground(Widget):
    """Fond blanc avec deux taches lavande dans les coins."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        w, h = self.size
        x0, y0 = self.pos
        with self.canvas:
            Color(*theme.rgba(theme.WHITE))
            Rectangle(pos=self.pos, size=self.size)
            Color(*theme.rgba(theme.LAVENDER))
            Ellipse(pos=(x0 - 0.30 * w, y0 + 0.88 * h), size=(0.65 * w, 0.26 * h))
            Ellipse(pos=(x0 + 0.70 * w, y0 - 0.12 * h), size=(0.65 * w, 0.26 * h))


class _Line(Widget):
    """Un trait horizontal fin."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*theme.rgba(theme.LAVENDER_DARK))
            self._rect = Rectangle(pos=self.pos, size=(self.width, dp(1)))
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = (self.x, self.center_y)
        self._rect.size = (self.width, dp(1))


class Divider(BoxLayout):
    """Séparateur « ——— ou ——— »."""

    def __init__(self, text="ou", **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(24))
        kwargs.setdefault("spacing", dp(10))
        super().__init__(**kwargs)
        self.add_widget(_Line())
        self.add_widget(
            Label(
                text=text,
                color=theme.rgba(theme.TEXT_MUTED),
                font_size=sp(13),
                size_hint_x=None,
                width=dp(24),
            )
        )
        self.add_widget(_Line())


class AuthScreen(Screen):
    """Connexion et inscription, avec deux onglets."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        root.add_widget(AuthBackground())

        # Tout le contenu est dans un ScrollView : l'écran peut défiler
        scroll = ScrollView(do_scroll_x=False, bar_width=0)
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(24), dp(40), dp(24), dp(24)],
            spacing=dp(14),
        )
        content.bind(minimum_height=content.setter("height"))

        # --- En-tête : logo, nom, sous-titre ---
        content.add_widget(LogoWidget(variant="dark", size_hint_y=None, height=dp(110)))
        content.add_widget(
            make_label(
                f"[b][color={theme.PRIMARY}]Find[/color]"
                f"[color={theme.ACCENT}]Back[/color][/b]",
                font_size=sp(32),
                color=theme.rgba(theme.TEXT_DARK),
                markup=True,
            )
        )
        self.subtitle = make_label("", sp(14), theme.rgba(theme.TEXT_DARK))
        content.add_widget(self.subtitle)

        # --- Onglets ---
        self.tabs = SegmentedTabs(
            options=[("login", "Connexion"), ("register", "Inscription")],
            selected="login",
        )
        self.tabs.bind(on_select=lambda instance, key: self.show_tab(key))
        content.add_widget(self.tabs)

        # --- Zone du formulaire (change selon l'onglet) ---
        self.form_holder = BoxLayout(orientation="vertical", size_hint_y=None)
        self.form_holder.bind(minimum_height=self.form_holder.setter("height"))
        content.add_widget(self.form_holder)

        # --- Message d'erreur ou d'information ---
        self.message = make_label("", sp(13), theme.rgba(theme.DANGER))
        content.add_widget(self.message)

        # --- Lien pour changer d'onglet ---
        self.switch_link = make_label(
            "", sp(14), theme.rgba(theme.TEXT_DARK), markup=True
        )
        self.switch_link.bind(on_ref_press=lambda instance, ref: self.show_tab(ref))
        content.add_widget(self.switch_link)

        self.login_form = self._build_login_form()
        self.register_form = self._build_register_form()

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)
        self.show_tab("login")

    # ---------- Arrivée sur l'écran ----------

    def on_pre_enter(self, *args):
        """Arriver ici signifie être déconnecté : on efface la session."""
        session.clear()
        for field in (self.login_password, self.reg_password, self.reg_confirm):
            field.clear()
        self.message.text = ""

    # ---------- Construction des formulaires ----------

    def _new_form_box(self):
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12))
        box.bind(minimum_height=box.setter("height"))
        return box

    def _build_login_form(self):
        form = self._new_form_box()
        self.login_email = IconTextInput("email", "Adresse e-mail")
        self.login_password = IconTextInput("lock", "Mot de passe", password=True)
        self.login_button = RoundedButton(text="Se connecter")
        self.login_button.bind(on_release=self.submit_login)

        google_button = RoundedButton(
            text="Continuer avec Google",
            bg_color=theme.rgba(theme.LAVENDER),
            color=theme.rgba(theme.TEXT_DARK),
        )
        google_button.bind(
            on_release=lambda *args: self.show_info(
                "La connexion avec Google sera disponible plus tard."
            )
        )

        for widget in (
            self.login_email,
            self.login_password,
            self.login_button,
            Divider(),
            google_button,
        ):
            form.add_widget(widget)
        return form

    def _build_register_form(self):
        form = self._new_form_box()
        self.reg_first_name = IconTextInput("person", "Prénom")
        self.reg_last_name = IconTextInput("person", "Nom")
        self.reg_email = IconTextInput("email", "Adresse e-mail")
        self.reg_occupation = IconTextInput("label", "Statut", text="Étudiant")
        self.reg_password = IconTextInput("lock", "Mot de passe", password=True)
        self.reg_confirm = IconTextInput(
            "lock", "Confirmer le mot de passe", password=True
        )
        self.register_button = RoundedButton(text="Créer mon compte")
        self.register_button.bind(on_release=self.submit_register)

        for widget in (
            self.reg_first_name,
            self.reg_last_name,
            self.reg_email,
            self.reg_occupation,
            self.reg_password,
            self.reg_confirm,
            self.register_button,
        ):
            form.add_widget(widget)
        return form

    # ---------- Changement d'onglet ----------

    def show_tab(self, key):
        self.tabs.select(key, notify=False)
        self.form_holder.clear_widgets()
        link_style = f"[ref={{ref}}][color={theme.PRIMARY}][b]{{label}}[/b][/color][/ref]"

        if key == "login":
            self.form_holder.add_widget(self.login_form)
            self.subtitle.text = "Connectez-vous pour continuer"
            self.switch_link.text = "Pas de compte ? " + link_style.format(
                ref="register", label="Inscrivez-vous"
            )
        else:
            self.form_holder.add_widget(self.register_form)
            self.subtitle.text = "Créez votre compte pour commencer"
            self.switch_link.text = "Déjà un compte ? " + link_style.format(
                ref="login", label="Connectez-vous"
            )
        self.message.text = ""

    # ---------- Messages ----------

    def show_error(self, text):
        self.message.color = theme.rgba(theme.DANGER)
        self.message.text = text

    def show_info(self, text):
        self.message.color = theme.rgba(theme.SUCCESS)
        self.message.text = text

    # ---------- Connexion ----------

    def submit_login(self, *args):
        email = self.login_email.text.strip().lower()
        password = self.login_password.text

        error = validators.validate_email(email)
        if error is None and not password:
            error = "Veuillez saisir votre mot de passe."
        if error:
            self.show_error(error)
            return

        self.show_info("Connexion en cours…")
        run_async(
            lambda: auth_service.login(email, password),
            on_success=self._on_authenticated,
            on_error=self._on_auth_error,
            busy_widget=self.login_button,
        )

    # ---------- Inscription ----------

    def submit_register(self, *args):
        first_name = self.reg_first_name.text.strip()
        last_name = self.reg_last_name.text.strip()
        email = self.reg_email.text.strip().lower()
        occupation = self.reg_occupation.text.strip()
        password = self.reg_password.text
        confirm = self.reg_confirm.text

        error = (
            validators.validate_name(first_name, "Prénom")
            or validators.validate_name(last_name, "Nom")
            or validators.validate_email(email)
            or validators.validate_name(occupation, "Statut")
            or validators.validate_password(password)
        )
        if error is None and password != confirm:
            error = "Les mots de passe ne correspondent pas."
        if error:
            self.show_error(error)
            return

        self.show_info("Création du compte…")
        run_async(
            lambda: auth_service.register(
                first_name, last_name, email, password, occupation
            ),
            on_success=self._on_authenticated,
            on_error=self._on_auth_error,
            busy_widget=self.register_button,
        )

    # ---------- Résultat des appels à l'API ----------

    def _on_authenticated(self, result):
        token, user = result
        session.set(token, user)
        self.message.text = ""
        self.manager.transition.direction = "left"
        self.manager.current = "home"

    def _on_auth_error(self, error):
        self.show_error(error_text(error))