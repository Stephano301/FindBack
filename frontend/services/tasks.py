import threading
import traceback

from kivy.app import App
from kivy.clock import Clock

from services.api_client import ApiError
from widgets.toast import show_toast


def error_text(error):
    """Message à afficher pour une erreur."""
    if isinstance(error, ApiError):
        return error.message
    return "Une erreur inattendue est survenue."


def handle_error(error):
    """Gestion par défaut des erreurs : message en bas, et retour à la connexion si la session a expiré."""
    if isinstance(error, ApiError) and error.status_code == 401:
        root = App.get_running_app().root
        root.transition.direction = "right"
        root.current = "auth"
    show_toast(error_text(error))


def run_async(task, on_success=None, on_error=None, busy_widget=None):
    """Exécute task() en arrière-plan, puis appelle on_success(résultat) ou on_error(erreur).

    busy_widget : un bouton qu'on désactive pendant l'appel.
    """
    if busy_widget is not None:
        busy_widget.disabled = True

    def finish(result, error):
        # Cette fonction s'exécute dans le fil principal de Kivy
        if busy_widget is not None:
            busy_widget.disabled = False
        if error is not None:
            (on_error or handle_error)(error)
        elif on_success:
            on_success(result)

    def worker():
        try:
            result = task()
        except Exception as error:
            if not isinstance(error, ApiError):
                traceback.print_exc()
            Clock.schedule_once(lambda dt, e=error: finish(None, e), 0)
        else:
            Clock.schedule_once(lambda dt, r=result: finish(r, None), 0)

    threading.Thread(target=worker, daemon=True).start()