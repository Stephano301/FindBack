from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

import theme
from widgets.logo import LogoWidget
from widgets.page_dots import PageDots
from widgets.rounded_button import RoundedButton

# Contenu des 3 pages de présentation (tu peux modifier ces textes)
SLIDES = [
    {
        "headline": "Trouvez  ·  Déclarez  ·  Récupérez",
        "text": "Ne perdez plus vos objets,\nretrouvez-les facilement !",
    },
    {
        "headline": "Déclarez en quelques secondes",
        "text": "Publiez un objet perdu ou trouvé\navec une photo, un lieu et une date.",
    },
    {
        "headline": "Récupérez-le simplement",
        "text": "Envoyez une demande et entrez en contact\navec la personne qui l'a trouvé.",
    },
]

# Silhouette de ville en bas de l'écran : (position, largeur, hauteur) en fractions
CITY = [
    (0.02, 0.10, 0.060),
    (0.13, 0.08, 0.090),
    (0.22, 0.11, 0.050),
    (0.62, 0.09, 0.070),
    (0.72, 0.07, 0.115),
    (0.80, 0.10, 0.060),
    (0.91, 0.08, 0.085),
]


class SplashBackground(Widget):
    """Dessine le fond violet, la vague claire et la silhouette de ville."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)

    def _hill(self, x_offset, top, width, height):
        """Une grande ellipse dont seul le haut est visible : cela forme une colline."""
        w, h = self.size
        x0, y0 = self.pos
        Ellipse(
            pos=(x0 + x_offset * w, y0 + (top - height) * h),
            size=(width * w, height * h),
        )

    def _draw(self, *args):
        self.canvas.clear()
        w, h = self.size
        x0, y0 = self.pos
        with self.canvas:
            # Fond violet
            Color(*theme.rgba(theme.PRIMARY))
            Rectangle(pos=self.pos, size=self.size)

            # Deux collines superposées pour l'effet de vague
            Color(*theme.rgba(theme.PRIMARY_LIGHT, 0.55))
            self._hill(-0.55, 0.33, 1.5, 0.70)
            Color(*theme.rgba(theme.LAVENDER))
            self._hill(-0.20, 0.28, 1.4, 0.60)

            # Silhouette de ville
            Color(*theme.rgba(theme.LAVENDER_DARK, 0.7))
            for x, width, height in CITY:
                Rectangle(pos=(x0 + x * w, y0), size=(width * w, height * h))


def make_label(text, font_size, color, bold=False, markup=False):
    """Crée un texte centré, qui passe à la ligne et dont la hauteur s'adapte."""
    label = Label(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold,
        markup=markup,
        halign="center",
        valign="middle",
        size_hint_y=None,
    )
    label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
    label.bind(texture_size=lambda inst, size: setattr(inst, "height", size[1] + dp(6)))
    return label


def build_slide(headline, text):
    """Construit une page du carrousel : logo, nom, titre et texte."""
    box = BoxLayout(
        orientation="vertical",
        padding=[dp(24), dp(48), dp(24), dp(0)],
        spacing=dp(6),
    )
    box.add_widget(LogoWidget())
    box.add_widget(
        make_label(
            f"[b]Find[color={theme.ACCENT}]Back[/color][/b]",
            font_size=sp(40),
            color=theme.rgba(theme.WHITE),
            markup=True,
        )
    )
    box.add_widget(
        make_label(headline, font_size=sp(17), color=theme.rgba(theme.WHITE))
    )
    box.add_widget(
        make_label(text, font_size=sp(14), color=theme.rgba(theme.LAVENDER))
    )
    return box


class SplashScreen(Screen):
    """Écran d'accueil : trois pages de présentation, puis la connexion."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        root.add_widget(SplashBackground())

        # Le carrousel occupe le haut de l'écran
        self.carousel = Carousel(
            direction="right",
            loop=False,
            size_hint=(1, 0.72),
            pos_hint={"x": 0, "top": 1},
        )
        for slide in SLIDES:
            self.carousel.add_widget(build_slide(slide["headline"], slide["text"]))
        self.carousel.bind(index=self._on_page_changed)
        root.add_widget(self.carousel)

        # Bouton "Passer" en haut à droite
        skip_button = Button(
            text="Passer",
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=theme.rgba(theme.WHITE),
            font_size=sp(15),
            size_hint=(None, None),
            size=(dp(90), dp(40)),
            pos_hint={"right": 0.97, "top": 0.98},
        )
        skip_button.bind(on_release=self.go_to_auth)
        root.add_widget(skip_button)

        # Bouton principal : "Suivant", puis "Commencer" sur la dernière page
        self.action_button = RoundedButton(
            text="Suivant",
            size_hint=(None, None),
            size=(dp(220), dp(50)),
            pos_hint={"center_x": 0.5, "y": 0.15},
        )
        self.action_button.bind(on_release=self.on_action)
        root.add_widget(self.action_button)

        # Les points de pagination
        self.dots = PageDots(
            count=len(SLIDES),
            size_hint=(1, None),
            height=dp(20),
            pos_hint={"x": 0, "y": 0.07},
        )
        root.add_widget(self.dots)

        self.add_widget(root)

    def _on_page_changed(self, carousel, index):
        self.dots.index = index
        is_last = index == len(SLIDES) - 1
        self.action_button.text = "Commencer" if is_last else "Suivant"

    def on_action(self, *args):
        if self.carousel.index < len(SLIDES) - 1:
            self.carousel.load_next()
        else:
            self.go_to_auth()

    def go_to_auth(self, *args):
        self.manager.transition.direction = "left"
        self.manager.current = "auth"