import os

from kivy.config import Config

import theme

# La taille de la fenêtre doit être réglée AVANT d'importer le reste de Kivy
Config.set("graphics", "width", str(theme.WINDOW_WIDTH))
Config.set("graphics", "height", str(theme.WINDOW_HEIGHT))
# Évite les points rouges qui apparaissent avec le clic droit de la souris
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, SlideTransition  # noqa: E402

from screens.admin_screen import AdminScreen  # noqa: E402
from screens.auth_screen import AuthScreen  # noqa: E402
from screens.claims_screen import ClaimsScreen  # noqa: E402
from screens.declare_screen import DeclareScreen  # noqa: E402
from screens.edit_profile_screen import EditProfileScreen  # noqa: E402
from screens.home_screen import HomeScreen  # noqa: E402
from screens.item_detail_screen import ItemDetailScreen  # noqa: E402
from screens.item_list_screens import ItemsScreen, MyItemsScreen  # noqa: E402
from screens.profile_screen import ProfileScreen  # noqa: E402
from screens.splash_screen import SplashScreen  # noqa: E402


class FindBackApp(App):
    title = "FindBack"

    def build(self):
        Window.clearcolor = theme.rgba(theme.BACKGROUND)

        manager = ScreenManager(transition=SlideTransition(duration=0.25))
        manager.add_widget(SplashScreen(name="splash"))
        manager.add_widget(AuthScreen(name="auth"))
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(DeclareScreen(name="declare"))
        manager.add_widget(ItemDetailScreen(name="item_detail"))
        manager.add_widget(ItemsScreen(name="items"))
        manager.add_widget(MyItemsScreen(name="my_items"))
        manager.add_widget(ClaimsScreen(name="claims"))
        manager.add_widget(ProfileScreen(name="profile"))
        manager.add_widget(EditProfileScreen(name="edit_profile"))
        manager.add_widget(AdminScreen(name="admin"))

        # Raccourci de développement : FINDBACK_START=home démarre sur l'accueil
        start = os.environ.get("FINDBACK_START", "splash")
        manager.current = start if manager.has_screen(start) else "splash"
        return manager


if __name__ == "__main__":
    FindBackApp().run()