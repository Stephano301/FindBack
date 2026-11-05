import math

from kivy.graphics import Color, Line, Quad
from kivy.metrics import dp
from kivy.properties import OptionProperty
from kivy.uix.widget import Widget

import theme


class LogoWidget(Widget):
    """Logo FindBack dessiné avec le canvas : loupe, colis et étincelles.

    variant="light" : pour un fond violet (logo blanc)
    variant="dark"  : pour un fond clair (logo violet)
    """

    variant = OptionProperty("light", options=["light", "dark"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, variant=self._draw)
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        cx, cy = self.center
        side = min(self.width, self.height)
        radius = side * 0.34
        line_width = max(dp(4), side * 0.045)

        if self.variant == "light":
            ring_color = theme.WHITE
            face_top, face_left, face_right = (
                theme.LAVENDER,
                theme.LAVENDER_DARK,
                theme.PRIMARY_LIGHT,
            )
        else:
            ring_color = theme.PRIMARY
            face_top, face_left, face_right = (
                theme.PRIMARY_LIGHT,
                theme.PRIMARY,
                theme.PRIMARY_DARK,
            )

        with self.canvas:
            # Anneau de la loupe
            Color(*theme.rgba(ring_color))
            Line(circle=(cx, cy, radius), width=line_width)

            # Manche de la loupe (en bas à gauche)
            angle = math.radians(225)
            Line(
                points=[
                    cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle),
                    cx + radius * 1.6 * math.cos(angle),
                    cy + radius * 1.6 * math.sin(angle),
                ],
                width=line_width * 1.4,
                cap="round",
            )

            # Étincelles orange (en haut à droite)
            Color(*theme.rgba(theme.ACCENT))
            for degrees in (35, 60, 85):
                a = math.radians(degrees)
                Line(
                    points=[
                        cx + radius * 1.22 * math.cos(a),
                        cy + radius * 1.22 * math.sin(a),
                        cx + radius * 1.48 * math.cos(a),
                        cy + radius * 1.48 * math.sin(a),
                    ],
                    width=dp(3),
                    cap="round",
                )

            # Colis au centre : trois faces d'un cube
            s = radius * 0.55
            dx = s * 0.87
            dy = s * 0.5
            Color(*theme.rgba(face_top))
            Quad(points=[cx, cy + s, cx + dx, cy + dy, cx, cy, cx - dx, cy + dy])
            Color(*theme.rgba(face_left))
            Quad(points=[cx - dx, cy + dy, cx, cy, cx, cy - s, cx - dx, cy - dy])
            Color(*theme.rgba(face_right))
            Quad(points=[cx, cy, cx + dx, cy + dy, cx + dx, cy - dy, cx, cy - s])
