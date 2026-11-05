from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.label import Label

import theme

_current_toast = None


class ToastLabel(Label):
    def __init__(self, text, **kwargs):
        width = min(Window.width - dp(32), dp(330))
        super().__init__(
            text=text,
            color=theme.rgba(theme.WHITE),
            font_size=sp(14),
            halign="center",
            valign="middle",
            size_hint=(None, None),
            width=width,
            text_size=(width - dp(24), None),
            **kwargs
        )
        with self.canvas.before:
            Color(*theme.rgba(theme.TEXT_DARK, 0.94))
            self._shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )
        self.bind(
            pos=self._update_shape, size=self._update_shape, texture_size=self._resize
        )
        self.texture_update()
        self._resize()

    def _resize(self, *args):
        self.height = self.texture_size[1] + dp(24)
        self.pos = ((Window.width - self.width) / 2, dp(36))

    def _update_shape(self, *args):
        self._shape.pos = self.pos
        self._shape.size = self.size


def _remove_toast(toast):
    global _current_toast
    if toast in Window.children:
        Window.remove_widget(toast)
    if _current_toast is toast:
        _current_toast = None


def show_toast(text, duration=2.2):
    """Affiche un message temporaire en bas de la fenêtre."""
    global _current_toast
    if _current_toast is not None:
        _remove_toast(_current_toast)
    toast = ToastLabel(text)
    Window.add_widget(toast)
    _current_toast = toast
    Clock.schedule_once(lambda dt: _remove_toast(toast), duration)